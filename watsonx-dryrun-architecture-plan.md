# Watsonx MCP Server — Dry-Run Fix + Architecture Expansion Plan

## Overview

**Goal:** Fix all code bugs found in the dry-run analysis of `watsonx_mcp_server.py` and
`test.py`, wire up dependencies properly, and produce an architecture document that shows
how to grow this project from a single-tool MCP server into a well-structured, multi-tool
security auditing pipeline.

**Scope:**
- Fix import bug in `watsonx_mcp_server.py` (wrong MCP SDK class name)
- Fix syntax and logic errors in `test.py`
- Add `requirements.txt` so the project is installable
- Write `ARCHITECTURE.md` — full project flow, component diagram, and growth roadmap

**Non-Goals:**
- No credential file changes (`.env` stays as-is; never read or modified)
- No changes to `.bobignore` or `.gitignore`
- No changes to existing `README.md` or `SECURITY.MD`
- No new Watson AI models or tools beyond fixing existing ones

---

## Dry-Run Findings Summary

| File | Line | Issue | Severity |
|---|---|---|---|
| `watsonx_mcp_server.py` | 4 | `from mcp.server import MCPServer` — ✅ correct for mcp 2.x; `FastMCP` was renamed to `MCPServer` in v2 | ✅ No action |
| `watsonx_mcp_server.py` | 9 | `mcp = MCPServer(...)` — ✅ correct for mcp 2.x | ✅ No action |
| `test.py` | 1 | Missing `import sqlite3` — NameError at runtime | 🟡 Medium |
| `test.py` | 10 | Bare text `Initialize a dummy table...` — SyntaxError (missing `#`) | 🔴 Critical |
| `test.py` | 28 | `if name == "main":` — missing `__` dunder syntax; block never runs | 🟡 Medium |
| `test.py` | 33 | Bare unindented string `Test case 2:` — SyntaxError | 🔴 Critical |
| project root | — | No `requirements.txt` — `python-dotenv`, `requests`, `mcp` undeclared | 🟡 Medium |

---

## Sub-Tasks

---

### Sub-Task 1 — Verify `watsonx_mcp_server.py` import (No Change Required)

**Intent**
~~The server uses `MCPServer` which does not exist in MCP SDK v2.~~
**Correction (verified 2025):** The installed SDK is **mcp 2.1.1**. In mcp 2.x, `FastMCP`
was **renamed to `MCPServer`** — `from mcp.server import MCPServer` is the correct import.
The comment on line 8 is accurate. No code change is needed.

**Verification Run**
- `python -m py_compile watsonx_mcp_server.py` → **exit 0 ✅**
- `from mcp.server import MCPServer` → **import succeeds ✅**
- `MCPServer` exposes `.tool()` decorator and `.run()` method ✅

**Expected Outcomes**
- `watsonx_mcp_server.py` is already correct as-is for mcp 2.x
- No edits required to this file for the import bug

**Todo List**
1. ~~Open `watsonx_mcp_server.py`.~~
2. ~~Replace line 4: `from mcp.server import MCPServer` → `from mcp import FastMCP`~~
3. ~~Replace line 9: `mcp = MCPServer("WatsonxCritic")` → `mcp = FastMCP("WatsonxCritic")`~~
4. ~~Remove the now-inaccurate comment on line 8 about SDK v2 renaming.~~

**Relevant Context**
- mcp 2.x migration guide: `FastMCP` renamed to `MCPServer` (from `mcp.server`)
- File `watsonx_mcp_server.py` lines 4, 8–9 are correct for mcp 2.1.1

**Status**: `[x] complete — no changes needed, import verified correct`

---

### Sub-Task 2 — Fix `test.py` syntax and logic errors

**Intent**
`test.py` is the intentionally-vulnerable code file used to demonstrate what the MCP
security audit tool should detect. However it contains SyntaxErrors that prevent Python
from even parsing it, and a missing import that causes a NameError. These must be fixed
so the file is valid Python (while keeping the intentional SQL injection vulnerability
for the audit demo).

**Expected Outcomes**
- `python -m py_compile test.py` exits with code 0 (no syntax errors)
- `import sqlite3` is present at the top of the file
- Line 10 is a proper Python comment (`# Initialize a dummy table...`)
- `if __name__ == "__main__":` uses correct dunder syntax
- Line 33 bare string is converted to a proper comment

