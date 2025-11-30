# app.py

from google.adk.agents.remote_a2a_agent import ( RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH,)
from google.adk.runners import App

from .agent import root_agent 
from .observability_plugin import ObservabilityPlugin

app = App(
    name="stockanalyst_app",
    root_agent=root_agent,
    plugins=[ObservabilityPlugin()],  # Add your custom plugin here
    )

__all__ = ["app"]

