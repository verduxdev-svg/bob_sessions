# Hackathon Submission Plan: Intelligent Code Review & Security Quality Coach

## Overview

**Goal:** Transform the existing Actor-Critic security review prototype into a
complete, judge-ready hackathon submission that scores maximum points across all
four rubric dimensions (20/20).

**Current state:**
- ✅ `watsonx_mcp_server.py` — MCP server with `watsonx_security_audit` tool
- ✅ `.bob/skills/review/SKILL.md` — Actor-Critic review skill (88 sections)
- ✅ `review_summary/` — 3 Markdown + SARIF review reports already generated
- ✅ `ARCHITECTURE.md`, `AGENTS.md`, `SECURITY.MD` — docs in place
- ❌ `README.md` — still the generic hackathon template (needs full replacement)
- ❌ `.env.example` — referenced in README but missing from repo
- ❌ No screenshots of Bob session consumption (required for judging validation)
- ❌ No custom `SecurityReviewer` mode file
- ❌ No watsonx Orchestrate `Security Approver Agent` (Phase 3)
- ❌ No ngrok tunnel setup or documented alternative for Orchestrate integration
- ❌ No demo video

**Approach:** Six focused sub-tasks, ordered by judging impact. Each sub-task is
independently completable. The first four deliver the core repository structure;
sub-tasks 5–6 deliver the Orchestrate integration and submission packaging.

---

## Sub-Task 1 — Replace README.md with the Rubric-Mapped Submission README

**Status:** `[ ] pending`

**Intent:**
The current README is the generic hackathon template. Judges score directly
against the README structure. It must be replaced with the rubric-mapped version
specified in the hackathon guide, augmented with evidence links that point to
real artifacts already in the repo.

**Expected Outcomes:**
- `README.md` contains all four rubric sections (Completeness, Creativity,
  Design, Effectiveness) with concrete evidence pointers.
- Every claim in the README links to a real file already committed (review
  reports, SARIF blocks, skill file, MCP server).
- Setup instructions are accurate for the current codebase (references
  `watsonx_mcp_server.py`, correct env var names, correct mode name).
- No placeholder text remains.

**Todo List:**
1. Write new `README.md` with the four rubric sections from the hackathon guide.
2. Under **Completeness**: link to `watsonx_mcp_server.py`, `ARCHITECTURE.md`,
   and the three `review_summary/*.md` files as evidence of end-to-end execution.
3. Under **Creativity**: reference the Actor-Critic two-pass pattern in
   `.bob/skills/review/SKILL.md` (§49) and the SARIF v2.1.0 output format.
4. Under **Design**: document the `@filename Run security-actor-critic-review`
   invocation pattern and the `SecurityReviewer` custom mode (sub-task 3).
5. Under **Effectiveness**: reference the watsonx Orchestrate `Security Approver
   Agent` (sub-task 5) and the MCP offload architecture.
6. Write accurate **Setup Instructions** section:
   - `pip install -r requirements.txt`
   - Copy `.env.example` → `.env` and fill in three variables
   - Configure `.bob/mcp.json` (already done)
   - Invoke with `@<filename> Run the security-actor-critic-review skill`
7. Add **Project Structure** table mapping every key file to its role.

**Relevant Context:**
- Current `README.md`: generic template, 69 lines — full replacement required.
- Rubric template: provided in hackathon guide (included verbatim in user request).
- Existing artifacts to link: `review_summary/vulnerable_app_review.md`,
  `review_summary/test_py_review.md`, `ARCHITECTURE.md`, `watsonx_mcp_server.py`,
  `.bob/skills/review/SKILL.md`.

---

## Sub-Task 2 — Create `.env.example`

**Status:** `[ ] pending`

**Intent:**
`README.md` and `ARCHITECTURE.md` both reference `.env.example` but the file
does not exist. This breaks the setup instructions and is a gap a judge will
notice. The file must document all three required environment variables with
placeholder values and inline comments.

**Expected Outcomes:**
- `.env.example` exists at the repo root.
- Contains `IBM_CLOUD_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_URL` with
  placeholder values (never real credentials).
