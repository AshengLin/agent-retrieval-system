# python -m eval.run_eval
import asyncio
from src.routers.skill_router import route

TEST_CASES = [
    {
        "query": "Recommend movies by Christopher Nolan that I haven't seen.",
        "expected_skills": [
            "movie_recommendation_by_director",
            "exclude_watched_movies"
        ]
    }
]


def main(cases):
    for case in cases:
        skills = route(case["query"])

        if set(skills) == set(case["expected_skills"]):
            print(f"PASS: {case['query']}")
        else:
            print(f"FAIL: {case['query']}")
            print(f"Expected: {case['expected_skills']}")
            print(f"Actual:   {skills}")


if __name__ == "__main__":
    main(TEST_CASES)
