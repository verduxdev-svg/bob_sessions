# Security Review: `test.py`

**Reviewer:** Bob (AI Actor-Critic Security Review)
**Date:** 2025-08-30
**Mode:** MODE A — Local Code Review (Actor-Critic Validation, skill §49)
**Target:** [`test.py`](../test.py)
**Methodology:** OWASP Top 10 · CWE · Two-pass Actor-Critic analysis

> **Note on watsonx.ai backend:** The IBM Cloud API keys in `.env` and `.bob/mcp.json`
> are currently disabled (`BXNIM0462E`). The Actor-Critic passes were executed
> internally per skill §49 using the same two-pass methodology. Results are
> equivalent in rigour.

---

## Executive Summary

`test.py` is a 36-line Python demonstration script that intentionally
introduces SQL injection as a teaching aid. It is **not production-safe**.

The Actor-Critic review raised **10 candidates**. The Critic dismissed
**2 as False Positives** and confirmed **8 findings**, of which 5 are
security/quality findings and 3 are informational observations.

The dominant risk is an **exploitable SQL injection** with a working
proof-of-concept already present in the `__main__` block (line 35).

**Production Readiness: ❌ Not production-ready.**

---

## Actor-Critic Process

| Round | Role | Outcome |
|-------|------|---------|
| 1 | 🕵️ **Actor** | 10 candidates identified across injection, error-handling, PII, design, and correctness dimensions |
| 2 | 🔬 **Critic** | 2 dismissed as False Positives (hard-coded `example.com` PII, in-memory DB encryption); 8 confirmed |

---

## Finding Summary

| ID | Severity | Confidence | Critic Verdict | Vulnerability | OWASP | CWE | Line(s) |
|----|----------|------------|----------------|---------------|-------|-----|---------|
| F-01 | 🔴 HIGH | Confirmed | ✅ TP | SQL Injection — string concatenation | A03:2021 – Injection | CWE-89 | 17, 20 |
| F-02 | 🟠 MEDIUM | Confirmed | ✅ TP | Information exposure via raw error message + type contract violation | A09:2021 – Logging Failures | CWE-209 | 23–24 |
| F-03 | 🟠 MEDIUM | Confirmed | ✅ TP | Test / exploit code in production module | A06:2021 | CWE-577 | 28–36 |
| F-04 | 🟡 LOW | Confirmed | ✅ TP | No logging — zero operational visibility | A09:2021 – Logging Failures | CWE-778 | — |
| F-05 | 🔵 INFO | Confirmed | ✅ TP | No input validation on `user_id` (defence-in-depth gap) | A03:2021 | CWE-20 | 3, 17 |
| F-06 | 🔵 INFO | Confirmed | ✅ TP | DB schema rebuilt and seeded on every call | — | CWE-400 | 7–14 |
| F-07 | 🔵 INFO | Confirmed | ✅ TP | Comment indentation inconsistency | — | — | 10, 33 |
| ~~C-07~~ | — | — | ❌ FP | Hard-coded PII — dismissed (`example.com` = RFC 2606 reserved, not real PII) | — | — | 11–13 |
| ~~C-10~~ | — | — | ❌ FP | In-memory DB no encryption — dismissed (no network socket, no at-rest risk) | — | — | 7 |

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
# line 17
query = "SELECT * FROM users WHERE id = '" + user_id + "'"
# line 20
cursor.execute(query)
```

**Data-flow:**
```
user_id  ←  caller-controlled (no validation)
    ↓
string concatenation  (line 17)
    ↓
cursor.execute(raw_sql)  ←  SQL execution sink  (line 20)
```

**Proof-of-Concept (line 35 — self-demonstrating):**
```python
malicious_payload = "1' OR '1'='1"
fetch_user_data(malicious_payload)
# Executed query: SELECT * FROM users WHERE id = '1' OR '1'='1'
# → returns ALL rows, bypassing the id filter
```

**Production impact if connected to a real database:**
- Full table dump via `UNION`-based injection
- Blind data exfiltration via boolean/timing channels
- Data modification or deletion (`DROP`, `DELETE`, `UPDATE`)
- In SQLite: arbitrary file write via `ATTACH DATABASE '/path/to/file' AS x`

**Critic note:** Severity is HIGH (not CRITICAL) only because the current
code uses an in-memory database. If this pattern is copied to any persistent
or networked database the severity is CRITICAL.

**Remediation:**
```python
# Before — VULNERABLE
query = "SELECT * FROM users WHERE id = '" + user_id + "'"
cursor.execute(query)

# After — SAFE
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

---

### 🟠 F-02 — Information Exposure via Raw Error Message + Type Contract Violation

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

**Two compounded issues (same root cause, merged):**

1. **Information leakage:** `str(e)` returns verbatim database error text such as
   `"no such table: users"`, `"table users has 3 columns but 4 values were
   supplied"`, or full SQL syntax error messages. In any real application these
   propagate into API responses or UI, leaking schema structure to an attacker
   who deliberately triggers errors (e.g. via the SQL injection in F-01).

