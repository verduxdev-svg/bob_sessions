import requests, sys

TOKEN_URL  = 'https://iam.cloud.ibm.com/identity/token'
WATSONX_URL = 'https://us-south.ml.cloud.ibm.com'
API_KEY    = '2YYihLJxrxnb8ZgIW5WCx6A05TBWi1oz2DQ7InbjDYyA'
PROJECT_ID = '778c398d-aa2f-42e2-b69f-dbd659038628'
MODEL_ID   = 'ibm/granite-4-h-small'

def get_token():
    r = requests.post(TOKEN_URL,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data='grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=' + API_KEY)
    r.raise_for_status()
    return r.json()['access_token']

def call_watsonx(token, prompt, max_tokens=2000):
    r = requests.post(
        WATSONX_URL + '/ml/v1/text/generation?version=2023-05-29',
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + token},
        json={
            "input": prompt,
            "parameters": {"decoding_method": "greedy", "max_new_tokens": max_tokens, "min_new_tokens": 20},
            "model_id": MODEL_ID,
            "project_id": PROJECT_ID
        })
    r.raise_for_status()
    return r.json()['results'][0]['generated_text']

CODE = open('test.py').read()

# ── ACTOR ────────────────────────────────────────────────────────────────────
ACTOR_PROMPT = f"""You are a senior application security engineer performing a thorough OWASP Top 10 code review.

Analyse this Python file exhaustively. Cover ALL of these dimensions:
- Injection (SQL, command, etc.)
- Broken Authentication / Credential exposure
- Sensitive data exposure
- Security misconfiguration
- Cryptographic failures
- Error handling / information leakage
- Code correctness (runtime errors, import issues)
- Data-flow: trace every untrusted input source to every sink

For EACH finding output EXACTLY this structure:
Finding ID: F-xx
Vulnerability: <name>
OWASP: <category and code>
CWE: <CWE-xxx>
Severity: Critical | High | Medium | Low | Info
Confidence: Confirmed | High | Medium | Low
Line(s): <line numbers>
Description: <what is wrong and why it matters>
PoC: <how an attacker or the runtime triggers this>
Fix: <concrete corrected code>

Be exhaustive — include correctness issues, not just security issues.

```python
{CODE}
```
"""

# ── CRITIC ───────────────────────────────────────────────────────────────────
CRITIC_PROMPT_TPL = """You are a rigorous security peer-reviewer (the Critic).

Review the Actor's findings below. For each finding:
1. State TRUE POSITIVE or FALSE POSITIVE with reasoning.
2. If TP: confirm or adjust the severity (raise/lower/keep) with justification.
3. If FP: explain why the issue is not exploitable or not present.
4. If the fix is incomplete or a better fix exists, provide it.

After reviewing all findings, add a section:
## Missed Findings
List any real vulnerabilities the Actor overlooked.

Format each finding response as:
[F-xx] TP/FP | Severity: keep <X> | OR raise to <X> | OR lower to <X> | Notes: <your reasoning>

Actor's Findings:
---
{actor}
---

Code:
```python
{code}
```
"""

print("Getting token...", flush=True)
token = get_token()
print("OK\n", flush=True)

print("=== ACTOR PASS ===", flush=True)
actor = call_watsonx(token, ACTOR_PROMPT, max_tokens=2000)
print(actor, flush=True)

print("\n\n=== CRITIC PASS ===", flush=True)
critic = call_watsonx(token, CRITIC_PROMPT_TPL.format(actor=actor, code=CODE), max_tokens=2000)
print(critic, flush=True)

with open('.bob/tmp/ac_actor.txt', 'w', encoding='utf-8') as f:
    f.write(actor)
with open('.bob/tmp/ac_critic.txt', 'w', encoding='utf-8') as f:
    f.write(critic)

print("\nDONE", flush=True)
