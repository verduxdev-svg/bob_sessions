import os, requests
from pathlib import Path
from dotenv import load_dotenv

# Load credentials the same way watsonx_mcp_server.py does
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env")

API_KEY    = os.getenv("IBM_CLOUD_API_KEY")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
BASE_URL   = os.getenv("WATSONX_URL")
MODEL_ID   = "ibm/granite-4-h-small"

assert API_KEY,    "IBM_CLOUD_API_KEY not set"
assert PROJECT_ID, "WATSONX_PROJECT_ID not set"
assert BASE_URL,   "WATSONX_URL not set"

def get_token():
    r = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={API_KEY}"
    )
    r.raise_for_status()
    return r.json()["access_token"]

def call_watsonx(token, prompt, max_tokens=2000):
    r = requests.post(
        f"{BASE_URL}/ml/v1/text/generation?version=2023-05-29",
        headers={"Content-Type": "application/json",
                 "Accept": "application/json",
                 "Authorization": f"Bearer {token}"},
        json={
            "input": prompt,
            "parameters": {"decoding_method": "greedy",
                           "max_new_tokens": max_tokens,
                           "min_new_tokens": 20},
            "model_id": MODEL_ID,
            "project_id": PROJECT_ID
        }
    )
    r.raise_for_status()
    return r.json()["results"][0]["generated_text"]

CODE = open("test.py", encoding="utf-8").read()

# ── ACTOR ────────────────────────────────────────────────────────────────────
ACTOR_PROMPT = f"""You are a senior application security engineer performing a thorough OWASP Top 10 and CWE code review.

Analyse the Python file below exhaustively across ALL dimensions:
- Injection (SQL, command, log, etc.)
- Sensitive data / credential exposure
- Cryptographic failures
- Security misconfiguration
- Error handling and information leakage
- Code correctness (runtime errors, missing imports, type mismatches)
- Data-flow: trace every untrusted input from source to sink

For EACH finding output EXACTLY this block (no extra text between findings):

Finding ID: F-xx
Vulnerability: <name>
OWASP: <category and code e.g. A03:2021 - Injection>
CWE: <CWE-xxx>
Severity: Critical | High | Medium | Low | Info
Confidence: Confirmed | High | Medium | Low
Lines: <line numbers>
Description: <what is wrong and why it matters>
PoC: <how an attacker or the runtime triggers this>
Fix: <concrete corrected code snippet>

Be exhaustive — include correctness issues, not just security issues.

```python
{CODE}
```
"""

# ── CRITIC ───────────────────────────────────────────────────────────────────
CRITIC_PROMPT_TPL = """You are a rigorous security peer-reviewer (the Critic). Challenge every finding from the Actor below.

For each finding:
1. Decide: TRUE POSITIVE or FALSE POSITIVE — give your reasoning.
2. If TRUE POSITIVE: confirm or adjust severity (raise/lower/keep) with justification.
3. If FALSE POSITIVE: explain why it is not present or not exploitable.
4. If the fix is incomplete, provide a better one.

Format each response as:
[F-xx] TP/FP | Severity: keep <X> | OR raise to <X> | OR lower to <X> | Notes: <reasoning>

After all findings, add:
## Missed Findings
List any real vulnerabilities the Actor overlooked, with the same Finding ID format starting at F-xx+1.

Actor Findings:
---
{actor}
---

Code under review:
```python
{code}
```
"""

print("=== Getting IAM token ===", flush=True)
token = get_token()
print("Token OK\n", flush=True)

print("=== ACTOR PASS ===", flush=True)
actor = call_watsonx(token, ACTOR_PROMPT, max_tokens=2000)
print(actor, flush=True)

print("\n\n=== CRITIC PASS ===", flush=True)
critic = call_watsonx(token, CRITIC_PROMPT_TPL.format(actor=actor, code=CODE), max_tokens=2000)
print(critic, flush=True)

with open(".bob/tmp/ac2_actor.txt", "w", encoding="utf-8") as f:
    f.write(actor)
with open(".bob/tmp/ac2_critic.txt", "w", encoding="utf-8") as f:
    f.write(critic)

print("\nDONE", flush=True)
