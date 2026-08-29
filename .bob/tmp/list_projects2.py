import requests, json

token_resp = requests.post(
    'https://iam.cloud.ibm.com/identity/token',
    headers={'Content-Type': 'application/x-www-form-urlencoded'},
    data='grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=2YYihLJxrxnb8ZgIW5WCx6A05TBWi1oz2DQ7InbjDYyA'
)
token = token_resp.json()['access_token']
auth = 'Bearer ' + token

# List projects via Watson Data Platform API
resp = requests.get(
    'https://api.dataplatform.cloud.ibm.com/v2/projects',
    headers={'Authorization': auth, 'Accept': 'application/json'}
)
print('Projects status:', resp.status_code)
try:
    data = resp.json()
    for p in data.get('resources', []):
        print('  Project:', p.get('entity', {}).get('name'), '| ID:', p.get('metadata', {}).get('guid'))
except Exception:
    print(resp.text[:1000])
