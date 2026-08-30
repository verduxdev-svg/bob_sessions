# Bob Session Screenshots — Evidence Folder

This directory holds PNG screenshots of Bob IDE task/session consumption summaries.
These screenshots are required by the hackathon judging rubric to validate Bob usage.

## Required Screenshots

Add the following screenshots to this directory:

| Filename | What to capture |
|----------|----------------|
| `bob-session-vulnerable-app-review.png` | Bob task summary for the `vulnerable_app.py` Actor-Critic review session |
| `bob-session-test-py-review.png` | Bob task summary for the `test.py` Actor-Critic review session |
| `bob-session-mcp-server-build.png` | Bob task summary for the MCP server implementation session |
| `orchestrate-tool-registration.png` | watsonx Orchestrate — Tool registration screen showing `watsonx_security_audit` connected |
| `orchestrate-agent-config.png` | watsonx Orchestrate — Security Approver Agent configuration screen |
| `orchestrate-agent-test.png` | watsonx Orchestrate — Agent responding to a test PR diff (approve/reject output) |

## How to Take Screenshots in Bob IDE (Windows)

1. Complete a task in Bob IDE
2. Open the **Task** panel (left sidebar) and click on the completed task
3. The consumption summary shows token usage, tool calls, and time elapsed
4. Press **Win + Shift + S** or open **Snipping Tool**
5. Select the Bob IDE window showing the task summary
6. Save as PNG with the filename from the table above
7. Place the PNG file in this `screenshots/` directory
8. Commit with: `git add screenshots/*.png && git commit -m "chore: add Bob session evidence screenshots"`

## How to Take Screenshots of watsonx Orchestrate

1. Log in to IBM Cloud: https://cloud.ibm.com
2. Launch your watsonx Orchestrate instance from the Resource List
3. Navigate to each screen listed in the table above
4. Press **Win + Shift + S** (Windows) or **Cmd + Shift + 4** (macOS)
5. Save PNGs with the filenames above into this directory

## Note

The review session evidence also exists as Markdown files in [`review_summary/`](../review_summary/):
- `vulnerable_app_review.md` — full Actor-Critic report for `vulnerable_app.py`
- `test_py_review.md` — full Actor-Critic report for `test.py`
- `requirements_txt_review.md` — dependency audit report

These Markdown reports supplement (but do not replace) the required PNG screenshots.
