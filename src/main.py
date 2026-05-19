import asyncio
from routers.skill_router import route
from skills.skill_loader import load_skills
from agent.functional_agent import create_agent, run_agent_verbose

BASE_SYSTEM_PROMPT = """
Please answer based on the information provided.
Do not make unfounded assumptions.
"""


async def main():
    query = "Please recommend some movies by my favorite directors that I haven't seen yet."

    # ===== SKILL ROUTING =====
    selected_skills = route(query)
    print("Selected skills:", selected_skills)

    # ===== LOAD SKILLS =====
    skill_prompt = load_skills(
        selected_skills,
        skills_dir="./skills"
    )
    print(skill_prompt)

    # ===== BUILD SYSTEM PROMPT =====
    final_system_prompt = BASE_SYSTEM_PROMPT + "\n\n" + skill_prompt

    # ===== AGENT =====
    agent = await create_agent(system_prompt=final_system_prompt)
    response = await run_agent_verbose(agent, query)

    print("\n\n--------------------\nResponse: \n", str(response))

if __name__ == "__main__":
    asyncio.run(main())
