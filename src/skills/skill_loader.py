import os
from typing import List
import yaml


def extract_prompt_body(content: str) -> str:
    """
    Remove YAML frontmatter and return prompt body.
    """

    try:
        _, _, body = content.split("---", 2)
        return body.strip()

    except ValueError:
        return content.strip()


def load_full_skill(skill_name: str, skills_dir: str) -> str:
    """
    Load a full skill markdown file by skill name.
    """

    for filename in os.listdir(skills_dir):

        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(skills_dir, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            _, yaml_block, _ = content.split("---", 2)

            metadata = yaml.safe_load(yaml_block)

            if metadata.get("name") == skill_name:
                return extract_prompt_body(content)

        except Exception:
            continue

    return ""


def load_skills(skill_names: List[str], skills_dir: str) -> str:
    """
    Combine multiple skills into one prompt.
    """

    prompts = []

    for skill_name in skill_names:

        prompt = load_full_skill(skill_name, skills_dir)

        if prompt:
            prompts.append(prompt)

    return "\n\n".join(prompts)