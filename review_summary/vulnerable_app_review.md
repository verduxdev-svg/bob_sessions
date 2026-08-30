# Security Review: `vulnerable_app.py`

**Reviewer:** Bob (AI Actor-Critic Security Review)
**Date:** 2025-08-30
**Mode:** MODE A — Local Code Review (Actor-Critic Validation, skill §49)
**Target:** [`vulnerable_app.py`](../vulnerable_app.py)
**Methodology:** OWASP Top 10 · CWE · Two-pass Actor-Critic analysis

---

## Executive Summary

`vulnerable_app.py` is a 14-line Python module containing a single public
function `get_user_data`. It presents **two self-annotated critical flaws**
and **five additional confirmed vulnerabilities** discovered in the
Actor-Critic review.

The Actor raised **10 candidates**. The Critic confirmed **9 as True Positives**
(2 merged into parent findings), dismissed **0 as False Positives**, and
elevated one finding from HIGH to **CRITICAL** based on the use of a
persistent on-disk database rather than an in-memory one.

**This file must not be deployed in any production context.**

**Production Readiness: ❌ Not production-ready.**

---

## Actor-Critic Process

| Round | Role | Outcome |
|-------|------|---------|
| 1 | 🕵️ **Actor** | 10 candidates across injection, credential exposure, resource management, data exposure, error handling, and correctness |
| 2 | 🔬 **Critic** | 0 False Positives · 7 independent TPs · 2 merged into parent findings · C-01 severity raised to CRITICAL |

---

## Finding Summary

| ID | Severity | Confidence | Critic Verdict | Vulnerability | OWASP | CWE | Line(s) |
|----|----------|------------|----------------|---------------|-------|-----|---------|
| F-01 | 🔴 CRITICAL | Confirmed | ✅ TP — raised to CRITICAL | SQL Injection — persistent DB, unquoted | A03:2021 – Injection | CWE-89 | 11–12 |
| F-02 | 🔴 HIGH | Confirmed | ✅ TP | Hard-coded API credential in source | A02:2021 – Crypto Failures | CWE-798 | 6 |
| F-03 | 🟠 MEDIUM | Confirmed | ✅ TP | Database connection never closed — resource leak | A05:2021 – Misconfig | CWE-772 | 9–14 |
| F-04 | 🟠 MEDIUM | Confirmed | ✅ TP | Unbounded `fetchall()` — data over-exposure + DoS | A03:2021 – Injection | CWE-400 | 13 |
| F-05 | 🟠 MEDIUM | Confirmed | ✅ TP | No error handling — unhandled exceptions leak internals | A09:2021 – Logging Failures | CWE-209 | 4–14 |
| F-06 | 🟡 LOW | Confirmed | ✅ TP | Hardcoded relative DB path — misconfiguration risk | A05:2021 – Misconfig | CWE-426 | 9 |
| F-07 | 🔵 INFO | Confirmed | ✅ TP | No input validation on `user_id` — defence-in-depth gap | A03:2021 | CWE-20 | 4, 11 |
| F-08 | 🔵 INFO | Confirmed | ✅ TP | Dead `import os` — unused import | — | — | 1 |

---

## Detailed Findings

---

### 🔴 F-01 — SQL Injection (Persistent Database, Unquoted Concatenation)

**OWASP:** A03:2021 – Injection
**CWE:** CWE-89
**Severity:** CRITICAL *(Critic raised from HIGH — persistent on-disk DB)*
**Confidence:** Confirmed
**Lines:** 11–12

**Vulnerable code:**
```python
query = "SELECT * FROM users WHERE id = " + user_id   # line 11
cursor.execute(query)                                   # line 12
```

**Data-flow:**
```
user_id  ←  caller-controlled function argument
    ↓  no validation, no type guard
string concatenation — numeric context, no quoting  (line 11)
    ↓
cursor.execute(raw SQL)  ←  sink: SQLite on database.db  (line 12)
    ↓
cursor.fetchall()  →  returned to caller, no row limit
```

**Proof-of-Concept attacks:**

*Authentication / filter bypass:*
```python
get_user_data("1 OR 1=1")
# Query: SELECT * FROM users WHERE id = 1 OR 1=1
# → returns every row in the users table
```