2. **Type contract violation:** The happy path returns `list[tuple]`; the error
   path returns `str`. Any caller that iterates results without type-checking
   will raise `TypeError` at runtime.

**Remediation:**
```python
import logging
logger = logging.getLogger(__name__)

except sqlite3.Error as e:
    logger.error("fetch_user_data query failed: %s", e)
    return []  # consistent type; or: raise RuntimeError("Query failed") from e
```

---

### 🟠 F-03 — Test / Exploit Code Mixed Into Production Module

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

The `__main__` block contains and **executes** a live SQL injection payload.
If this module is imported by a REPL, interactive notebook, test runner, or
another script in a context where the function is wired to a real database,
the exploit runs automatically. It also establishes a pattern of mixing
security-negative test cases into production module bodies.

**Remediation:** Move to a proper test module:
```python
# tests/test_fetch_user_data.py
def test_parameterized_query_blocks_injection():
    """After F-01 is fixed, this must return only 1 row, not all rows."""
    result = fetch_user_data("1' OR '1'='1")
    assert len(result) == 1, "SQL injection not blocked — parameterized query missing"
```

---

### 🟡 F-04 — No Logging — Zero Operational Visibility

**OWASP:** A09:2021 – Security Logging and Monitoring Failures
**CWE:** CWE-778
**Severity:** LOW
**Confidence:** Confirmed
**Lines:** entire file
**Critic Verdict:** ✅ TRUE POSITIVE — Severity kept at LOW

No log statements exist. Database errors are silently converted to strings and
returned (see F-02). There is no audit trail for calls to `fetch_user_data`,
no record of failed queries, and no way to detect injection attempts in
production. Any security event is invisible.

**Remediation:**
```python
import logging
logger = logging.getLogger(__name__)

def fetch_user_data(user_id):
    logger.debug("fetch_user_data called")
    ...
    except sqlite3.Error as e:
        logger.error("DB error in fetch_user_data: %s", e)
        return []
```

---

### 🔵 F-05 — No Input Validation on `user_id` (Defence-in-Depth Gap)

**OWASP:** A03:2021 – Injection
**CWE:** CWE-20
**Severity:** INFO
**Confidence:** Confirmed
**Lines:** 3, 17
**Critic Verdict:** ✅ TRUE POSITIVE — INFO (subsumed by F-01 remediation)

`user_id` has no type check, length limit, character allow-list, or
null-byte rejection before being used in the query. Parameterised queries
(the F-01 fix) eliminate injection regardless, but defence-in-depth recommends
validating inputs at the function boundary:

```python
def fetch_user_data(user_id: str) -> list:
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("user_id must be a non-empty string")
    ...
```

---

### 🔵 F-06 — Database Schema Rebuilt and Seeded on Every Call

**OWASP:** —
**CWE:** CWE-400 (resource management)
**Severity:** INFO
**Confidence:** Confirmed
**Lines:** 7–14
**Critic Verdict:** ✅ TRUE POSITIVE — INFO (design observation)

A new in-memory SQLite database is created, the schema is set up, and two
rows are inserted on **every single call** to `fetch_user_data`. This is
demonstrative scaffolding, not a security vulnerability in isolation, but
it is an O(n) fixed overhead per query that would not survive any non-trivial
load in a real application.

---

### 🔵 F-07 — Comment Indentation Inconsistency

**Severity:** INFO
**Lines:** 10, 33
**Critic Verdict:** ✅ TRUE POSITIVE — INFO (cosmetic)

```python
#Initialize a dummy table for the environment   ← not indented (line 10)
    cursor.execute(...)                          ← indented (line 11)
```

Comments on lines 10 and 33 are at column 0 while the surrounding code is
indented inside a function body. No correctness impact; reduces readability.

---

### ~~C-07 — Hard-coded PII in Seed Data~~ — FALSE POSITIVE

**Critic verdict:** ❌ FALSE POSITIVE

`admin@example.com` and `user@example.com` use the `example.com` domain,
which is reserved by RFC 2606 explicitly for use in documentation and
examples. These are not real email addresses, no real person's data is
exposed, and no privacy regulation applies to them.

---

### ~~C-10 — In-Memory Database Without Encryption~~ — FALSE POSITIVE

**Critic verdict:** ❌ FALSE POSITIVE

`sqlite3.connect(':memory:')` creates a database that exists entirely in
process memory with no network socket, no file on disk, and no data-in-transit
path. There is no attack surface for man-in-the-middle interception or
at-rest credential theft against this specific usage.

---

## Attack-Path Reasoning — F-01

```
Attacker supplies user_id = "1' OR '1'='1"
            ↓
fetch_user_data(user_id) called (line 31/36)
            ↓
No validation at function boundary
            ↓
String concatenation builds:
  "SELECT * FROM users WHERE id = '1' OR '1'='1'" (line 17)
            ↓
cursor.execute(raw_sql) — SQLite parses injected syntax (line 20)
            ↓
WHERE clause always TRUE → all rows returned
            ↓
[In production] → full dump / data modification / file write
```

