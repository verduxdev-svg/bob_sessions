#!/usr/bin/env bash
# ============================================================
#  start_server.sh — Launch WatsonxCritic in HTTP/SSE mode
#  Use this to expose the MCP server through ngrok for
#  watsonx Orchestrate integration.
#
#  Prerequisites:
#    1. pip install -r requirements.txt
#    2. cp .env.example .env && nano .env  (fill in credentials)
#    3. Install ngrok: https://ngrok.com/download
#
#  Usage:
#    chmod +x start_server.sh
#    ./start_server.sh           (starts on default port 8000)
#    ./start_server.sh 9000      (starts on port 9000)
#
#  Then in a SECOND terminal window:
#    ngrok http 8000
#  Copy the https://*.ngrok-free.app URL and paste it into:
#  watsonx Orchestrate -> Discover -> Tools -> Add a tool -> MCP server
# ============================================================

PORT=${1:-8000}

echo "[WatsonxCritic] Starting HTTP/SSE MCP server on port $PORT..."
echo "[WatsonxCritic] Once started, run in another terminal:"
echo "   ngrok http $PORT"
echo ""

python watsonx_mcp_server.py --http --port "$PORT"