*Stacked query — data destruction:*
```python
get_user_data("1; DROP TABLE users--")
# → destroys the users table (SQLite supports this via executescript)
```

*Out-of-band file write via ATTACH:*
```python
get_user_data("1 UNION SELECT 1,2,sql FROM sqlite_master--")
# → exfiltrates the entire DB schema
```

**Why CRITICAL (not HIGH):**
Unlike the in-memory case in `test.py`, `database.db` is a **persistent
on-disk file**. SQL injection here can:
- Permanently destroy or modify production data
- Exfiltrate the entire database to the attacker
- Write arbitrary files on the filesystem via `ATTACH DATABASE`
- Corrupt the application for all users, not just the current request

**Remediation — parameterized query:**
```python
# Before — VULNERABLE
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)

# After — SAFE
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

The `?` placeholder instructs the SQLite driver to bind `user_id` as a
data value, never as executable SQL syntax.

---

### 🔴 F-02 — Hard-coded API Credential in Source

**OWASP:** A02:2021 – Cryptographic Failures
**CWE:** CWE-798
**Severity:** HIGH
**Confidence:** Confirmed
**Lines:** 6

**Vulnerable code:**
```python
API_KEY = "sk-12345ABCDE"
```

**Issues (two compounded problems, same root cause):**

1. **Hard-coded credential:** The `sk-` prefix is the conventional format for
   OpenAI, Anthropic, Stripe, and many other service API keys. A key with this
   format committed to source will be flagged by automated secret scanners
   (GitHub secret scanning, truffleHog, gitleaks) and is trivially extracted
   from any repository clone, build log, or code review.

2. **Dead variable — never used:** `API_KEY` is assigned but never read,
   passed, or returned anywhere in the function. It exists only in local scope
   and is garbage-collected on return. There is no runtime security impact
   from the unused variable, but the credential is still present in source
   and will be committed to version control.

**Attack path:**
```
Developer commits file
    ↓
git history retains value permanently
    ↓
Anyone with repo read access (including leaked forks, CI logs) extracts key
    ↓
Key used to authenticate against the target API service
    ↓
Unauthorized API access / billing fraud / data theft
```

**Remediation:**
```python
import os

def get_user_data(user_id):
    api_key = os.environ["API_KEY"]   # loaded from environment / secrets manager
    # ... use api_key where actually needed, or remove if unused
```

If `API_KEY` is not actually needed by this function, **remove it entirely**
rather than moving it to an environment variable. Dead credential references
should not exist in production code.

---

### 🟠 F-03 — Database Connection Never Closed (Resource Leak)

**OWASP:** A05:2021 – Security Misconfiguration
**CWE:** CWE-772
**Severity:** MEDIUM
**Confidence:** Confirmed
**Lines:** 9–14

**Vulnerable code:**
```python
conn = sqlite3.connect('database.db')   # line 9  ← opened
cursor = conn.cursor()
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)
return cursor.fetchall()
# conn is never closed — no finally, no with, no conn.close()
```

`conn` is opened but never explicitly closed. In a server context where
`get_user_data` is called repeatedly:

- Each call leaks a file descriptor and an open SQLite lock on `database.db`
- Under concurrent load this exhausts file descriptors → server crash
- An open write lock can block other processes from accessing the database
- If an exception is raised before `fetchall()` (e.g. via SQL injection error),
  the connection is never reclaimed

**Remediation — use a context manager:**
```python
def get_user_data(user_id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchall()
    # conn.close() called automatically on exit, even on exception
```

---

### 🟠 F-04 — Unbounded `fetchall()` — Data Over-Exposure and Memory DoS

**OWASP:** A03:2021 – Injection (excessive data return)
**CWE:** CWE-400
**Severity:** MEDIUM
**Confidence:** Confirmed
**Lines:** 13

**Vulnerable code:**
```python
return cursor.fetchall()
```

There is no `LIMIT` clause in the query and `fetchall()` loads every matching
row into memory at once.

**Two compounded risks:**

1. **Data over-exposure:** Combined with the SQL injection in F-01, an attacker
   payload of `1 OR 1=1` causes `fetchall()` to return the **entire `users`
   table** in a single call — all rows, all columns, including any
   password hashes, tokens, or PII in the table.

2. **Memory exhaustion:** On a legitimately large table, even a benign query
   with an injected `1 OR 1=1` condition returns unbounded rows into the
   Python process heap. This can exhaust memory and crash the server.

**Remediation:**
```python
# Add LIMIT to the query and use fetchmany for large result sets
cursor.execute("SELECT id, name FROM users WHERE id = ? LIMIT 100", (user_id,))
rows = cursor.fetchall()
return rows
```

Explicitly select only the columns needed (avoid `SELECT *`) and always
apply a `LIMIT` appropriate to the use case.

---

### 🟠 F-05 — No Error Handling — Unhandled Exceptions Leak Internals

**OWASP:** A09:2021 – Security Logging and Monitoring Failures
**CWE:** CWE-209
**Severity:** MEDIUM
**Confidence:** Confirmed
**Lines:** 4–14

The function has no `try/except` block. Any of the following errors propagate
as unhandled exceptions to the caller:

| Scenario | Exception raised | Information leaked |
|---|---|---|
| `database.db` missing or inaccessible | `sqlite3.OperationalError` | File path, DB name |
| SQL syntax error (e.g. injection attempt) | `sqlite3.OperationalError` | Full query string, column names |
| `user_id` is not a string (e.g. `None`) | `TypeError: can only concatenate str…` | Source line, variable types |
| Permission denied on `database.db` | `sqlite3.OperationalError` | File path, OS error message |

In a web framework these exceptions typically produce a 500 response body or
log entry that includes the stack trace, revealing the DB file path, the raw
SQL query (including any injected content), and internal code structure.

**Remediation:**
```python
import logging
logger = logging.getLogger(__name__)

def get_user_data(user_id):
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM users WHERE id = ? LIMIT 100",
                           (user_id,))
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error("get_user_data failed for user_id=%r: %s", user_id, e)
        return []   # or raise a typed application exception
