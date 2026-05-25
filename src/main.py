import asyncio
from routers.skill_router import route
from routers.skill_loader import load_skills
from routers.tool_resolver import resolve_required_tools
from agent.functional_agent import create_agent, run_agent_verbose

BASE_SYSTEM_PROMPT = """
Please answer based on the information provided.
Do not make unfounded assumptions.
"""


async def main():
    # query = "Please recommend some movies by my favorite directors that I haven't seen yet."
    query = "我最常看的電影導演是誰"
    skills_dir = "./skills"

    # ===== SKILL ROUTING =====
    selected_skills = route(query)
    print("Selected skills:", selected_skills)

    # ===== LOAD SKILLS =====
    skill_prompt = load_skills(selected_skills, skills_dir)

    # ===== Resolve tools =====
    required_tools = resolve_required_tools(selected_skills, skills_dir)
    print("required_tools:", required_tools)

    # ===== BUILD SYSTEM PROMPT =====
    final_system_prompt = BASE_SYSTEM_PROMPT + "\n\n" + skill_prompt

    # ===== AGENT =====
    agent = await create_agent(system_prompt=final_system_prompt, tool_list=required_tools)
    response = await run_agent_verbose(agent, query)

    print("\n\n--------------------\nResponse: \n", str(response))

if __name__ == "__main__":
    asyncio.run(main())
