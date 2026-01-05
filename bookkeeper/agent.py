import asyncio
import csv
import os
from google.adk.agents import LlmAgent, Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.models import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from datetime import datetime

from .sub_agents.image_agent.agent import image_agent
from .sub_agents.transactions_analyst.agent import transactions_analyst

bookkeeper = Agent(
    name="bookkeeper",
    model=LiteLlm("ollama/qwen2.5:7b"), 
    description="Personal finance management agent",
    instruction="""
    You are a personal finance management agent that is responsible for overseeing the work of the other agents.

    Always delegate the task to the appropriate agent. Use your best judgement to determine which agent to delegate to.

    You are responsible for delegating tasks to the following agent:
    - image_agent
    - transactions_analyst
    """,
    sub_agents=[image_agent, transactions_analyst],
)


# Instantiate constants
APP_NAME = "Bookkeeper_App"
USER_ID = "12345"
SESSION_ID = "112233"

async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner


root_agent = bookkeeper