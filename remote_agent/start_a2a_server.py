# start_a2a_server.py

import os
import subprocess
import logging
import json
import requests
import subprocess
import time
import uuid
# from agent import root_agent
# from agent import earnings_remote_a2a_app


logger = logging.getLogger()

# Start uvicorn server in background

server_process = None
# uvicorn agent:a2a_app --host localhost --port 8001
start_server: bool = True
if start_server:
    try:
        server_process = subprocess.Popen(
        [
        "uvicorn",
        "agent:a2a_app",  # Module:app format
        "--host",
        "localhost",
        "--port",
        "8001",
        ],
#        cwd="/home/schakrab02/drsa/ai-gcp-5d/accounting_agent",  # Run from current directory
        cwd=".",  # Run from current directory
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ},  # Pass environment variables (including GOOGLE_API_KEY)
        )

    except Exception as ex2:
        print(f'Exception from Popen: {ex2}')

# Store the process so we can stop it later
    logger.info(f"   Waiting for server to be ready... ProcessId = {server_process}")
    globals()["earnings_remote_server_process"] = server_process
    print(f"   Global Variables = {globals()}")
    logger.info(f"   Global Variables = {globals()}")

    print("🚀 Starting Earnings Remote Agent server...")


print("   Waiting for server to be ready...")
logger.info("   Waiting for server to be ready...")

# Wait for server to start (poll until it responds)
max_attempts = 30
for attempt in range(max_attempts):
    try:
        response = requests.get("http://localhost:8001/.well-known/agent-card.json", timeout=1)
        if response.status_code == 200:
            print(f"\n✅ Earnings Remote Agent server is running!")
            print(f"   Server URL: http://localhost:8001")
            print(f"   Agent card: http://localhost:8001/.well-known/agent-card.json")

            agent_card = response.json()
            print("📋 Product Catalog Agent Card:")
            print(json.dumps(agent_card, indent=2))

            print("\n✨ Key Information:")
            print(f"   Name: {agent_card.get('name')}")
            print(f"   Description: {agent_card.get('description')}")
            print(f"   URL: {agent_card.get('url')}")
            print(f"   Skills: {len(agent_card.get('skills', []))} capabilities exposed")

            break
    except requests.exceptions.RequestException:
        time.sleep(5)
        print(".", end="", flush=True)
    else:
        print("\n⚠️  Server may not be ready yet. Check manually if needed.")

