import os
import requests

token_resp = requests.post(
    'https://iam.cloud.ibm.com/identity/token',
    headers={'Content-Type': 'application/x-www-form-urlencoded'},
    data='grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=2YYihLJxrxnb8ZgIW5WCx6A05TBWi1oz2DQ7InbjDYyA'
)
token = token_resp.json()['access_token']
auth = 'Bearer ' + token

# List WML instances
resp = requests.get(
    'https://us-south.ml.cloud.ibm.com/ml/v4/instances',
    headers={'Authorization': auth, 'Accept': 'application/json'},
    params={'version': '2023-05-29'}
)
print('WML instances status:', resp.status_code)
print(resp.text[:2000])
