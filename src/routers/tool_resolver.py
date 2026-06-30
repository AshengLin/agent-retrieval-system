from src.routers.skill_router import load_skill_metadata


def resolve_required_tools(selected_skill_names, skills_dir):
    """
    Identify the tools required for these skills.

    If no skills are selected, return [].
    """
    skills = load_skill_metadata(skills_dir)
    required_tools = set()

    for skill in skills:
        if skill["name"] in selected_skill_names:
            tools = skill.get("required_tools", [])
            required_tools.update(tools)
            print(required_tools)
    return list(required_tools)

