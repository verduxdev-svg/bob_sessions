# Code Review: `requirements.txt`

**Reviewer:** Bob (AI Code Review)  
**Date:** 2025-07-11  
**Mode:** MODE A — Local Code Review  
**Target:** [`requirements.txt`](../requirements.txt)

---

## Executive Summary

[`requirements.txt`](../requirements.txt) is **empty**. The repository contains [`watsonx_mcp_server.py`](../watsonx_mcp_server.py) which imports three third-party packages (`requests`, `python-dotenv`, `mcp`) that are not declared anywhere. Any developer or CI/CD environment that tries to run the project will encounter immediate `ModuleNotFoundError` failures with no indication of what needs to be installed.

---

## Findings

---

### 🟠 MEDIUM — Three Third-Party Dependencies Are Undeclared

**Location:** [`requirements.txt`](../requirements.txt) (empty), [`watsonx_mcp_server.py:2-4`](../watsonx_mcp_server.py:2)  
**Confidence:** Confirmed

`watsonx_mcp_server.py` imports:

| Import | PyPI Package | Purpose |
|--------|-------------|---------|
| `import requests` | `requests` | HTTP calls to IBM IAM and Watsonx APIs |
| `from dotenv import load_dotenv` | `python-dotenv` | Loading `.env` credentials |
| `from mcp.server import MCPServer` | `mcp` (or `mcp-server`) | MCP server framework |

None of these are declared in `requirements.txt`. The consequence is:

- A fresh `pip install -r requirements.txt` installs nothing.
- Running `watsonx_mcp_server.py` raises `ModuleNotFoundError` immediately.
- CI/CD pipelines, containers, and collaborators have no reliable way to reproduce the environment.

**Remediation:** Populate `requirements.txt` with pinned or minimum-bounded versions:

```
requests>=2.31.0
python-dotenv>=1.0.0
mcp>=1.0.0
```

For production or reproducible builds, pin exact versions and commit a `pip freeze` lockfile or use `pip-tools` / `poetry` to generate a `requirements.lock`.

---

### 🟡 LOW — No Dependency Version Constraints

**Confidence:** Confirmed (follows from above)

Because the file is empty, there are no version constraints at all. When dependencies are added, use minimum bounds (`>=`) to prevent accidental installation of vulnerable older versions, and consider upper bounds or exact pins for production environments where reproducibility and supply-chain control matter.

---

### 🔵 INFO — No `requirements-dev.txt` or Equivalent

There is no development-dependency file. For a project that may grow to include tests, linters (`flake8`, `ruff`), type checkers (`mypy`), or security scanners (`bandit`, `safety`), separating runtime from dev dependencies early prevents bloated production installs.

---

## Summary Table

| # | Severity | Confidence | Issue |
|---|----------|------------|-------|
| 1 | 🟠 MEDIUM | Confirmed | `requests`, `python-dotenv`, `mcp` used but not declared — project is uninstallable |
| 2 | 🟡 LOW | Confirmed | No version bounds once dependencies are added |
| 3 | 🔵 INFO | Confirmed | No dev-dependency file |

---

## Recommended `requirements.txt`

```
requests>=2.31.0
python-dotenv>=1.0.0
mcp>=1.0.0
```

Add versions appropriate to your tested environment. Run `pip freeze > requirements.lock` (or use `pip-tools`) to lock transitive dependencies for reproducible deployments.

---

## Production Readiness

**Not production-ready.** The empty file means the project cannot be installed or deployed reliably. This is the single most actionable fix in the entire repository — it is a one-minute change with immediate impact on every developer, CI run, and deployment.
