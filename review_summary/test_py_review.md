# Security Review: `test.py`

**Reviewer:** Bob (IBM watsonx.ai Actor-Critic Review)
**Model:** `ibm/granite-4-h-small` via watsonx.ai
**Date:** 2025-07-14
**Mode:** MODE A — Local Code Review (Actor-Critic Validation)
**Target:** [`test.py`](../test.py)
**Methodology:** OWASP Top 10 · CWE · Two-round Actor-Critic validation

---

## Executive Summary

`test.py` is a 36-line Python demonstration script that intentionally introduces
SQL injection as a teaching aid. The file is **not production-safe**. The
Actor-Critic review identified **4 confirmed True Positive findings** and
dismissed 1 False Positive raised by the Actor.

The single highest-risk issue is an exploitable SQL injection vulnerability
with a working proof-of-concept already present in the `__main__` block.
Three supporting issues (information leakage through error messages, error
type loss, and test/production code mixing) were also confirmed.

**Production Readiness: ❌ Not production-ready.**

---

## Actor-Critic Process

| Round | Role | Action |
|-------|------|--------|
| 1 | 🕵️ **Actor** | Exhaustive OWASP scan — all injection categories, data-flow, correctness |
| 2 | 🔬 **Critic** | Independent peer challenge — TP/FP verdict + severity calibration on every finding |

---

## Finding Summary

| ID | Severity | Confidence | Critic Verdict | Vulnerability | OWASP | Line(s) |
|----|----------|------------|----------------|---------------|-------|---------|
| F-01 | 🔴 HIGH | Confirmed | ✅ TRUE POSITIVE | SQL Injection | A03:2021 – Injection | 17, 20 |
| F-02 | 🟠 MEDIUM | Confirmed | ✅ TRUE POSITIVE | Information Exposure via Error Messages | A09:2021 – Logging Failures | 23–24 |
| F-03 | 🟡 LOW | Confirmed | ✅ TRUE POSITIVE | Exception Type Silenced / Lost | A09:2021 – Logging Failures | 23–24 |
| F-04 | 🟠 MEDIUM | Confirmed | ✅ TRUE POSITIVE | Test / Demo Code in Production File | A06:2021 – Outdated Components | 28–36 |
| F-05 | — | Estimated | ❌ FALSE POSITIVE | Insecure DB Connection (in-memory SQLite) | A02:2021 | N/A |

---

## Detailed Findings

---

### 🔴 F-01 — SQL Injection (Unsanitized String Concatenation)

**OWASP:** A03:2021 – Injection
**CWE:** CWE-89
**Severity:** HIGH
**Confidence:** Confirmed
**Lines:** 17, 20
**Critic Verdict:** ✅ TRUE POSITIVE — Severity kept at HIGH

**Vulnerable code:**
```python
query = "SELECT * FROM users WHERE id = '" + user_id + "'"
cursor.execute(query)
```

**Data-flow path:**
```
user_id (caller-controlled)
    ↓  no validation, no parameterization
string concatenation → SQL query string
    ↓
cursor.execute(query)   ← sink: SQL execution engine
```

**Proof-of-Concept (demonstrated on line 35):**
```python
malicious_payload = "1' OR '1'='1"
fetch_user_data(malicious_payload)
# Resulting query: SELECT * FROM users WHERE id = '1' OR '1'='1'
# Returns ALL rows — authentication/filter bypass confirmed
```

In a production database (non-in-memory) consequences extend to:
- Full table dump via `UNION`-based injection
- Blind data exfiltration via timing or error channels
- Data modification or deletion (`INSERT`, `UPDATE`, `DELETE`)
- In SQLite: out-of-band file write via `ATTACH DATABASE`

**Remediation — use a parameterized query:**
```python
# Before (vulnerable)
query = "SELECT * FROM users WHERE id = '" + user_id + "'"
cursor.execute(query)

# After (safe)
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

---

### 🟠 F-02 — Information Exposure Through Error Messages

**OWASP:** A09:2021 – Security Logging and Monitoring Failures
**CWE:** CWE-209
**Severity:** MEDIUM
**Confidence:** Confirmed
**Lines:** 23–24
**Critic Verdict:** ✅ TRUE POSITIVE — Severity kept at MEDIUM

**Vulnerable code:**
```python
except sqlite3.Error as e:
    return str(e)
```

Raw database error messages are returned to the caller. In a real application
these strings are often propagated into API responses or rendered in the UI,
leaking schema names, table names, column names, SQL syntax, and driver
version details — information an attacker uses to craft more precise injection
payloads.

**Remediation:**
```python
import logging
logger = logging.getLogger(__name__)

except sqlite3.Error as e:
    logger.error("Database error in fetch_user_data: %s", e)
    return []   # or raise a typed application exception
```

---

### 🟡 F-03 — Exception Type Silenced / Error Type Lost

**OWASP:** A09:2021 – Security Logging and Monitoring Failures
**CWE:** CWE-209
**Severity:** LOW
**Confidence:** Confirmed
**Lines:** 23–24
**Critic Verdict:** ✅ TRUE POSITIVE — Severity kept at LOW

`return str(e)` discards the exception type and traceback, making it
impossible for callers to distinguish a database error from a valid empty
result set without fragile string parsing. This masks operational failures
and creates type-inconsistency bugs (`list` vs `str` return type).

**Remediation:** Re-raise or return a typed error object:
```python
except sqlite3.Error as e:
    logger.error("fetch_user_data failed: %s", e)
    raise RuntimeError("Database query failed") from e
