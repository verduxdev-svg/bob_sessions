# IBM Bob Task Session Summary Screenshots — Capture Guide

> **This document is required reading for the hackathon submission.**
> The judges specifically require screenshots of IBM Bob **task session summaries** —
> the panel inside Bob IDE that shows completed tasks with tool call logs,
> token usage, and elapsed time. These are distinct from screenshots of the
> output files Bob produced.

---

## What a Bob Task Session Summary Looks Like

A task session summary is captured from the **Tasks panel** in the Bob IDE
left sidebar. It shows:

- The task title and timestamp
- A list of every **tool call** Bob made during the task (e.g., `read_file`,
  `use_skill`, `mcp__watsonx-critic__watsonx_security_audit`, `write_file`)
- **Token consumption** (input tokens, output tokens)
- **Elapsed time** for the session
- The final response or a link to the artifact produced

This is the evidence the judges need to verify that **IBM Bob was actively used**
to build the project — not just that outputs exist.

---

## Step-by-Step: How to Capture a Bob Task Session Summary

### In Bob IDE (Windows)

1. **Open Bob IDE** and make sure you are in the workspace where you ran
   the security reviews (`d:\Promt\bob_sessions`).

2. **Click the Tasks icon** in the left sidebar (clock/history icon).
   This opens the Tasks panel listing all previous sessions.

3. **Click on a completed task** — for example the session where you ran
   `@vulnerable_app.py Run the security-actor-critic-review skill`.

4. The task expands to show:
   - The user prompt at the top
   - Each tool call as a collapsible row (e.g., `read_file`, `use_skill`,
     `mcp__watsonx-critic__watsonx_security_audit`, `write_file`)
   - Token usage summary at the bottom
   - Elapsed time

5. **Scroll to the bottom** of the task to see the full consumption summary.

6. **Take a screenshot:**
   - Press **Win + Shift + S** → select the Bob IDE window
   - Or open **Snipping Tool** (search in Start menu)
   - Capture the full Tasks panel including the task title, tool call list,
     and the token/time summary at the bottom

7. **Save the file** as a PNG into the `screenshots/` directory:
   - `screenshots/bob-task-session-vulnerable-app.png`
   - `screenshots/bob-task-session-test-py.png`
   - `screenshots/bob-task-session-mcp-server-build.png`

8. **Commit and push:**
   ```bash
   git add screenshots/
   git commit -m "chore: add Bob task session summary screenshots"
   git push origin main
   ```

---

## Which Sessions to Capture

Capture a task session summary for each of the following:

| Screenshot filename | Task to find in the Tasks panel |
|---|---|
| `screenshots/bob-task-session-vulnerable-app.png` | The session where `@vulnerable_app.py` was reviewed — output is `review_summary/vulnerable_app_review.md` |
| `screenshots/bob-task-session-test-py.png` | The session where `@test.py` was reviewed — output is `review_summary/test_py_review.md` |
| `screenshots/bob-task-session-mcp-server-build.png` | The session where `watsonx_mcp_server.py` was implemented or modified |
| `screenshots/bob-task-session-skill-build.png` | The session where `.bob/skills/review/SKILL.md` was authored *(optional but strong evidence)* |

---

## What the Judges Check For

The hackathon rubric checks:

> *"Your code repository includes IBM Bob task session summary screenshots that
> clearly document how IBM Bob was used throughout the development process."*

A passing submission must show:

1. ✅ Bob was used in **Agent mode** (the task panel shows autonomous multi-step execution)
2. ✅ Bob called **real tools** during the session (`read_file`, `write_file`, MCP tools)
3. ✅ Bob produced **real output** that is committed in the repo
4. ✅ At least **one session per major deliverable** is evidenced

---

## Current Screenshot Status

| Screenshot | Type | Judges' requirement met? |
|---|---|---|
| `bob-session-vulnerable-app-review.jpeg` | Review **output** rendered in Bob preview panel | ⚠️ Partial — shows the report Bob wrote, not the task session summary |
| `bob-session-test-py-review.png` | Review **output** rendered in Bob preview panel | ⚠️ Partial — shows the report Bob wrote, not the task session summary |
| `Mcp_server.png` | Source code editor view of `watsonx_mcp_server.py` | ⚠️ Partial — shows the file Bob produced, not the task session |
| `Agent_test.jpeg` | watsonx Orchestrate agent live test result | ✅ Strong Orchestrate evidence |
| `Test resul of agent.jpeg` | watsonx Orchestrate agent output | ✅ Strong Orchestrate evidence |
| `Behaviourl.jpeg` | Orchestrate agent behaviour config screen | ✅ Orchestrate configuration evidence |
| `Tools in watsonxCritic copy 2.jpeg` | Orchestrate tools registration screen | ✅ Orchestrate MCP tool evidence |

**Action needed:** Add task session summary screenshots for the Bob IDE sessions
(the three items marked ⚠️ above need to be supplemented with task panel screenshots).

---

## What the Task Panel Screenshot Must Show

To satisfy the judges, the screenshot must be recognisably the Bob IDE with:

- The **task title** visible (the original user prompt or task name)
- At least **2–3 tool calls** visible in the collapsed/expanded list
- Ideally the **token usage** or **time elapsed** summary visible
- The **Bob IDE chrome** (sidebar, mode indicator) recognisable in the frame

The output files (`review_summary/*.md`, `watsonx_mcp_server.py`) serve as
**corroborating evidence** — they prove what Bob produced. The task session
screenshots prove Bob did the work.

---

*IBM watsonx Hackathon · WatsonxCritic · Bob Task Session Evidence Guide*
