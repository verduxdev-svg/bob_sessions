import requests, json, sys

TOKEN_URL = 'https://iam.cloud.ibm.com/identity/token'
WATSONX_URL = 'https://us-south.ml.cloud.ibm.com'
API_KEY = '2YYihLJxrxnb8ZgIW5WCx6A05TBWi1oz2DQ7InbjDYyA'
PROJECT_ID = '778c398d-aa2f-42e2-b69f-dbd659038628'
MODEL_ID = 'ibm/granite-4-h-small'

def get_token():
    r = requests.post(TOKEN_URL,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data='grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=' + API_KEY)
    r.raise_for_status()
    return r.json()['access_token']

def call_watsonx(token, prompt, max_tokens=2000):
    payload = {
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": max_tokens,
            "min_new_tokens": 20
        },
        "model_id": MODEL_ID,
        "project_id": PROJECT_ID
    }
    r = requests.post(
        WATSONX_URL + '/ml/v1/text/generation?version=2023-05-29',
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + token},
        json=payload
    )
    r.raise_for_status()
    return r.json()['results'][0]['generated_text']

CODE = open('test.py').read()

# ─── ACTOR PROMPT ────────────────────────────────────────────────────────────
ACTOR_PROMPT = f"""You are a senior application security engineer performing a thorough OWASP Top 10 code review.

Analyse the Python code below and produce an exhaustive list of every security vulnerability you can find.
For EACH finding provide:
- Finding ID (F-01, F-02, …)
- Vulnerability name
- OWASP Top 10 category and code (e.g. A03:2021 – Injection)
- Severity: Critical / High / Medium / Low / Informational
- Exact line number(s)
- Proof-of-concept exploit description (how an attacker would trigger it)
- Recommended fix (concrete code snippet where possible)

Be thorough — do not skip edge cases or informational issues.

```python
{CODE}
```
"""

# ─── CRITIC PROMPT ───────────────────────────────────────────────────────────
CRITIC_PROMPT_TEMPLATE = """You are a rigorous security peer-reviewer (the Critic). Your job is to challenge an Actor's security findings.

For each finding in the Actor's report below:
1. Confirm it is a REAL vulnerability (True Positive) OR dismiss it as a False Positive — give your reasoning.
2. If the finding is valid, assess whether the severity rating is correct or should be adjusted up/down and why.
3. If the finding is missing important context or a better fix exists, provide it.
4. Identify any vulnerabilities the Actor MISSED that should be added.

Be critical but fair. Output a structured Critic Review in this format for each finding:
  [F-xx] TP/FP | Severity: keep/raise/lower to <new severity> | Notes: <your assessment>

Then append a section "## Missed Findings" listing anything the Actor overlooked.

Actor's Report:
---
{actor_output}
---

Code under review:
```python
{code}
```
"""

print("=== STEP 1: Getting IAM token ===", flush=True)
token = get_token()
print("Token acquired.\n", flush=True)

print("=== STEP 2: ACTOR — initial findings ===", flush=True)
actor_output = call_watsonx(token, ACTOR_PROMPT, max_tokens=2000)
print(actor_output, flush=True)

print("\n\n=== STEP 3: CRITIC — peer review of findings ===", flush=True)
critic_prompt = CRITIC_PROMPT_TEMPLATE.format(actor_output=actor_output, code=CODE)
critic_output = call_watsonx(token, critic_prompt, max_tokens=2000)
print(critic_output, flush=True)

# Save outputs for the report
with open('.bob/tmp/actor_output.txt', 'w') as f:
    f.write(actor_output)
with open('.bob/tmp/critic_output.txt', 'w') as f:
    f.write(critic_output)

print("\n\nDONE", flush=True)
