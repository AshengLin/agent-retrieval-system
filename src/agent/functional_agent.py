from dotenv import load_dotenv
import os
from llama_index.core.agent.workflow import FunctionAgent, ToolCall, ToolCallResult
from llama_index.llms.google_genai import GoogleGenAI
from google.genai import types
from typing import List, Optional
from llama_index.tools.mcp import BasicMCPClient, aget_tools_from_mcp_url

# ===== ENV =====
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")


# ===== LLM =====
llm = GoogleGenAI(
    model="gemini-2.5-flash",
    generation_config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=0
        )
    ),
)


async def create_agent(system_prompt: str, tool_list: Optional[List[str]]):
    client = BasicMCPClient("http://127.0.0.1:8000/mcp")

    allowed_tools = tool_list or None  # fallback policy

    tools = await aget_tools_from_mcp_url(
        "http://127.0.0.1:8000/mcp",
        client=client,
        allowed_tools=allowed_tools
    )

    print("\nLoaded tools:")
    for tool in tools:
        print("-", tool.metadata.name)

    agent = FunctionAgent(
        tools=tools,
        llm=llm,
        system_prompt=system_prompt
    )
    return agent


async def run_agent(agent, query: str, callback=None):
    """
    Run agent and optionally stream events to external handlers.
    """
    handler = agent.run(query)
    async for event in handler.stream_events():
        if callback is None:
            if isinstance(event, ToolCall):
                print(f"Calling tool {event.tool_name} with args {event.tool_kwargs}...")
                print("--------------\n\n")
            elif isinstance(event, ToolCallResult):
                print(
                    f"Called tool {event.tool_name} with args {event.tool_kwargs}\n\nGot result: {event.tool_output}"
                )
        else:
            await callback(event)
    return await handler
