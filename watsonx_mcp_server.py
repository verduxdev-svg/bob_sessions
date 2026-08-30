import argparse
import os
from pathlib import Path
import requests
import uvicorn
from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer as FastMCP
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Mount, Route

# Explicitly load .env from the directory where this script lives
script_dir = Path(__file__).resolve().parent
dotenv_path = script_dir / ".env"
load_dotenv(dotenv_path=dotenv_path)

mcp = FastMCP("WatsonxCritic")


def get_iam_token() -> str:
    """Programmatically generate an IAM access token."""
    api_key = os.getenv("IBM_CLOUD_API_KEY")
    if not api_key:
        raise ValueError("IBM_CLOUD_API_KEY environment variable is not set.")
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
    base_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

    prompt = f"""You are an expert security auditor. Review the following code diff against OWASP Top 10 standards.
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
    parser = argparse.ArgumentParser(description="WatsonxCritic MCP Server")
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run in HTTP/SSE mode on localhost:8000 (for ngrok / watsonx Orchestrate)"
    )
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP mode (default: 8000)")
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP mode (default: 0.0.0.0)")
    args = parser.parse_args()

    if args.http:
        print(f"[WatsonxCritic] Starting HTTP/SSE MCP server on http://{args.host}:{args.port}")
        print("[WatsonxCritic] Expose publicly with:  ngrok http", args.port)

        # Wrap MCP SSE app with a root redirect so Orchestrate's gateway probe
        # hits / → redirects to /sse instead of getting a 404.
        async def root_redirect(request: Request) -> RedirectResponse:
            return RedirectResponse(url="/sse")

        sse_app = mcp.sse_app()
        app = Starlette(
            routes=[
                Route("/", endpoint=root_redirect),
                Mount("/", app=sse_app),
            ]
        )
        uvicorn.run(app, host=args.host, port=args.port)
    else:
        # Default: stdio transport — used by Bob IDE via .bob/mcp.json
        mcp.run(transport="stdio")
