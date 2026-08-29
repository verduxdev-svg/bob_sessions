import os
import requests
from dotenv import load_dotenv
from mcp.server import MCPServer

load_dotenv()

mcp = MCPServer("WatsonxCritic")

def get_iam_token() -> str:
    """Programmatically generate an IAM access token."""
    api_key = os.getenv("IBM_CLOUD_API_KEY")
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={api_key}"
    
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

@mcp.tool()
def watsonx_security_audit(code_diff: str) -> str:
    """
    Sends code diffs to watsonx.ai for OWASP security analysis.
    Returns a markdown report and SARIF JSON.
    """
    token = get_iam_token()
    project_id = os.getenv("WATSONX_PROJECT_ID")
    base_url = os.getenv("WATSONX_URL")
    
    prompt = f"""
    You are an expert security auditor. Review the following code diff against OWASP Top 10 standards.
    Format your response with a Markdown summary followed by a valid SARIF v2.1.0 JSON block containing the findings.
    
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
        "model_id": "ibm/granite-4-h-small",
        "project_id": project_id
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    endpoint = f"{base_url}/ml/v1/text/generation?version=2023-05-29"
    response = requests.post(endpoint, headers=headers, json=payload)
    response.raise_for_status()
    
    return response.json()["results"][0]["generated_text"]

if __name__ == "__main__":
    
    mcp.run(transport='stdio')