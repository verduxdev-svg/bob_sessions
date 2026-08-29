import os
import requests

os.environ['IBM_CLOUD_API_KEY'] = '2YYihLJxrxnb8ZgIW5WCx6A05TBWi1oz2DQ7InbjDYyA'
os.environ['WATSONX_PROJECT_ID'] = '63b8b6bd-8e24-4c27-94f5-753bfb4bb541'
os.environ['WATSONX_URL'] = 'https://us-south.ml.cloud.ibm.com'

api_key = os.environ['IBM_CLOUD_API_KEY']
url = 'https://iam.cloud.ibm.com/identity/token'
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
data = 'grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=' + api_key

response = requests.post(url, headers=headers, data=data)
print('IAM status:', response.status_code)
if response.status_code == 200:
    token = response.json()['access_token']
    print('Got token:', token[:30], '...')

    # Now test the watsonx generation endpoint
    project_id = os.environ['WATSONX_PROJECT_ID']
    base_url = os.environ['WATSONX_URL']

    code_diff = '''--- /dev/null
+++ b/test.py
@@ -1,3 +1,3 @@
+API_KEY = "12345"
+query = "SELECT * FROM users WHERE id = '" + user_id + "'"
'''

    prompt = f"""You are an expert security auditor. Review the following code diff against OWASP Top 10 standards.
Format your response with a Markdown summary followed by a valid SARIF v2.1.0 JSON block.

Code Diff:
{code_diff}
"""

    payload = {
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 1500,
            "min_new_tokens": 10
        },
        "model_id": "ibm/granite-3-8b-instruct",
        "project_id": project_id
    }

    headers2 = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + token
    }

    endpoint = base_url + "/ml/v1/text/generation?version=2023-05-29"
    resp = requests.post(endpoint, headers=headers2, json=payload)
    print('Watsonx status:', resp.status_code)
    if resp.status_code == 200:
        result = resp.json()['results'][0]['generated_text']
        print(result)
    else:
        print('Error:', resp.text)
else:
    print('IAM Error:', response.text)
