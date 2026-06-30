# PYTHONPATH=. chainlit run src/ui/chainlit_app.py --port 8001

import sys
from pathlib import Path
import chainlit as cl
from src.runtime import run_query
from llama_index.core.agent.workflow import ToolCall, ToolCallResult


@cl.on_message
async def on_message(message: cl.Message):
    steps = {}

    async def tool_callback(event):
        if isinstance(event, ToolCall):
            step = cl.Step(
                name=event.tool_name,
                type="tool"
            )
            await step.__aenter__()
            steps[event.tool_id] = step

            step.input = str(event.tool_kwargs)
        elif isinstance(event, ToolCallResult):
            step = steps.get(event.tool_id)
            if step:
                step.output = str(event.tool_output)
                await step.__aexit__(None, None, None)

    response = await run_query(message.content, callback=tool_callback)

    await cl.Message(
        content=str(response)
    ).send()
