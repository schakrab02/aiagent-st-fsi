# my_observability_plugin.py observability_plugin.py
import logging
from typing import Type, Dict, Any, Optional, List, Union, Annotated, Literal, Tuple, AsyncGenerator
from google.adk.plugins import LoggingPlugin
from google.adk.tools import BaseTool, AgentTool, FunctionTool, ToolContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event


logger = logging.getLogger(__name__)
class ObservabilityPlugin(LoggingPlugin):
    async def on_agent_start(self, agent_name: str, context: dict):
        print(f'ObservabilityPlugin.on_agent_start {__name__}:: Agent {agent_name} started with context: {context}   {__name}')
        logger.info(f'ObservabilityPlugin.on_agent_start {__name__}:: Agent {agent_name} started with context: {context}   {__name}')

    async def on_tool_invocation(self, tool_name: str, tool_args: dict, result: str):
        print(f'ObservabilityPlugin.on_tool_invocatio {__name__}:: Tool {tool_name} invoked with args: {tool_args}, result: {result}')
        logger.info(f'ObservabilityPlugin.on_tool_invocatio {__name__}:: Tool {tool_name} invoked with args: {tool_args}, result: {result}')

    async def on_tool_error_callback( self, *, tool: BaseTool, tool_args: dict[str, Any], 
            tool_context: ToolContext, error: Exception,) -> Optional[dict]:
        print(f'ObservabilityPlugin.on_tool_error_callback {__name__}:: Tool {tool} invoked with args: {tool_args}, Error: {error}')
        logger.error(f'ObservabilityPlugin.on_tool_error_callback {__name__}:: Tool {tool} invoked with args: {tool_args}, Error: {error}')

    async def on_event_callback( self, *, invocation_context: InvocationContext, event: Event) -> Optional[Event]:
        print(f'ObservabilityPlugin.on_event_callback {__name__}:: Invocation {invocation_context} Event: {event}')
        logger.info(f'ObservabilityPlugin.on_event_callback {__name__}:: Invocation {invocation_context} Event: {event}')

# Add other relevant callback methods as needed
