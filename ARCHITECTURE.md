# Architecture: Watsonx MCP Security Auditor

## §1 — System Overview

This project wires the Bob IDE to IBM Watsonx.ai through the Model Context Protocol (MCP).
`watsonx_mcp_server.py` runs as a local MCP server over stdio transport; Bob discovers and
invokes its tools as if they were native IDE capabilities. When a tool is called, the server
exchanges an IBM Cloud API key for a short-lived IAM Bearer token, then forwards the request
to the Watsonx.ai text generation API using the IBM Granite 3 8B Instruct model. The response
— a Markdown security report with an embedded SARIF v2.1.0 JSON block — is returned directly
to the Bob IDE.

**Components:**

| Component | Role |
|---|---|
| **Bob IDE** | Invokes registered MCP tools; receives and displays results |
| **MCP stdio transport** | Bidirectional JSON-RPC channel between Bob and the server process |
| **`watsonx_mcp_server.py`** | MCP server; houses tool definitions and API orchestration |
| **IBM IAM token endpoint** | `https://iam.cloud.ibm.com/identity/token` — exchanges API key for Bearer token |
| **Watsonx.ai text generation API** | `POST /ml/v1/text/generation` — runs inference on IBM Granite 3 8B Instruct |

---

## §2 — Data Flow

```
1. Bob IDE
   └─ invokes registered MCP tool, e.g. watsonx_security_audit(code_diff="...")
          │
          │  stdio (JSON-RPC)
          ▼
2. watsonx_mcp_server.py
   └─ receives code_diff argument
          │
          │  POST https://iam.cloud.ibm.com/identity/token
          │       grant_type=apikey  &  apikey=<IBM_CLOUD_API_KEY>
          ▼
3. IBM IAM token endpoint
   └─ returns short-lived Bearer token (TTL: 60 min)
          │
          │  POST <WATSONX_URL>/ml/v1/text/generation?version=2023-05-29
          │       Authorization: Bearer <token>
          │       model_id: ibm/granite-3-8b-instruct
          │       project_id: <WATSONX_PROJECT_ID>
          │       input: OWASP audit prompt + code_diff
          ▼
4. Watsonx.ai text generation API
   └─ returns generated_text (Markdown report + SARIF v2.1.0 JSON block)
          │
          │  stdio (JSON-RPC response)
          ▼
5. Bob IDE
   └─ displays Markdown report and SARIF findings inline
```

---

## §3 — Environment Variables

All credentials must be loaded from environment variables. Copy `.env.example` to `.env`
and fill in your values. **Never hardcode credentials in source files.**

| Variable | Purpose | Format / Example |
|---|---|---|
| `IBM_CLOUD_API_KEY` | Authenticates with IBM IAM to obtain a Bearer token | IBM Cloud API key string, e.g. `abc123...` |
| `WATSONX_PROJECT_ID` | Identifies the Watsonx.ai project for billing and model access | UUID, e.g. `a1b2c3d4-...` |
| `WATSONX_URL` | Base URL of the Watsonx.ai regional endpoint | e.g. `https://us-south.ml.cloud.ibm.com` |

See [`SECURITY.MD`](SECURITY.MD) for credential management rules and [``.env.example``](.env.example)
for the template.

---

## §4 — Current Tool Inventory

### `watsonx_security_audit(code_diff: str) -> str`

**Source:** [`watsonx_mcp_server.py:22`](watsonx_mcp_server.py)

Accepts a code diff (plain text) and submits it to IBM Granite 3 8B Instruct with an
OWASP Top 10 security audit prompt. Returns a single string containing:

- A **Markdown summary** of findings with severity classifications
- A **SARIF v2.1.0 JSON block** suitable for ingestion by code-scanning tools

**Authentication:** calls `get_iam_token()` on every invocation — no caching currently.

---

## §5 — Growth Roadmap

### Tier 1 — Short-term (single session additions)

Small, self-contained additions that do not require restructuring the project.

| Addition | Description |
|---|---|
| `watsonx_code_explain` tool | Explains selected code in plain English; useful for onboarding and code review |
| `watsonx_fix_suggestion` tool | Asks Watsonx.ai to produce a corrected version of a flagged snippet |
| IAM token caching | Cache the Bearer token in memory for its 60-minute TTL; avoids a round-trip to IAM on every tool call |

### Tier 2 — Medium-term (project structure)

