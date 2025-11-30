#!/bin/sh

python -c "
import os
import sys
import vertexai
from vertexai import agent_engines
import asyncio

PROJECT_LOCATION='us-east4'
PROJECT_ID=os.environ[\"GOOGLE_CLOUD_PROJECT\"]
print(f'GOOGLE_CLOUD_PROJECT = {PROJECT_ID} LOCATION = {PROJECT_LOCATION}')

vertexai.init(
    project=PROJECT_ID,
    location=PROJECT_LOCATION,
    )

# Get the most recently deployed agent
agents_list = list(agent_engines.list())
if agents_list:
    remote_agent = agents_list[0]  # Get the first (most recent) agent
    client = agent_engines
    print(f'✅ Connected to deployed agent: {remote_agent.resource_name}')
    async def run_agent(remote_agent):
        async for item in remote_agent.async_stream_query(
            message=\"What is the weather in Tokyo?\",
	    ):
                print(item)
    asyncio.run(run_agent(remote_agent))
else:
    print('❌ No agents found. Please deploy first.')

"