```

---

### 🟡 F-06 — Hardcoded Relative Database Path

**OWASP:** A05:2021 – Security Misconfiguration
**CWE:** CWE-426
**Severity:** LOW
**Confidence:** Confirmed
**Lines:** 9

**Vulnerable code:**
```python
conn = sqlite3.connect('database.db')
```

The path `database.db` resolves relative to the process working directory
(`os.getcwd()`). This is unpredictable across deployment environments:

- Running from a different directory silently creates a **new, empty**
  `database.db` rather than raising an error — masking the misconfiguration
  entirely and returning empty results as if the table is empty.
- The path is not configurable without a code change.
- Logs and error messages expose the file name and implicitly the server path.

**Remediation:**
```python
import os
DB_PATH = os.environ.get("DATABASE_PATH", "/opt/app/data/database.db")

def get_user_data(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        ...
```

---

### 🔵 F-07 — No Input Validation on `user_id` (Defence-in-Depth Gap)

**OWASP:** A03:2021 – Injection
**CWE:** CWE-20
**Severity:** INFO
**Confidence:** Confirmed
**Lines:** 4, 11

`user_id` accepts any type with no guard. Passing `None`, an `int`, a `list`,
or a very long string causes a `TypeError` at concatenation (line 11) before
the SQL engine is even reached — but the error is unhandled (see F-05).

The F-01 fix (parameterized query) eliminates injection regardless of content,
but defence-in-depth recommends validating at the function boundary:

```python
def get_user_data(user_id: str) -> list:
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError(f"user_id must be a non-empty string, got {type(user_id)}")
    ...
```

---

### 🔵 F-08 — Dead `import os` (Unused Import)

**Severity:** INFO
**Confidence:** Confirmed
**Lines:** 1

```python
import os   # imported but never referenced
```

`os` is imported at the top of the file but not used anywhere. No security
impact; pure code hygiene. Remove or replace with a real usage (e.g. for
the environment-variable credential loading recommended in F-02 and F-06).

---

## Attack-Path Reasoning — F-01 (CRITICAL)

```
Attacker calls get_user_data("1 OR 1=1")
            ↓
No type or length check on user_id  (line 4)
            ↓
String concatenated into numeric SQL context — no quoting  (line 11)
   query = "SELECT * FROM users WHERE id = 1 OR 1=1"
            ↓
cursor.execute(raw SQL) against database.db  (line 12)
            ↓
WHERE clause always TRUE → all rows selected
            ↓
cursor.fetchall() — no LIMIT — entire users table in memory  (line 13)
            ↓
All user records returned to attacker (PII, password hashes, tokens)
            ↓
[Extended] ATTACH DATABASE → arbitrary file write on server filesystem
```

---

## Compound Risk: F-01 + F-04 + F-05

These three findings chain together into a particularly dangerous path:

```
SQL Injection (F-01)
    → no row limit (F-04) → entire table exfiltrated in one call
    → no error handling (F-05) → syntax errors reveal query structure,
      aiding injection payload refinement
    → connection leak (F-03) → injection attempts that error lock the
      DB file, amplifying DoS impact
```

---

## Production Readiness Assessment

| Dimension | Status | Notes |
|-----------|--------|-------|
| Security — Injection | ❌ CRITICAL | Exploitable SQL injection against persistent DB |
| Security — Secrets | ❌ Fail | Hard-coded `sk-` API key in source |
| Security — Error Handling | ❌ Fail | No try/except; stack traces leaked |
| Resource Management | ❌ Fail | DB connection never closed |
| Data Protection | ❌ Fail | Unbounded SELECT *; all rows returned |
| Configuration | ⚠️ Warn | Relative DB path; no environment config |
| Input Validation | ❌ Fail | No type or length guard on user_id |
| Logging | ❌ Fail | No logging whatsoever |
| Testing | ❌ Fail | No tests present |
| Code Quality | ⚠️ Warn | Dead import, dead credential variable |

---

## Remediation Priority

| Priority | Finding | Action |
|----------|---------|--------|
| 🔴 Immediate | F-01 | Replace string concatenation with `cursor.execute("… WHERE id = ?", (user_id,))` |
| 🔴 Immediate | F-02 | Remove `API_KEY = "sk-…"` from source; load from `os.environ` if needed |
| 🟠 Before deployment | F-03 | Wrap connection in `with sqlite3.connect(…) as conn:` |
| 🟠 Before deployment | F-04 | Add `LIMIT`, select specific columns, avoid `SELECT *` |
| 🟠 Before deployment | F-05 | Add `try/except sqlite3.Error` with logging and safe return |
| 🟡 Low priority | F-06 | Move DB path to `os.environ["DATABASE_PATH"]` |
| 🔵 Defence-in-depth | F-07 | Add `isinstance` type guard at function entry |
| 🔵 Hygiene | F-08 | Remove unused `import os` (or repurpose for F-02/F-06) |

---

## Fully Remediated Version

```python
import os
import sqlite3
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("DATABASE_PATH", "/opt/app/data/database.db")


def get_user_data(user_id: str) -> list:
    """Fetch a single user record by ID.

    Args:
        user_id: The user's ID string. Must be non-empty.

    Returns:
        List of matching row tuples, or empty list on error.

    Raises:
        ValueError: If user_id is not a valid non-empty string.
    """
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError(f"user_id must be a non-empty string, got {type(user_id)!r}")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, email FROM users WHERE id = ? LIMIT 1",
                (user_id,),
            )
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error("get_user_data failed for user_id=%r: %s", user_id, e)
        return []