Refactors and CI additions that improve maintainability and testability.

| Addition | Description |
|---|---|
| Module split | `server.py` (MCP wiring) · `watsonx_client.py` (API calls) · `iam.py` (token management) |
| `pytest` test suite | Unit tests with mocked HTTP (`responses` or `httpretty`); no real API key needed in CI |
| GitHub Actions workflow | `pip install -r requirements.txt && pytest` on every push and PR |

> **Note:** Do not commit build artifacts to `dist/`, `build/`, or `target/` — these directories
> are git-ignored per [`AGENTS.md`](AGENTS.md). CI must not produce or persist output there.

### Tier 3 — Long-term (production hardening)

Additions for reliability, auditability, and deeper GitHub integration.

| Addition | Description |
|---|---|
| Token refresh background task | Replace per-call IAM polling with a background thread that refreshes the token proactively before expiry |
| SARIF file writer | Persist audit reports to a `reports/` directory for post-session review and trend tracking |
| `watsonx_batch_audit` tool | Accepts multiple diffs; aggregates and deduplicates SARIF results across all changed files |
| GitHub Actions PR integration | Trigger the MCP audit on every PR via `gh` CLI; post SARIF results as PR annotations |

---

## §6 — watsonx Orchestrate Integration (Security Approver Agent)

This section describes the extended architecture that connects the local MCP server to IBM
watsonx Orchestrate via an ngrok tunnel, enabling a manager-persona autonomous agent to make
PR approval/rejection decisions based on SARIF output.

### Transport Layer Duality

The server supports two transports via the `--http` flag:

| Transport | Command | Used By |
|---|---|---|
| `stdio` (default) | `python watsonx_mcp_server.py` | Bob IDE via `.bob/mcp.json` |
| `streamable-http` | `python watsonx_mcp_server.py --http` | ngrok → watsonx Orchestrate |

### Orchestrate Integration Data Flow

```
Developer submits PR diff
       │
       ▼
Bob IDE (SecurityReviewer mode)
  └─ watsonx_security_audit(code_diff)  ← MCP stdio
       │
       ▼
watsonx_mcp_server.py  ← starts on port 8000 in HTTP mode
       │
       ▼
ngrok tunnel (ngrok http 8000)
  └─ https://<subdomain>.ngrok-free.app  ← public HTTPS endpoint
       │
       ▼
watsonx Orchestrate — Tool Registry
  └─ watsonx_security_audit tool registered via MCP server URL
       │
       ▼
Security Approver Agent (IBM Granite model in Orchestrate)
  └─ Instruction: "Review SARIF. If HIGH/CRITICAL → REJECT. If mitigated → APPROVE."
       │
       ▼
PR Decision: APPROVED / CONDITIONALLY APPROVED / REJECTED
  └─ Notification sent to developer with finding details
```

### ngrok Setup (step-by-step)

1. **Download ngrok:** https://ngrok.com/download  
2. **Create free account:** https://dashboard.ngrok.com  
3. **Authenticate:**
   ```bash
   ngrok config add-authtoken <YOUR_NGROK_AUTHTOKEN>
   ```
   Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken

4. **Start the HTTP MCP server** (Terminal 1):
   ```bash
   # Windows
   start_server.bat

   # Linux / macOS
   ./start_server.sh
   ```

5. **Start the tunnel** (Terminal 2):
   ```bash
   ngrok http 8000
   ```
   Note the public URL, e.g. `https://abc123.ngrok-free.app`

6. **Register in watsonx Orchestrate:**
   - Discover → Tools → Add a tool → MCP server
   - URL: `https://abc123.ngrok-free.app`
   - Transport: Streamable HTTP (SSE)
   - The `watsonx_security_audit` tool will be auto-discovered

### Security Approver Agent Configuration

Full agent specification including the instruction prompt, tool connection steps, and test
invocation examples are documented in [`orchestrate-agent-config.md`](orchestrate-agent-config.md).

**Agent name:** `Security Approver Agent`  
**Model:** IBM Granite (Orchestrate default)  
**Tool:** `watsonx_security_audit` (connected via ngrok tunnel)  
**Decision logic:**
- 🔴 CRITICAL or HIGH findings → **PR REJECTED** — developer notified with finding list
- 🟠 MEDIUM only → **CONDITIONAL APPROVAL** — follow-up tickets required
- 🟡 LOW / INFO only → **PR APPROVED**

