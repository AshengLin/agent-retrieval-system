from src.routers.skill_router import route
from src.routers.skill_loader import load_skills
from src.routers.tool_resolver import resolve_required_tools
from src.agent.functional_agent import create_agent, run_agent
from pathlib import Path
SKILLS_DIR = Path(__file__).parent / "skills"

BASE_SYSTEM_PROMPT = """
Please answer based on the information provided.
Do not make unfounded assumptions.
"""


async def run_query(query: str, callback=None):
    # skills_dir = "./skills"

    # ===== SKILL ROUTING =====
    selected_skills = route(query, skills_dir=SKILLS_DIR)
    print("Selected skills:", selected_skills)

    # ===== LOAD SKILLS =====
    skill_prompt = load_skills(selected_skills, SKILLS_DIR)

    # ===== Resolve tools =====
    required_tools = resolve_required_tools(selected_skills, SKILLS_DIR)
    print("required_tools:", required_tools)

    # ===== BUILD SYSTEM PROMPT =====
    final_system_prompt = BASE_SYSTEM_PROMPT + "\n\n" + skill_prompt

    # ===== AGENT =====
    agent = await create_agent(system_prompt=final_system_prompt, tool_list=required_tools)
    response = await run_agent(agent, query, callback=callback)

    print("\n\n--------------------\nResponse: \n", str(response))
    return response
