from dotenv import load_dotenv
import os
from llama_index.core.agent.workflow import FunctionAgent, ToolCall, ToolCallResult
from llama_index.llms.google_genai import GoogleGenAI
from google.genai import types
import asyncio
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


async def create_agent():
    client = BasicMCPClient("http://127.0.0.1:8000/mcp")

    tools = await aget_tools_from_mcp_url(
        "http://127.0.0.1:8000/mcp",
        client=client,
        allowed_tools=["movie_search_tool", "get_favorite_director", "get_watched_movies"]
    )

    system_prompt = """
    Please answer based on the information provided.
    Do not make unfounded assumptions.
    """

    agent = FunctionAgent(
        tools=tools,
        llm=llm,
        system_prompt=system_prompt
    )
    return agent


async def run_agent_verbose(agent, query: str):
    handler = agent.run(query)
    async for event in handler.stream_events():
        if isinstance(event, ToolCall):
            print(f"Calling tool {event.tool_name} with args {event.tool_kwargs}...")
            print("--------------")
        elif isinstance(event, ToolCallResult):
            print(
                f"Called tool {event.tool_name} with args {event.tool_kwargs}\n\nGot result: {event.tool_output}"
            )
    return await handler


async def main():
    agent = await create_agent()
    response = await run_agent_verbose(agent, "Please recommend some movies by my favorite directors that I haven't seen yet.")
    print("\n\n\nANS:", str(response))

if __name__ == "__main__":
    asyncio.run(main())
