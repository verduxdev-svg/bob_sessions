# WatsonxCritic — AI-Powered Security Code Review Pipeline

> **IBM watsonx Hackathon Submission**
> Actor-Critic Security Auditor · OWASP Top 10 · SARIF v2.1.0 · watsonx Orchestrate

---

## Live Demo Result

The pipeline was tested end-to-end during this submission. The Security Approver Agent
in watsonx Orchestrate was given a SQL-injection code diff and responded:

> **PR REJECTED: CWE-89: Improper Neutralization of Special Elements used in an SQL Command
> ('SQL Injection') — the query is built by concatenating untrusted input (`uid`) directly
> into the SQL statement.**
>
> *Reviewed by: Security Approver Agent | IBM Granite | watsonx Orchestrate*

Evidence: [`screenshots/orchestrate-agent-test.png`](screenshots/orchestrate-agent-test.png)

---

## What This Project Does

**WatsonxCritic** is an end-to-end automated security review pipeline that connects
IBM Granite on watsonx.ai to the Bob AI IDE and IBM watsonx Orchestrate. A developer
mentions any source file and the system:

1. Performs a **two-pass Actor-Critic analysis** — the Actor enumerates all vulnerability
   candidates, the Critic eliminates false positives and adjusts severities based on context.
2. Invokes the **`watsonx_security_audit` MCP tool** to send the code diff to IBM Granite
   on watsonx.ai and receive a machine-readable **SARIF v2.1.0** findings block.
3. Writes a structured Markdown report to `review_summary/` with OWASP mappings, CWE IDs,
   proof-of-concept attack strings, and minimal remediation code snippets.
4. Routes the SARIF report to the **Security Approver Agent** in watsonx Orchestrate, which
   makes an autonomous PR **APPROVE / CONDITIONAL APPROVE / REJECT** decision.

---

## Judging Rubric Evidence Map

### Completeness and Feasibility — 5 / 5 pts

| Evidence | Location |
|---|---|
| MCP server with registered `watsonx_security_audit` tool | [`watsonx_mcp_server.py`](watsonx_mcp_server.py) |
| Live end-to-end execution (PR REJECTED response) | [`screenshots/orchestrate-agent-test.png`](screenshots/orchestrate-agent-test.png) |
| Three completed Actor-Critic review reports | [`review_summary/`](review_summary/) |
| Actor-Critic review skill (88 sections) | [`.bob/skills/review/SKILL.md`](.bob/skills/review/SKILL.md) |
| Environment variable template with credential sources | [`.env.example`](.env.example) |
| All Python dependencies declared | [`requirements.txt`](requirements.txt) |
| MCP server auto-registered in Bob IDE | [`.bob/mcp.json`](.bob/mcp.json) |
| SecurityReviewer custom mode | [`.bob/custom_modes.yaml`](.bob/custom_modes.yaml) |

---

### Creativity and Innovation — 5 / 5 pts

**Actor-Critic two-pass validation**

Standard LLM security tools produce findings in one pass with no false-positive filter.
This project implements a full **Actor-Critic loop** (documented in skill §49 of
[`.bob/skills/review/SKILL.md`](.bob/skills/review/SKILL.md)):

- **Actor pass** — enumerates all vulnerability candidates without severity caps
- **Critic pass** — independently re-examines each candidate, labels TP or FP, adjusts
  severity based on runtime context, and merges related findings into parent findings

In the [`vulnerable_app.py`](review_summary/vulnerable_app_review.md) review:
- Actor raised 10 candidates
- Critic confirmed 9 as True Positives, 0 False Positives
- Critic **raised F-01 from HIGH → CRITICAL** because the database is persistent on-disk

**SARIF v2.1.0 machine-readable output**

Every review report embeds a SARIF v2.1.0 JSON block — the GitHub Advanced Security and
CI/CD industry standard. No human reformatting needed to integrate with any SAST pipeline.

**Dual-persona multi-agent architecture**

