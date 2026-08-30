# Bob Session Screenshots — Evidence Folder

This directory holds screenshots and screen recordings documenting Bob IDE usage
and the WatsonxCritic pipeline running end-to-end. These are required by the
hackathon judging rubric to validate Bob usage throughout development.

## Screenshots Present

| Filename | What it shows |
|----------|----------------|
| `bob-session-vulnerable-app-review.jpeg` | Bob task session — `vulnerable_app.py` Actor-Critic security review |
| `bob-session-test-py-review.png` | Bob task session — `test.py` Actor-Critic security review |
| `Mcp_server.png` | MCP server registered and active in Bob IDE |
| `Behaviourl.jpeg` | watsonx Orchestrate Security Approver Agent behaviour screen |
| `Tools in watsonxCritic copy 2.jpeg` | watsonx Orchestrate — `watsonx_security_audit` tool registered |
| `Agent_test.jpeg` | watsonx Orchestrate — Agent responding with PR REJECTED decision |
| `Test resul of agent.jpeg` | watsonx Orchestrate — Agent test result output |

## How These Were Captured

### Bob IDE sessions (Windows)

1. Completed a task in Bob IDE (SecurityReviewer mode)
2. Opened the **Task** panel in the left sidebar and clicked the completed task
3. The consumption summary shows token usage, tool calls, and time elapsed
4. Captured with **Win + Shift + S** (Snipping Tool)
5. Saved into this directory

### watsonx Orchestrate screens

1. Logged into IBM Cloud → launched the watsonx Orchestrate instance
2. Navigated to the Security Approver Agent and Tools screens
3. Captured with **Win + Shift + S** (Snipping Tool)
4. Saved into this directory

## What Each Screenshot Proves

| Screenshot | Judging rubric evidence |
|---|---|
| `bob-session-vulnerable-app-review.jpeg` | Bob was actively used to run the Actor-Critic review skill on `vulnerable_app.py` |
| `bob-session-test-py-review.png` | Bob was actively used to run the Actor-Critic review skill on `test.py` |
| `Mcp_server.png` | The `watsonx_security_audit` MCP tool is registered in Bob IDE and callable |
| `Tools in watsonxCritic copy 2.jpeg` | The MCP tool is discoverable inside watsonx Orchestrate |
| `Behaviourl.jpeg` | The Security Approver Agent is configured with its instruction persona |
| `Agent_test.jpeg` | Live end-to-end test: agent received a SQL-injection diff and responded PR REJECTED |
| `Test resul of agent.jpeg` | Confirms the REJECT output with CWE-89 reasoning from IBM Granite |

## Supplementary evidence

The full written Actor-Critic outputs are also committed in [`review_summary/`](../review_summary/):
- `vulnerable_app_review.md` — full Actor-Critic report for `vulnerable_app.py`
- `test_py_review.md` — full Actor-Critic report for `test.py`
- `requirements_txt_review.md` — dependency audit report

These Markdown reports supplement the screenshots.
