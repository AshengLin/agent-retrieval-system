import asyncio
from runtime import run_query


async def main():
    response = await run_query(
        "Please recommend some movies by my favorite directors that I haven't seen yet."
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