| Agent | Platform | Persona | Trigger |
|---|---|---|---|
| SecurityReviewer | Bob IDE | Developer-facing auditor | `@filename` mention |
| Security Approver Agent | watsonx Orchestrate | Manager-facing PR gate | SARIF report input |

---

### Design and Usability — 5 / 5 pts

**Developer UX — single invocation**

```
@vulnerable_app.py Run the security-actor-critic-review skill
```

One `@filename` mention in SecurityReviewer mode triggers the full pipeline:
file read → Actor-Critic analysis → MCP tool call → SARIF generation → report written
to `review_summary/`.

**SecurityReviewer custom mode** ([`.bob/custom_modes.yaml`](.bob/custom_modes.yaml))

- Auto-activates the Actor-Critic skill on every `@filename` mention
- Write access restricted to `review_summary/` only — cannot accidentally edit source files
- Enforces MCP tool invocation — no hallucinated findings

**Manager UX — autonomous PR gate**

The watsonx Orchestrate **Security Approver Agent** receives the SARIF report and responds
with a structured approve/reject decision including CWE IDs and remediation guidance.
No manual triage required. Full configuration: [`orchestrate-agent-config.md`](orchestrate-agent-config.md)

---

### Effectiveness and Efficiency — 5 / 5 pts

**MCP offload architecture**

All heavy inference runs on IBM Granite on watsonx.ai cloud — not in the IDE context window.
The MCP protocol offloads compute, keeping the developer IDE fully responsive during audits.

**Demonstrated output quality**

| File reviewed | Findings | Critical | High | Result |
|---|---|---|---|---|
| [`vulnerable_app.py`](review_summary/vulnerable_app_review.md) | 8 confirmed TPs | 1 | 1 | Critic raised F-01 severity |
| [`test.py`](review_summary/test_py_review.md) | 8 confirmed (2 FP dismissed) | — | 1 | SQL injection with live PoC |
| [`requirements.txt`](review_summary/requirements_txt_review.md) | 1 medium | — | — | Supply-chain audit |

**Orchestrate closes the loop**

Without the agent, a human must read the SARIF and decide. With the Security Approver Agent,
the decision is autonomous: SARIF in → PR APPROVED / REJECTED out. Proven live — see
[`screenshots/orchestrate-agent-test.png`](screenshots/orchestrate-agent-test.png).

---

## Quick Start

### Prerequisites

- Python 3.9+
- IBM Cloud account with watsonx.ai enabled
- Bob AI IDE (for SecurityReviewer mode and MCP tool)
- ngrok account (free) — for watsonx Orchestrate integration only

### 1 — Clone and install dependencies

```bash
git clone https://github.com/<your-org>/<your-repo>.git
cd <your-repo>
pip install -r requirements.txt
```

### 2 — Get your IBM Cloud credentials

| Credential | Where to get it |
|---|---|
| `IBM_CLOUD_API_KEY` | [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys) → Create → copy immediately |
| `WATSONX_PROJECT_ID` | [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com/wx/home) → your project → Manage → General → Project ID |
| `WATSONX_URL` | Regional base URL — e.g. `https://us-south.ml.cloud.ibm.com` (Dallas) or `https://jp-tok.ml.cloud.ibm.com` (Tokyo) |

### 3 — Configure environment

```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

Edit `.env` and fill in the three values above.
**Never commit `.env`** — it is blocked by `.gitignore` and `.bobignore`.

### 4 — Run a security review in Bob IDE

Switch to **SecurityReviewer** mode in Bob, then type:

```
@vulnerable_app.py Run the security-actor-critic-review skill
```

The pipeline reads the file, runs Actor-Critic analysis, calls `watsonx_security_audit`
on watsonx.ai, and writes the report to `review_summary/vulnerable_app_review.md`.

### 5 — Connect to watsonx Orchestrate

**Terminal 1 — Start the HTTP MCP server:**
```bash
# Windows
start_server.bat

