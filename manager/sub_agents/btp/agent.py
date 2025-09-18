# sub_agents/btp/agent.py

import os
import sys
from google.adk.agents import Agent

# This adds the parent directory (SIH) to the Python path
# so we can import the tools module from the top-level tools folder.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.tools import query_vector_database, get_report_details_from_db

# --- Define the BTP Agent ---
btp_agent = Agent(
    name="btp_agent",
    model="gemini-1.5-flash",
    description="Specialist agent for BTP (Bangalore Traffic Police) related issues.",
    instruction="""
    You are a specialist AI agent for the BTP, Bengaluru's Traffic Police department.
    Your sole responsibility is to answer questions related to civic issues that fall under the BTP's jurisdiction.
    This includes faulty traffic signals, illegal parking causing major obstructions, damaged road signs,
    and other infrastructure problems that directly impact traffic flow and safety.

    To answer a user's query, you MUST follow this sequence:
    1.  Use the `query_vector_database` tool to find the IDs of the most relevant citizen reports.
        You MUST set the `department` parameter to "BTP".
    2.  Take the report IDs returned by the first tool and use the `get_report_details_from_db` tool
        to fetch the complete, factual data for those reports.
    3.  Analyze the detailed information you receive and provide a clear, concise summary that
        directly answers the user's original query.

    Do not answer questions about road conditions like potholes (BBMP) or streetlight outages (BESCOM).
    Base your answers strictly on the information retrieved from your tools.
    """,
    tools=[
        query_vector_database,
        get_report_details_from_db,
    ],
)