**Todo List**
1. Open `test.py`.
2. Add `import sqlite3` on line 2 (after the existing line 1).
3. Fix line 10: add `#` prefix → `# Initialize a dummy table for the environment`
4. Fix line 28: `if name == "main":` → `if __name__ == "__main__":`
5. Fix line 33: add `#` prefix → `# Test case 2: Exploitation of the SQL injection vulnerability`
6. Keep the `API_KEY = "12345"` hardcoded credential on line 1 — it is intentional for
   the security audit demo (it's a fake key, not a real IBM credential).

**Relevant Context**
- File: `test.py` — all lines
- The SQL injection on line 17 (`query = "SELECT * FROM users WHERE id = '" + user_id + "'"`)
  must remain unchanged — it is the intentional vulnerability for audit testing

**Status**: `[ ] pending`

---

### Sub-Task 3 — Add `requirements.txt`

**Intent**
The project has no declared dependencies. Anyone cloning the repo cannot run
`watsonx_mcp_server.py` without guessing the packages. This sub-task pins the three
required packages with minimum safe versions.

**Expected Outcomes**
- `requirements.txt` exists in project root
- Contains `mcp`, `requests`, and `python-dotenv`
- A developer can run `pip install -r requirements.txt` and then start the server

**Todo List**
1. Create `requirements.txt` in the project root with the following content:
   ```
   mcp>=1.0.0
   requests>=2.31.0
   python-dotenv>=1.0.0
   ```

**Relevant Context**
- No existing `requirements.txt`, `pyproject.toml`, or `setup.py` in project root
- Versions pinned to minimum known-good, not locked, to avoid hampering hackathon participants

**Status**: `[ ] pending`

---

### Sub-Task 4 — Write `ARCHITECTURE.md`

**Intent**
Document the full system architecture — current state and how to grow it. This gives
hackathon participants a clear map of how data flows from Bob IDE → MCP server →
IBM IAM → Watsonx.ai, and shows concrete next steps for expanding the project.

**Expected Outcomes**
- `ARCHITECTURE.md` exists in project root
- Contains: component overview, data flow description, environment variable table,
  current tool inventory, and a "Growth Roadmap" section with 3 expansion tiers

**Todo List**
1. Create `ARCHITECTURE.md` with the following sections:

   **§1 — System Overview**
   - Single-paragraph description of the pipeline
   - Component list: Bob IDE, MCP stdio transport, watsonx_mcp_server.py,
     IBM IAM token endpoint, Watsonx.ai text generation API

   **§2 — Data Flow (step-by-step)**
   1. Bob IDE invokes a registered MCP tool (e.g. `watsonx_security_audit`)
   2. MCP server receives the `code_diff` argument via stdio transport
   3. Server calls IBM IAM `/identity/token` to exchange `IBM_CLOUD_API_KEY` for a
      short-lived Bearer token
   4. Server POST to Watsonx.ai `/ml/v1/text/generation` with Granite model prompt
   5. Response (Markdown + SARIF block) returned to Bob IDE

   **§3 — Environment Variables**
   Table: `IBM_CLOUD_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_URL` — purpose and format

   **§4 — Current Tool Inventory**
   - `watsonx_security_audit(code_diff: str) -> str`
     Sends a code diff to IBM Granite 3 8B Instruct. Returns a Markdown report with
     embedded SARIF v2.1.0 JSON.

   **§5 — Growth Roadmap**

   *Tier 1 — Short-term (single session additions):*
   - Add `watsonx_code_explain` tool — explains selected code in plain English
   - Add `watsonx_fix_suggestion` tool — asks Watsonx.ai to produce a corrected
     version of a flagged snippet
   - Add token caching — cache the IAM Bearer token for its 60-minute TTL so each
     tool call doesn't re-authenticate

   *Tier 2 — Medium-term (project structure):*
   - Split server into `server.py` (MCP wiring), `watsonx_client.py` (API calls),
     `iam.py` (token management)
   - Add `pytest` test suite with mocked HTTP calls (no real API key needed in CI)
   - Add GitHub Actions workflow: `pip install -r requirements.txt && pytest`

   *Tier 3 — Long-term (production hardening):*
   - Replace polling IAM token with a token refresh background task
   - Add SARIF output file writer — persist audit reports to `reports/` directory
   - Add `watsonx_batch_audit` tool — accepts multiple diffs and aggregates SARIF results
   - Integrate with GitHub Actions: trigger MCP audit on every PR via `gh` CLI

2. Save file as `ARCHITECTURE.md` in project root.

**Relevant Context**
- `watsonx_mcp_server.py` — source of truth for current tools and API calls
- `SECURITY.MD` — informs the env-var table descriptions
- `AGENTS.md` — notes that `dist/`, `build/`, `target/` are git-ignored; CI plan must
  not commit artifacts

**Status**: `[ ] pending`

---

## Implementation Order

```
Sub-Task 1 (fix server import) → Sub-Task 2 (fix test.py) → Sub-Task 3 (requirements.txt) → Sub-Task 4 (ARCHITECTURE.md)
```

Tasks 1–3 are independent of each other and can be done in any order; Task 4 should
come last since it documents the corrected state.

---

## Validation Checklist (run after all sub-tasks complete)

- [ ] `python -m py_compile watsonx_mcp_server.py` exits 0
- [ ] `python -m py_compile test.py` exits 0
- [ ] `pip install -r requirements.txt` completes without error
- [ ] `python watsonx_mcp_server.py` starts and waits for stdio input (no crash on startup)
- [ ] `ARCHITECTURE.md` exists and all 5 sections are present
