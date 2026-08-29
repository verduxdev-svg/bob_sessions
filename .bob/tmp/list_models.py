import requests

token_resp = requests.post(
    'https://iam.cloud.ibm.com/identity/token',
    headers={'Content-Type': 'application/x-www-form-urlencoded'},
    data='grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=2YYihLJxrxnb8ZgIW5WCx6A05TBWi1oz2DQ7InbjDYyA'
)
token = token_resp.json()['access_token']
auth = 'Bearer ' + token

resp = requests.get(
    'https://us-south.ml.cloud.ibm.com/ml/v1/foundation_model_specs',
    headers={'Authorization': auth, 'Accept': 'application/json'},
    params={'version': '2023-05-29', 'limit': 200}
)
print('Status:', resp.status_code)
if resp.status_code == 200:
    models = resp.json().get('resources', [])
    print(f'Found {len(models)} models:')
    for m in models:
        mid = m.get('model_id', '')
        if 'granite' in mid.lower():
            print(' ', mid)
else:
    print(resp.text[:500])