```

**Changes from vulnerable original:**
1. `API_KEY` removed entirely (was unused and a security liability)
2. Parameterized query — SQL injection eliminated
3. `with` statement — connection always closed, even on exception
4. `SELECT id, name, email … LIMIT 1` — minimal columns, bounded result
5. `try/except sqlite3.Error` — errors logged internally, not leaked
6. Type guard on `user_id` — fail-fast with clear error
7. `DB_PATH` from environment variable — configurable, not hardcoded
8. `logging` — operational visibility for security events

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
            "shortDescription": { "text": "SQL Injection via string concatenation against persistent DB (CWE-89, OWASP A03:2021)" },
            "defaultConfiguration": { "level": "error" }
          },
          {
            "id": "F-02",
            "name": "HardcodedCredential",
            "shortDescription": { "text": "Hard-coded API key literal in source (CWE-798, OWASP A02:2021)" },
            "defaultConfiguration": { "level": "error" }
          },
          {
            "id": "F-03",
            "name": "ConnectionLeak",
            "shortDescription": { "text": "Database connection opened but never closed (CWE-772)" },
            "defaultConfiguration": { "level": "warning" }
          },
          {
            "id": "F-04",
            "name": "UnboundedFetchall",
            "shortDescription": { "text": "fetchall() with no LIMIT — data over-exposure and memory DoS (CWE-400)" },
            "defaultConfiguration": { "level": "warning" }
          },
          {
            "id": "F-05",
            "name": "MissingErrorHandling",
            "shortDescription": { "text": "No try/except — exceptions propagate with internal details (CWE-209)" },
            "defaultConfiguration": { "level": "warning" }
          },
          {
            "id": "F-06",
            "name": "HardcodedDBPath",
            "shortDescription": { "text": "Relative database path not configurable via environment (CWE-426)" },
            "defaultConfiguration": { "level": "note" }
          },
          {
            "id": "F-07",
            "name": "NoInputValidation",
            "shortDescription": { "text": "No type or length check on user_id before SQL use (CWE-20)" },
            "defaultConfiguration": { "level": "note" }
          },
          {
            "id": "F-08",
            "name": "DeadImport",
            "shortDescription": { "text": "import os is unused" },
            "defaultConfiguration": { "level": "none" }
          }
        ]
      }
    },
    "results": [
      {
        "ruleId": "F-01", "level": "error",
        "message": { "text": "user_id concatenated directly into SQL string (numeric context, no quoting) against persistent database.db — CRITICAL SQL Injection (OWASP A03:2021, CWE-89)." },
        "locations": [{ "physicalLocation": {
          "artifactLocation": { "uri": "vulnerable_app.py" },
          "region": { "startLine": 11, "endLine": 12 }
        }}]
      },
      {
        "ruleId": "F-02", "level": "error",
        "message": { "text": "API_KEY = \"sk-12345ABCDE\" — hard-coded credential with sk- prefix committed to source (CWE-798, OWASP A02:2021)." },
        "locations": [{ "physicalLocation": {
          "artifactLocation": { "uri": "vulnerable_app.py" },
          "region": { "startLine": 6, "endLine": 6 }
        }}]
      },
      {
        "ruleId": "F-03", "level": "warning",
        "message": { "text": "sqlite3 connection opened at line 9 but never closed — file descriptor and lock leak (CWE-772)." },
        "locations": [{ "physicalLocation": {
          "artifactLocation": { "uri": "vulnerable_app.py" },
          "region": { "startLine": 9, "endLine": 14 }
        }}]
      },
      {
        "ruleId": "F-04", "level": "warning",
        "message": { "text": "fetchall() with no LIMIT clause — entire table returned on injection; memory exhaustion vector (CWE-400)." },
        "locations": [{ "physicalLocation": {
          "artifactLocation": { "uri": "vulnerable_app.py" },
          "region": { "startLine": 13, "endLine": 13 }
        }}]
      },
      {
        "ruleId": "F-05", "level": "warning",
        "message": { "text": "No try/except — sqlite3.OperationalError and TypeError propagate with stack trace, leaking DB path and query structure (CWE-209)." },
        "locations": [{ "physicalLocation": {
          "artifactLocation": { "uri": "vulnerable_app.py" },
          "region": { "startLine": 4, "endLine": 14 }
        }}]
      },
      {
        "ruleId": "F-06", "level": "note",
        "message": { "text": "Relative path 'database.db' resolves from CWD — silently creates empty DB on misconfiguration (CWE-426)." },
        "locations": [{ "physicalLocation": {
          "artifactLocation": { "uri": "vulnerable_app.py" },
          "region": { "startLine": 9, "endLine": 9 }
        }}]
      },
      {
        "ruleId": "F-07", "level": "note",
        "message": { "text": "user_id has no type, length, or character validation before concatenation (CWE-20)." },
        "locations": [{ "physicalLocation": {
          "artifactLocation": { "uri": "vulnerable_app.py" },
          "region": { "startLine": 4, "endLine": 4 }
        }}]
      },
      {
        "ruleId": "F-08", "level": "none",
        "message": { "text": "import os is unused." },
        "locations": [{ "physicalLocation": {
          "artifactLocation": { "uri": "vulnerable_app.py" },
          "region": { "startLine": 1, "endLine": 1 }
        }}]
      }
    ]
  }]
}
```

---

*Review generated by IBM Bob · Actor-Critic skill (§49) · 2025-08-30*
