# Code Review — `test.py`

**Reviewer:** Bob (automated production-grade review)  
**Date:** 2026-08-29  
**Mode:** MODE A — Local Code Review  
**Scope:** `test.py` (36 lines)

---

## Executive Summary

`test.py` is an intentionally insecure demonstration script. It deliberately
embeds anti-patterns for educational purposes — the file's own inline comments
acknowledge them. This review treats them as real defects because no context
indicates they are contained or unexploitable.

The file should **never** be deployed, imported, or placed on any path reachable
by a running application.

---

## Findings

### 🔴 HIGH — Hardcoded API Key (CWE-798)

| Field | Value |
|---|---|
| **Location** | `test.py:1` |
| **Confidence** | Confirmed |
| **Exploitability** | Any developer with read access to the repo or its history |

```python
API_KEY = "12345"
```

A credential is committed in plaintext at module scope. Even a trivially weak
value like `"12345"` establishes an insecure pattern. If this file is committed
to version control the string is permanently recoverable from `git log` even
after deletion. Sensitive values must only be loaded from environment variables
via `os.getenv()` or a secrets manager; they must never appear as source-code
literals.

**Remediation:**
```python
import os
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable is not set")
```

---

### 🔴 HIGH — SQL Injection (CWE-89, OWASP A03:2021)

| Field | Value |
|---|---|
| **Location** | `test.py:17` |
| **Confidence** | Confirmed |
| **Exploitability** | Any caller that controls `user_id` |

```python
query = "SELECT * FROM users WHERE id = '" + user_id + "'"
cursor.execute(query)
```

`user_id` is concatenated directly into the SQL string without any sanitization
or parameterization. The file's own test case at line 35 demonstrates a working
payload (`1' OR '1'='1`) that dumps the full `users` table.

**Attack path:**
```
Caller passes malicious user_id
        ↓
String is concatenated into raw SQL
        ↓
cursor.execute() runs attacker-controlled query
        ↓
Entire users table returned / data modified / exfiltrated
```

**Remediation — use a parameterized query:**
```python
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

---

### 🟠 MEDIUM — Missing `import sqlite3` (NameError at runtime, CWE-480)

| Field | Value |
|---|---|
| **Location** | `test.py:7` |
| **Confidence** | Confirmed |

`sqlite3` is used but never imported. The file will raise a `NameError` on
every execution path. This is a correctness defect independent of the security
issues.

**Remediation:** Add `import sqlite3` at the top of the file.

---

### 🟠 MEDIUM — Broken `__name__ == "__main__"` Guard (Syntax Error, CWE-480)

| Field | Value |
|---|---|
| **Location** | `test.py:28` |
| **Confidence** | Confirmed |

```python
if name == "main":   # line 28 — wrong
```

The correct guard is `if __name__ == "__main__":`. The dunder prefixes are
absent. Python will evaluate this as a comparison of the (undefined) variable
`name` with the string `"main"`, raising `NameError: name 'name' is not
defined` at import time. The script will never execute its main block.

**Remediation:**
```python
if __name__ == "__main__":
```

---

### 🟡 LOW — Missing Comment Marker Causes Orphaned Plain-Text Line

| Field | Value |
|---|---|
| **Location** | `test.py:10` and `test.py:33` |
| **Confidence** | Confirmed |

Lines 10 and 33 are plain English prose without a `#` prefix:

```
10 | Initialize a dummy table for the environment
33 | Test case 2: Exploitation of the SQL injection vulnerability
```

Both lines are invalid Python syntax and will cause a `SyntaxError` before any
code executes. The `#` comment prefix is missing.

**Remediation:** Prefix both lines with `#`.

---

### 🔵 INFO — `except sqlite3.Error` Returns a String Instead of Re-raising

| Field | Value |
|---|---|
| **Location** | `test.py:23–24` |
| **Confidence** | Confirmed |

```python
except sqlite3.Error as e:
    return str(e)
```

Silently swallowing exceptions and converting them to strings makes call sites
unable to distinguish a legitimate empty result from an error. Error messages
may also contain internal state that should not be returned to callers.
Prefer raising a domain-specific exception or logging the error and re-raising.

---

## Summary Table

| # | Severity | Finding | Location | Confidence |
|---|---|---|---|---|
| 1 | 🔴 HIGH | Hardcoded credential | `test.py:1` | Confirmed |
| 2 | 🔴 HIGH | SQL Injection | `test.py:17` | Confirmed |
| 3 | 🟠 MEDIUM | Missing `import sqlite3` | `test.py:7` | Confirmed |
| 4 | 🟠 MEDIUM | Broken `__name__` guard | `test.py:28` | Confirmed |
| 5 | 🟡 LOW | Missing `#` on comment lines | `test.py:10,33` | Confirmed |
| 6 | 🔵 INFO | Error swallowed as string | `test.py:23` | Confirmed |

---

## Production Readiness Verdict

❌ **Not production-ready.**

The file contains a working, self-demonstrated SQL injection vulnerability, a
hardcoded credential, and multiple syntax errors that prevent execution. It
should not be deployed, and it should not be referenced or imported by any other
module.

---

*Persisted by Bob review skill — `review_summary/test_py_review.md`*