```

---

### 🟠 F-04 — Test / Demo Code Mixed Into Production Module

**OWASP:** A06:2021 – Vulnerable and Outdated Components (code hygiene)
**CWE:** CWE-577
**Severity:** MEDIUM
**Confidence:** Confirmed
**Lines:** 28–36
**Critic Verdict:** ✅ TRUE POSITIVE — Severity kept at MEDIUM

**Code:**
```python
if __name__ == "__main__":
    malicious_payload = "1' OR '1'='1"
    print(fetch_user_data(malicious_payload))
```

The `__main__` block includes a live SQL injection exploit demonstration.
If this module were imported and executed in an interactive environment, CI
runner, or another script, the exploit test would execute against whatever
database is connected. It also hardcodes email addresses and user data that
constitute a minor PII risk in production code.

**Remediation:** Move test cases to a dedicated test module:
```python
# tests/test_fetch_user_data.py
import pytest
from test import fetch_user_data

def test_standard_query():
    assert fetch_user_data("1") == [("1", "Admin User", "admin@example.com")]

def test_sql_injection_blocked():
    result = fetch_user_data("1' OR '1'='1")
    assert len(result) == 1  # must NOT return all rows after fix
```

---

### ~~F-05 — Insecure DB Connection~~ (FALSE POSITIVE — dismissed by Critic)

**Critic verdict:** ❌ FALSE POSITIVE

The Actor raised a concern about unencrypted database connections. The Critic
correctly dismissed this: `sqlite3.connect(':memory:')` creates a purely
in-memory database with no network socket. There is no data-in-transit path,
no TCP connection, and no possibility of a man-in-the-middle attack on this
specific code. No action required for this finding.

---

## Attack-Path Reasoning (F-01)

```
Attacker controls user_id argument
        ↓
No input validation at function boundary
        ↓
user_id concatenated into SQL string (line 17)
        ↓
cursor.execute() passes raw string to SQLite engine (line 20)
        ↓
Engine interprets injected SQL as valid syntax
        ↓
Authentication / filter bypass → all rows returned
        ↓
In production: full table dump, data modification, or file write
```

---

## Production Readiness Assessment

| Dimension | Status | Notes |
|-----------|--------|-------|
| Security | ❌ Fail | Exploitable SQL injection confirmed |
| Error Handling | ❌ Fail | Raw errors returned; exception type lost |
| Code Organisation | ⚠️ Warn | Test/exploit code mixed into module body |
| Correctness | ✅ Pass | `import sqlite3` is present (fixed vs earlier version) |
| Logging | ❌ Fail | No logging; errors silently returned as strings |
| Testing | ❌ Fail | No unit tests; `__main__` block is not a test suite |

---

## Remediation Priority

1. **Immediate (before any deployment):** Replace string-concatenated SQL with a parameterized query (`cursor.execute("… WHERE id = ?", (user_id,))`).
2. **Immediate:** Replace `return str(e)` with proper logging and a safe return value or re-raise.
3. **Before production:** Move `__main__` block to a proper test module.
4. **Low priority:** Add structured logging so database errors are observable.

---

## SARIF v2.1.0

```json
{
  "version": "2.1.0",
  "runs": [{
    "tool": {
      "driver": {
        "name": "watsonx-critic",
        "informationUri": "https://us-south.ml.cloud.ibm.com",
        "rules": [
          { "id": "F-01", "name": "SQLInjection",           "shortDescription": { "text": "SQL Injection via string concatenation (CWE-89)" } },
          { "id": "F-02", "name": "ErrorInfoLeak",          "shortDescription": { "text": "Information exposure through error messages (CWE-209)" } },
          { "id": "F-03", "name": "ExceptionTypeLost",      "shortDescription": { "text": "Exception type silenced by str() conversion (CWE-209)" } },
          { "id": "F-04", "name": "TestCodeInProduction",   "shortDescription": { "text": "Test/demo exploit code mixed into production module (CWE-577)" } }
        ]
      }
    },
    "results": [
      {
        "ruleId": "F-01", "level": "error",
        "message": { "text": "SQL Injection: user_id concatenated into SQL string without parameterization (OWASP A03:2021, CWE-89)" },
        "locations": [{ "physicalLocation": { "artifactLocation": { "uri": "test.py" }, "region": { "startLine": 17, "endLine": 20 } } }]
      },
      {
        "ruleId": "F-02", "level": "warning",
        "message": { "text": "Raw sqlite3.Error message returned to caller — leaks schema/query details (OWASP A09:2021, CWE-209)" },
        "locations": [{ "physicalLocation": { "artifactLocation": { "uri": "test.py" }, "region": { "startLine": 23, "endLine": 24 } } }]
      },
      {
        "ruleId": "F-03", "level": "note",
        "message": { "text": "Exception converted to string loses type; caller cannot distinguish error from empty result (CWE-209)" },
        "locations": [{ "physicalLocation": { "artifactLocation": { "uri": "test.py" }, "region": { "startLine": 23, "endLine": 24 } } }]
      },
      {
        "ruleId": "F-04", "level": "warning",
        "message": { "text": "Live SQL injection exploit in __main__ block; test code mixed into production module (CWE-577)" },
        "locations": [{ "physicalLocation": { "artifactLocation": { "uri": "test.py" }, "region": { "startLine": 28, "endLine": 36 } } }]
      }
    ]
  }]
}
```

---

*Review generated by IBM Bob using the Actor-Critic skill with ibm/granite-4-h-small via IBM watsonx.ai.*
