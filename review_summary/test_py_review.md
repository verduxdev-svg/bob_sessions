# Code Review — `test.py`

**Date:** 2025-07-08  
**Mode:** MODE A — Local Code Review  
**Reviewer:** Bob (AI Principal Engineer)

---

## Executive Summary

`test.py` is a demonstration script that intentionally contains two well-known anti-patterns.  
Both are **real, confirmed vulnerabilities** — not theoretical. The file is not production-safe in any form.

---

## Findings

---

### 🔴 CRITICAL — Hardcoded Secret  
**Severity:** CRITICAL | **Confidence:** Confirmed  
**Location:** [`test.py` line 1](../test.py:1)

```python
API_KEY = "12345"
```

**Root Cause:** A credential is baked directly into source code.  
**Why it matters:** Secrets in source code are committed to version control, leak in CI logs, appear in code reviews, and cannot be rotated without a code change. Even a "dummy" key establishes a bad pattern that may be replicated with real values.  
**Impact:** Credential exposure leading to unauthorized API access.  
**Attack path:**
```
Developer commits file → git history retains value forever
                       → anyone with repo read access extracts key
                       → key used to authenticate against API
```
**Fix:**
```python
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable is not set")
```
Place the real value in `.env` (already in `.gitignore` for this repo).

---

### 🔴 HIGH — SQL Injection  
**Severity:** HIGH | **Confidence:** Confirmed  
**Location:** [`test.py` line 17](../test.py:17)

```python
query = "SELECT * FROM users WHERE id = '" + user_id + "'"
cursor.execute(query)
```

**Root Cause:** Attacker-controlled input is concatenated directly into a raw SQL string with no parameterization, escaping, or validation.  
**Why it matters:** Any caller of `fetch_user_data()` can inject arbitrary SQL. The script itself demonstrates the exploit on line 35–36 (`"1' OR '1'='1"`).  
**Impact:** Full data exfiltration — the payload `1' OR '1'='1` returns all rows, bypassing the intended single-row lookup. In a real database this could also lead to data deletion (`DROP TABLE`), out-of-band exfiltration, or (in some engines) remote code execution.  
**Attack path:**
```
Caller supplies: "1' OR '1'='1"
Resulting SQL:   SELECT * FROM users WHERE id = '1' OR '1'='1'
Database effect: Returns every row in the users table
```
**Fix — use parameterized queries:**
```python
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```
This separates code from data at the driver level and is immune to injection regardless of input content.

---

### 🟠 MEDIUM — Missing `import sqlite3`  
**Severity:** MEDIUM | **Confidence:** Confirmed  
**Location:** [`test.py` line 7](../test.py:7)

`sqlite3.connect()` is called but `sqlite3` is never imported. The script will raise a `NameError` at runtime before any intentional behavior runs.  
**Fix:**
```python
import sqlite3
```

---

### 🟠 MEDIUM — Broken `__name__` Guard  
**Severity:** MEDIUM | **Confidence:** Confirmed  
**Location:** [`test.py` line 28](../test.py:28)

```python
if name == "main":
```

The canonical Python idiom `if __name__ == "__main__":` uses `__name__` (dunder) and compares to `"__main__"` (also dunder). As written, `name` is an undefined variable that will raise a `NameError`, and the comparison string is missing the double underscores, so the guard would never trigger even if `name` were somehow defined.  
**Fix:**
```python
if __name__ == "__main__":
```

---

### 🟡 LOW — Bare `except sqlite3.Error` Returns Error String  
**Severity:** LOW | **Confidence:** Confirmed  
**Location:** [`test.py` lines 23–24](../test.py:23)

```python
except sqlite3.Error as e:
    return str(e)
```

Error details are returned to the caller as a plain string. In a real API this silently converts an exception into valid-looking data and leaks database error messages (e.g., table names, column names, SQL fragments) to untrusted callers.  
**Fix:** Log the error internally and return a typed sentinel or raise a domain exception:
```python
except sqlite3.Error as e:
    logging.error("Database error: %s", e)
    return []   # or raise a domain-level exception
```

---

### 🔵 INFO — Comment Syntax Error on Line 10  
**Location:** [`test.py` line 10](../test.py:10)

```python
Initialize a dummy table for the environment
```

The `#` is missing — this line is a bare statement that happens to be a string expression (valid Python at module level but a silent no-op inside a function where it appears). It should be:
```python
# Initialize a dummy table for the environment
```

---

## Summary Table

| # | Severity | Confidence | Title | Line |
|---|----------|------------|-------|------|
| 1 | 🔴 CRITICAL | Confirmed | Hardcoded API key | 1 |
| 2 | 🔴 HIGH | Confirmed | SQL Injection via string concatenation | 17 |
| 3 | 🟠 MEDIUM | Confirmed | Missing `import sqlite3` | 7 |
| 4 | 🟠 MEDIUM | Confirmed | Broken `__name__` guard | 28 |
| 5 | 🟡 LOW | Confirmed | DB error string returned to caller | 23 |
| 6 | 🔵 INFO | Confirmed | Missing `#` on comment line | 10 |

---

## Production Readiness Verdict

**❌ Not production-ready.**  

This file must not be deployed or used as a template for real code. All six findings require remediation; findings 1 and 2 are individually sufficient to block any release.