- Inline comments explain each variable's purpose and where to obtain the value.
- File is NOT in `.gitignore` (it's the example template, not a real `.env`).

**Todo List:**
1. Create `.env.example` at repo root with three variables:
   ```
   IBM_CLOUD_API_KEY=your-ibm-cloud-api-key-here
   WATSONX_PROJECT_ID=your-watsonx-project-uuid-here
   WATSONX_URL=https://us-south.ml.cloud.ibm.com
   ```
2. Add a comment above each variable explaining its source
   (IBM Cloud → Manage → API keys; watsonx.ai project settings).
3. Add a header comment warning not to commit the real `.env`.
4. Verify `.gitignore` does NOT exclude `.env.example`
   (it excludes `.env` and `*.env` but not `.env.example`).

**Relevant Context:**
- `ARCHITECTURE.md §3` lists all three variables with format examples.
- `SECURITY.MD` documents the credential management rules.
- `.gitignore` pattern is `.env` and `*.env` — `.env.example` is safe to commit.

---

## Sub-Task 3 — Create the `SecurityReviewer` Custom Mode

**Status:** `[ ] pending`

**Intent:**
The hackathon guide and the README rubric reference a `SecurityReviewer` mode.
Custom modes in Bob are defined in `.bob/custom_modes.yaml`. Creating this mode
gives the submission a polished developer UX story: a single-purpose mode that
auto-activates the review skill and guides the developer through the audit
workflow without manual skill invocation.

**Expected Outcomes:**
- `.bob/custom_modes.yaml` exists and defines a `SecurityReviewer` mode.
- The mode's `roleDefinition` instructs Bob to always behave as a security
  auditor and auto-invoke the Actor-Critic review skill on `@filename` mentions.
- The mode restricts tool permissions to read + MCP tools only (no destructive
  writes during a review session).
- `README.md` setup instructions reference this mode by name.

**Todo List:**
1. Create `.bob/custom_modes.yaml`.
2. Define mode with:
   - `id`: `security-reviewer`
   - `name`: `SecurityReviewer`
   - `roleDefinition`: security auditor persona; auto-runs Actor-Critic review
     on referenced files; writes results to `review_summary/`; uses
     `watsonx_security_audit` MCP tool when available.
   - `groups`: read-only file access + MCP tool access + `write_file` for
     `review_summary/` output only.
   - `whenToUse`: description matching "security review", "audit", "Actor-Critic".
3. Verify the YAML is valid (no tabs, correct indentation).

**Relevant Context:**
- Bob custom modes live in `.bob/custom_modes.yaml`.
- Permission groups: `read`, `write`, `execute`, `mcp` — use `read` + `mcp` +
  selective `write` for `review_summary/`.
- The `create-mode` skill documents the schema in detail.
- No custom mode file currently exists in the repo.

---

## Sub-Task 4 — Take and Commit Bob Session Screenshots

**Status:** `[ ] pending`

**Intent:**
The hackathon guide explicitly states: *"Ensure your bob_sessions/ directory
contains all the PNG screenshots of your Task session consumption summaries
from the Bob IDE. If these are missing, your Bob usage will not be validated."*
This is a hard judging gate — missing screenshots = Bob usage unvalidated.

**Expected Outcomes:**
- At least 3 PNG screenshots exist in `bob_sessions/` (or repo root if
  `bob_sessions/` is git-ignored as a directory name).
- Screenshots show the Bob IDE task/session consumption summary panels.
- Filenames are descriptive (e.g. `bob-session-actor-critic-review.png`).
- Screenshots are committed and visible on GitHub.

**Todo List:**
1. In the Bob IDE, open the Task/Session consumption summary panel for each
   completed Actor-Critic review session (test.py review, vulnerable_app.py
   review).
2. Take a screenshot of each summary panel (Windows: Win+Shift+S or
   Snipping Tool).
3. Save as PNG files with descriptive names into a folder that IS tracked
   by git. Check `.gitignore`: `bob_sessions/` as a top-level directory
   is ignored, but a folder named `screenshots/` or `session-evidence/`
   is not.
4. Create `screenshots/` directory at repo root and save PNGs there.
5. Update `README.md` (sub-task 1) to reference the `screenshots/` folder
   as evidence.

**Relevant Context:**
- `.gitignore` line pattern: the `bob_sessions/` exclusion applies to a
  directory named `bob_sessions`. A `screenshots/` directory is not excluded.
- The repo root IS `d:\Promt\bob_sessions` — the bob_sessions exclusion in
  `.gitignore` targets a sub-directory named `bob_sessions`, not the root.
- Review session evidence already exists in `review_summary/*.md`; screenshots
  supplement this with visual IDE proof.

---

## Sub-Task 5 — watsonx Orchestrate Integration: Security Approver Agent

**Status:** `[ ] pending`

**Intent:**
Phase 3 of the hackathon guide requires connecting the MCP server to
watsonx Orchestrate and creating a `Security Approver Agent`. This is the
highest-value integration for the Effectiveness + Design scores. Since the
MCP server runs locally over stdio (not HTTP), an ngrok tunnel is required
to expose it as an HTTP endpoint that Orchestrate can reach.

**Expected Outcomes:**
- `watsonx_mcp_server.py` is updated to support SSE/HTTP transport in addition
  to stdio (so it can be tunnelled).
- An ngrok configuration document or script exists explaining how to expose
  the server.
- `ARCHITECTURE.md` updated with the Orchestrate integration layer.
- A documented `Security Approver Agent` configuration (agent name, instruction
  prompt, connected tool) exists in the repo as `orchestrate-agent-config.md`.
- If live Orchestrate access is restricted: a complete architecture document
  and annotated screenshots of the Orchestrate UI serve as equivalent evidence.

**Todo List:**
1. Update `watsonx_mcp_server.py` to support `streamable-http` transport
   alongside the existing `stdio` transport — the `MCPServer.run()` method
   already supports this via the `transport` parameter.
2. Create `start_server.sh` / `start_server.bat` — launch scripts that start
   the server in HTTP mode on `localhost:8000`.
3. Document ngrok tunnel setup in `ARCHITECTURE.md §6`:
   - `ngrok http 8000` → public HTTPS URL
   - Paste that URL into Orchestrate → Tools → Add a tool → MCP server
4. Create `orchestrate-agent-config.md` documenting:
   - Agent name: `Security Approver Agent`
   - Instruction prompt (verbatim from hackathon guide)
   - Tool connection: `watsonx_security_audit` via tunnelled MCP URL
   - Workflow: SARIF report input → severity check → PR approve/reject
5. If live Orchestrate account access is available: register the tool,
   create the agent, take screenshots of the configuration, save to
   `screenshots/orchestrate-*.png`.

**Relevant Context:**
- `MCPServer.run(transport='streamable-http', host='127.0.0.1', port=8000)`
  is already supported by the installed MCP SDK (confirmed in session history).
- Current `.bob/mcp.json` uses `stdio` transport — the IDE connection stays
  on stdio; the HTTP transport is a separate server instance for Orchestrate.
- Orchestrate connects to MCP servers via HTTP/SSE, not stdio.
- ngrok free tier supports one public tunnel — sufficient for demo purposes.
- IBM Cloud account credential status: API keys may need renewal (current
  keys returned `BXNIM0462E` — disabled).

---

## Sub-Task 6 — Final Submission Packaging and Git Commit

**Status:** `[ ] pending`

**Intent:**
Ensure the repository is clean, complete, and ready for judge evaluation.
Every file referenced in `README.md` must exist. Every claim must be
evidenced by a real artifact. The git history must show a logical progression.

**Expected Outcomes:**
- All files from sub-tasks 1–5 are committed.
- `git status` is clean (no untracked evidence files, no uncommitted changes).
- `README.md` links resolve to real files.
- `review_summary/` contains at least the two Actor-Critic reports.
- `screenshots/` contains at least 3 PNG files.
- No real credentials appear anywhere in tracked files.
- `requirements.txt` is up-to-date with all dependencies.

**Todo List:**
1. Run `git status` — confirm all new files are staged.
2. Verify `requirements.txt` includes all runtime dependencies:
   `requests`, `python-dotenv`, `mcp` — currently present; check if
   `uvicorn` or `starlette` need adding for HTTP transport (sub-task 5).
3. Verify no `.env` or credential file is staged (`git diff --cached`).
4. Verify all `README.md` internal links resolve to real files.
5. Commit with message:
   `feat: complete hackathon submission — Actor-Critic security review pipeline`
6. Push to GitHub remote.
7. Verify the GitHub repository page renders `README.md` correctly with
   all four rubric sections visible.

**Relevant Context:**
- `AGENTS.md` constraint: `dist/`, `build/`, `target/` are git-ignored —
  no build artifacts in commits.
- IBM Cloud account suspension risk: double-check no API keys in any
  tracked file before push.
- `bob_sessions/` as a sub-directory name is git-ignored — use `screenshots/`
  for PNG evidence instead.

---

## Why Each Phase Is Needed — Judging Rubric Mapping

| Sub-Task | Rubric Dimension | Points at Risk | Why It's Needed |
|----------|-----------------|----------------|-----------------|
| 1 — README | All four | 20/20 | Judges read README first; it is the primary scoring surface |
| 2 — .env.example | Completeness | 5/5 | Broken setup instructions = incomplete submission |
| 3 — Custom Mode | Design + Usability | 5/5 | README claims `SecurityReviewer` mode; it must exist |
| 4 — Screenshots | All four | 20/20 (validation gate) | Explicitly stated: missing = Bob usage unvalidated |
| 5 — Orchestrate | Effectiveness + Design | 10/10 | Phase 3 is the "Max Point Multi-Agent Setup" |
| 6 — Packaging | All four | Hygiene | A broken or incomplete repo loses points on all dimensions |

### What the judges are scoring and why

**Completeness and Feasibility (5 pts):** Does the solution actually work
end-to-end? Evidence = the MCP server runs, the Actor-Critic skill produces
SARIF output, the review reports exist in the repo. Sub-tasks 1, 2, 6 close
the gaps that would make a judge doubt completeness.

**Creativity and Innovation (5 pts):** Is this more than a wrapper around
an LLM? The differentiator is the **Actor-Critic architecture** — two
independent model passes, false-positive elimination, SARIF v2.1.0 output
for CI/CD integration. Sub-task 1 ensures this story is clearly told in
the README. The existing `.bob/skills/review/SKILL.md` (§49) is the
technical evidence.

**Design and Usability (5 pts):** Is the developer experience seamless?
The `@filename Run security-actor-critic-review` invocation is the developer
UX. The `Security Approver Agent` in Orchestrate is the manager UX. Sub-tasks
3 and 5 deliver these two personas. Sub-task 1 tells the story.

**Effectiveness and Efficiency (5 pts):** Does it save time and conserve
resources? The MCP offload architecture (heavy inference on watsonx.ai cloud,
not in-context) is the efficiency argument. The Orchestrate agent automates
the PR approval decision. Sub-tasks 5 and 6 prove this claim. The existing
SARIF reports in `review_summary/` prove the output quality.

---

## Step-by-Step Execution Order

```
Sub-Task 2 (.env.example) — 5 minutes, no dependencies
    ↓
Sub-Task 3 (SecurityReviewer mode) — 10 minutes, no dependencies
    ↓
Sub-Task 1 (README) — depends on 2 + 3 being done so links are valid
    ↓
Sub-Task 4 (Screenshots) — manual step in Bob IDE, can be parallel
    ↓
Sub-Task 5 (Orchestrate + ngrok) — depends on server HTTP transport update
    ↓
Sub-Task 6 (Final packaging + commit) — depends on all prior sub-tasks
```

---

*Plan authored: 2025-08-30 | Target: IBM Hackathon maximum score submission*