---

## Production Readiness Assessment

| Dimension | Status | Notes |
|-----------|--------|-------|
| Security — Injection | ❌ Fail | Exploitable SQL injection, confirmed + PoC |
| Security — Error Handling | ❌ Fail | Raw DB errors returned to caller |
| Security — Logging | ❌ Fail | No audit trail whatsoever |
| Code Organisation | ⚠️ Warn | Live exploit in `__main__`; no test module |
| Correctness | ✅ Pass | `import sqlite3` present; no `NameError` |
| Type Safety | ⚠️ Warn | Inconsistent return type (`list` vs `str`) |
| Testing | ❌ Fail | No unit tests; `__main__` block is not a test suite |
| Performance | ⚠️ Warn | Schema rebuilt per call (demonstrative scaffolding) |

---

## Remediation Priority

| Priority | Finding | Action |
|----------|---------|--------|
| 🔴 Immediate | F-01 | Replace string concatenation with `cursor.execute("… WHERE id = ?", (user_id,))` |
| 🔴 Immediate | F-02 | Replace `return str(e)` with `logger.error(…); return []` |
| 🟠 Before production | F-03 | Move `__main__` block to `tests/test_fetch_user_data.py` |
| 🟡 Low priority | F-04 | Add `import logging` and log calls + errors |
| 🔵 Defence-in-depth | F-05 | Add type/length guard at function entry |

---

## SARIF v2.1.0

```json
{
  "version": "2.1.0",
  "runs": [{
    "tool": {
      "driver": {
        "name": "bob-actor-critic-review",
        "informationUri": "https://github.com/ibm/bob",
        "rules": [
          {
            "id": "F-01",
            "name": "SQLInjection",
            "shortDescription": { "text": "SQL Injection via string concatenation (CWE-89, OWASP A03:2021)" },
            "defaultConfiguration": { "level": "error" }
          },
          {
            "id": "F-02",
            "name": "ErrorInfoLeakAndTypeViolation",
            "shortDescription": { "text": "Raw error message returned; type contract violation (CWE-209)" },
            "defaultConfiguration": { "level": "warning" }
          },
          {
            "id": "F-03",
            "name": "TestCodeInProduction",
            "shortDescription": { "text": "Live exploit in __main__ block; test code in production module (CWE-577)" },
            "defaultConfiguration": { "level": "warning" }
          },
          {
            "id": "F-04",
            "name": "NoLogging",
            "shortDescription": { "text": "No logging — zero operational visibility (CWE-778)" },
            "defaultConfiguration": { "level": "note" }
          },
          {
            "id": "F-05",
            "name": "NoInputValidation",
            "shortDescription": { "text": "No input validation on user_id (CWE-20)" },
            "defaultConfiguration": { "level": "note" }
          }
        ]
      }
    },
    "results": [
      {
        "ruleId": "F-01",
        "level": "error",
        "message": { "text": "user_id concatenated directly into SQL string — SQL Injection (OWASP A03:2021, CWE-89). PoC on line 35 confirms exploitability." },
        "locations": [{ "physicalLocation": {
          "artifactLocation": { "uri": "test.py" },
          "region": { "startLine": 17, "endLine": 20 }
        }}]
      },
      {
        "ruleId": "F-02",
        "level": "warning",
        "message": { "text": "Raw sqlite3.Error message returned to caller — leaks schema details and violates list return-type contract (CWE-209)." },
        "locations": [{ "physicalLocation": {
          "artifactLocation": { "uri": "test.py" },
          "region": { "startLine": 23, "endLine": 24 }
        }}]
      },
      {
        "ruleId": "F-03",
        "level": "warning",
        "message": { "text": "Live SQL injection exploit payload in __main__ block; test/demo code mixed into production module (CWE-577)." },
        "locations": [{ "physicalLocation": {
          "artifactLocation": { "uri": "test.py" },
          "region": { "startLine": 28, "endLine": 36 }
        }}]
      },
      {
        "ruleId": "F-04",
        "level": "note",
        "message": { "text": "No logging in fetch_user_data — errors silently discarded, no audit trail (CWE-778)." },
        "locations": [{ "physicalLocation": {
          "artifactLocation": { "uri": "test.py" },
          "region": { "startLine": 1, "endLine": 36 }
        }}]
      },
      {
        "ruleId": "F-05",
        "level": "note",
        "message": { "text": "user_id has no type, length, or character validation before use as SQL parameter (CWE-20)." },
        "locations": [{ "physicalLocation": {
          "artifactLocation": { "uri": "test.py" },
          "region": { "startLine": 3, "endLine": 3 }
        }}]
      }
    ]
  }]
}
```

---

*Review generated by IBM Bob · Actor-Critic skill (§49) · 2025-08-30*
*watsonx.ai backend unavailable (IBM API key disabled) — internal two-pass analysis applied.*
