# fastmcp run server.py
from mcp.server.fastmcp import FastMCP
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range
from sentence_transformers import SentenceTransformer
from collections import Counter

# ===== INIT=====
client = QdrantClient(path="../vectordb/qdrant_data")
model = SentenceTransformer("all-MiniLM-L6-v2")

mcp = FastMCP("test_tools")


@mcp.tool()
def movie_search_tool(
    query: str,
    director: str = None,
    year: int = None,
    min_rating: float = None,
    top_k: int = 5
) -> list:
    """
    Search movies using semantic query + optional filters.
    """

    query_vector = model.encode(query).tolist()

    conditions = []

    if director:
        conditions.append(
            FieldCondition(
                key="director",
                match=MatchValue(value=director)
            )
        )

    if year:
        conditions.append(
            FieldCondition(
                key="year",
                match=MatchValue(value=str(year))
            )
        )

    if min_rating:
        conditions.append(
            FieldCondition(
                key="rating",
                range=Range(gte=min_rating)
            )
        )

    query_filter = Filter(must=conditions) if conditions else None

    results = client.search(
        collection_name="movies",
        query_vector=query_vector,
        query_filter=query_filter,
        limit=top_k
    )

    output = []
    for r in results:
        payload = r.payload
        output.append({
            "title": payload.get("title"),
            "director": payload.get("director"),
            "year": payload.get("year"),
            "rating": payload.get("rating"),
            "overview": payload.get("overview"),
        })

    return output


user_history = [  # fake data
    {"title": "Inception", "director": "Christopher Nolan"},
    {"title": "Interstellar", "director": "Christopher Nolan"},
    {"title": "The Dark Knight", "director": "Christopher Nolan"},
    {"title": "Tenet", "director": "Christopher Nolan"},
    {"title": "Pulp Fiction", "director": "Quentin Tarantino"},
]


@mcp.tool()
def get_favorite_director() -> str:
    """
    Return the user's most frequently watched director.
    """
    directors = [m["director"] for m in user_history if m["director"]]

    if not directors:
        return ""

    return Counter(directors).most_common(1)[0][0]


@mcp.tool()
def get_watched_movies() -> list:
    """
    Return a list of movie titles the user has already watched.
    """
    return [m["title"] for m in user_history]


if __name__ == "__main__":
    mcp.run()