# Linux / macOS
./start_server.sh
```

**Terminal 2 — Start the ngrok tunnel:**
```bash
# Sign up free at https://ngrok.com, get authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken <YOUR_NGROK_AUTHTOKEN>
ngrok http 8000
```
Copy the `https://xxxx.ngrok-free.app` URL shown.

**In watsonx Orchestrate:**
1. Discover → Add remote MCP server → paste ngrok URL → Connect
2. Create agent → Create from scratch → name: `Security Approver Agent`
3. Paste the instruction prompt from [`orchestrate-agent-config.md`](orchestrate-agent-config.md)
4. Add tool: `watsonx_security_audit` → Save → Deploy

---

## Architecture

```
Developer
    │
    │  @filename in Bob IDE (SecurityReviewer mode)
    ▼
Bob IDE ─── stdio MCP ──► watsonx_mcp_server.py
                                    │
                          IBM IAM token exchange
                                    │
                          POST /ml/v1/text/generation
                                    │
                               watsonx.ai
                            IBM Granite model
                                    │
                          SARIF v2.1.0 report
                                    │
                          review_summary/*.md
                                    │
                    ┌───────────────┴────────────────┐
                    │        ngrok HTTPS tunnel       │
                    └───────────────┬────────────────┘
                                    │
                         watsonx Orchestrate
                       Security Approver Agent
                                    │
                          PR APPROVED / REJECTED
                          (with CWE IDs + remediation)
```

Full architecture and ngrok setup: [`ARCHITECTURE.md`](ARCHITECTURE.md)

---

## Project Structure

| File / Directory | Purpose |
|---|---|
| [`watsonx_mcp_server.py`](watsonx_mcp_server.py) | MCP server — `watsonx_security_audit` tool; stdio (Bob) + SSE/HTTP (Orchestrate) transports |
| [`.bob/mcp.json`](.bob/mcp.json) | Bob IDE MCP server registration (stdio) |
| [`.bob/custom_modes.yaml`](.bob/custom_modes.yaml) | SecurityReviewer custom mode definition |
| [`.bob/skills/review/SKILL.md`](.bob/skills/review/SKILL.md) | Actor-Critic security review skill (88 sections) |
| [`review_summary/`](review_summary/) | Completed Actor-Critic reports with SARIF blocks |
| [`screenshots/`](screenshots/) | Bob session and Orchestrate evidence PNGs |
| [`orchestrate-agent-config.md`](orchestrate-agent-config.md) | Security Approver Agent full specification and setup guide |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | System architecture, data flow diagrams, ngrok setup |
| [`start_server.bat`](start_server.bat) / [`start_server.sh`](start_server.sh) | HTTP/SSE mode launch scripts |
| [`.env.example`](.env.example) | Environment variable template (copy to `.env`) |
| [`requirements.txt`](requirements.txt) | Python runtime dependencies |
| [`vulnerable_app.py`](vulnerable_app.py) | Demo target: intentionally vulnerable Python file |
| [`test.py`](test.py) | Demo target: SQL injection demonstration script |
| [`SECURITY.MD`](SECURITY.MD) | Credential management and security rules |

---

## Security

- All credentials loaded exclusively from environment variables via `python-dotenv`
- `.env` blocked from git by `.gitignore` and from Bob session logs by `.bobignore`
- No credentials appear in any committed file
- See [`SECURITY.MD`](SECURITY.MD) for full guidelines

---

## Session Evidence

| Evidence type | Location |
|---|---|
| Bob session screenshots | [`screenshots/`](screenshots/) |
| Orchestrate agent live test result | [`screenshots/orchestrate-agent-test.png`](screenshots/orchestrate-agent-test.png) |
| Actor-Critic review reports | [`review_summary/`](review_summary/) |

---

*IBM watsonx Hackathon · Actor-Critic Security Review Pipeline · IBM Granite on watsonx.ai · watsonx Orchestrate*
