import requests, json

token_resp = requests.post(
    'https://iam.cloud.ibm.com/identity/token',
    headers={'Content-Type': 'application/x-www-form-urlencoded'},
    data='grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=2YYihLJxrxnb8ZgIW5WCx6A05TBWi1oz2DQ7InbjDYyA'
)
token = token_resp.json()['access_token']
auth = 'Bearer ' + token

code_diff = '''--- /dev/null
+++ b/test.py
@@ -0,0 +1,36 @@
+API_KEY = "12345"
+
+def fetch_user_data(user_id):
+    """
+    Simulates fetching user data from a database using un-sanitized input.
+    """
+    connection = sqlite3.connect(':memory:')
+    cursor = connection.cursor()
+
+    cursor.execute("CREATE TABLE users (id TEXT, name TEXT, email TEXT)")
+    cursor.execute("INSERT INTO users VALUES ('1', 'Admin User', 'admin@example.com')")
+    cursor.execute("INSERT INTO users VALUES ('2', 'Standard User', 'user@example.com')")
+    connection.commit()
+
+    # ANTI-PATTERN: Un-sanitized input concatenated directly into a SQL query (SQL Injection)
+    query = "SELECT * FROM users WHERE id = '" + user_id + "'"
+
+    try:
+        cursor.execute(query)
+        results = cursor.fetchall()
+        return results
+    except sqlite3.Error as e:
+        return str(e)
+    finally:
+        connection.close()
+
+if __name__ == "__main__":
+    print(fetch_user_data("1"))
+    malicious_payload = "1' OR '1'='1"
+    print(fetch_user_data(malicious_payload))
'''

prompt = f"""You are an expert security auditor. Review the following Python code diff against OWASP Top 10 standards.

Identify all security vulnerabilities, classify them by OWASP category, severity (Critical/High/Medium/Low), and provide a remediation for each finding.

Format your response as:
1. A Markdown summary table of findings (Vulnerability | OWASP Category | Severity | Line | Remediation)
2. Followed by a SARIF v2.1.0 JSON block with all findings

Code Diff:
{code_diff}
"""

project_id = '778c398d-aa2f-42e2-b69f-dbd659038628'

for model_id in ['ibm/granite-4-h-small', 'ibm/granite-3-1-8b-base']:
    print(f"\n--- Trying model: {model_id} ---")
    payload = {
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 2000,
            "min_new_tokens": 10
        },
        "model_id": model_id,
        "project_id": project_id
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": auth
    }
    endpoint = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    resp = requests.post(endpoint, headers=headers, json=payload)
    print('Status:', resp.status_code)
    if resp.status_code == 200:
        result = resp.json()['results'][0]['generated_text']
        print(result)
        break
    else:
        print('Error:', resp.text[:800])
