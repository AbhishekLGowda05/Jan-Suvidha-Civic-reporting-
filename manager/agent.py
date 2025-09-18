# manager/agent.py

from google.adk.agents import Agent

# Import the specialist sub-agent instances that this manager will orchestrate
from .sub_agents.bbmp.agent import bbmp
from .sub_agents.bescom.agent import bescom
from .sub_agents.btp.agent import btp
from .sub_agents.bwhsp.agent import bwhsp

# --- Define the Root/Manager Agent ---
root_agent = Agent(
    name="manager_agent",
    model="gemini-1.5-flash",
    description="A manager agent that orchestrates and delegates tasks to specialist civic authority agents.",
    instruction="""
    You are the central manager for a civic issue reporting system in Bengaluru.
    Your primary responsibility is to analyze an incoming user query and delegate it to the correct specialist sub-agent.
    You MUST NOT attempt to answer the query yourself. Your only job is to route the task.

    Here are your available specialist agents and their responsibilities:
    - `bbmp_agent`: Handles issues related to roads (potholes), garbage, public parks, and general city infrastructure.
    - `bescom_agent`: Handles issues related to electricity, including streetlights, power outages, and exposed wiring.
    - `btp_agent`: Handles issues related to traffic infrastructure, such as faulty traffic signals and damaged road signs.
    - `bwssb_agent`: Handles issues related to the water supply and sewerage system, like pipe leakages and sewage blocks.

    Based on the user's query, determine the single best agent to handle the request and delegate the task to them.
    If a query is ambiguous or does not fit any category, ask the user for clarification.
    """,
    # The list of agents this manager can delegate tasks to.
    sub_agents=[
        bbmp,
        bescom,
        btp,
        bwhsp,
    ],
    # The manager agent itself does not need direct access to the database tools.
    # Its "tools" are its sub-agents.
    tools=[],
)