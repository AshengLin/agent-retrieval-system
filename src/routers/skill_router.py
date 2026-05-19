import os
import yaml
import json
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai

# ===== ENV =====
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# ===== PROMPT =====
ROUTER_PROMPT = """
You are a skill routers.

Your job is to select the most relevant skills for the user query.
You will be given:
1. A user query
2. A list of available skills (metadata only)

Return:
- A list of selected skill names

Rules:
- Only select from provided skills
- You may select multiple skills if needed
- If no skill is relevant, return an empty list

Output format (STRICT JSON):
{
  "skills": ["skill_name_1", "skill_name_2"]
}
"""


# ===== SCHEMA =====
class MatchResult(BaseModel):
    skills: List[str]


# ===== LOAD SKILLS =====
def load_skill_metadata(skills_dir: str):
    skills = []

    for filename in os.listdir(skills_dir):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(skills_dir, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.startswith("---"):
            continue

        try:
            _, yaml_block, _ = content.split("---", 2)
        except ValueError:
            continue

        metadata = yaml.safe_load(yaml_block)
        skills.append(metadata)

    return skills


def build_router_input(skills):
    return [
        {
            "name": s["name"],
            "description": s.get("description", "")
        }
        for s in skills
    ]


# ===== ROUTER FUNCTION =====
def route(query: str, skills_dir: str = "./skills") -> List[str]:
    client = genai.Client(api_key=api_key)

    skills = build_router_input(load_skill_metadata(skills_dir))
    skills_str = json.dumps(skills, ensure_ascii=False)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""
{ROUTER_PROMPT}

User Query:
{query}

Available Skills:
{skills_str}
""",
        config={
            "response_mime_type": "application/json",
            "response_json_schema": MatchResult.model_json_schema(),
        }
    )

    try:
        result = MatchResult.model_validate_json(response.text)
        return result.skills
    except Exception as e:
        print("Router parse error:", e)
        return []
