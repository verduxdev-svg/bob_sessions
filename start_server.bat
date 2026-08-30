@echo off
REM ============================================================
REM  start_server.bat — Launch WatsonxCritic in HTTP/SSE mode
REM  Use this to expose the MCP server through ngrok for
REM  watsonx Orchestrate integration.
REM
REM  Prerequisites:
REM    1. pip install -r requirements.txt
REM    2. Copy .env.example to .env and fill in credentials
REM    3. Install ngrok: https://ngrok.com/download
REM
REM  Usage:
REM    start_server.bat           (starts on default port 8000)
REM    start_server.bat 9000      (starts on port 9000)
REM
REM  Then in a SECOND terminal window:
REM    ngrok http 8000
REM  Copy the https://*.ngrok-free.app URL and paste it into
REM  watsonx Orchestrate -> Discover -> Tools -> Add a tool -> MCP server
REM ============================================================

SET PORT=%1
IF "%PORT%"=="" SET PORT=8000

echo [WatsonxCritic] Starting HTTP/SSE MCP server on port %PORT%...
echo [WatsonxCritic] Once started, run in another terminal:
echo    ngrok http %PORT%
echo.

python watsonx_mcp_server.py --http --port %PORT%
