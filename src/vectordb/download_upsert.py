import requests
import time
from dotenv import load_dotenv
import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct
from qdrant_client.http.models import VectorParams, HnswConfigDiff, Distance

# ===== ENV =====
load_dotenv()
BASE_URL = "https://api.themoviedb.org/3"


# ===== TMDb =====
def fetch_movies(page=1):
    url = f"{BASE_URL}/discover/movie"
    params = {
        "api_key": os.getenv("TMDB_API_KEY"),
        "language": "en-US",
        "sort_by": "popularity.desc",
        "page": page,
    }
    return requests.get(url, params=params).json()


def fetch_director(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/credits"
    params = {"api_key": os.getenv("TMDB_API_KEY")}
    data = requests.get(url, params=params).json()
    for person in data.get("crew", []):
        if person["job"] == "Director":
            return person["name"]
    return None


def build_movie_doc(movie):
    director = fetch_director(movie["id"])
    time.sleep(0.2)

    poster = movie.get("poster_path")

    return {
        "id": movie["id"],
        "title": movie["title"],
        "overview": movie["overview"],
        "rating": movie["vote_average"],
        "release_date": movie["release_date"],
        "director": director,
        "poster_path": f"https://image.tmdb.org/t/p/original/{poster}" if poster else None
    }


def get_movies(limit=5):
    movies = []
    page = 1

    while len(movies) < limit:
        data = fetch_movies(page)
        for m in data["results"]:
            print(m)
            doc = build_movie_doc(m)
            movies.append(doc)
            if len(movies) >= limit:
                break

        page += 1
    return movies


# ===== TEXT BUILD =====
def build_text(movie):
    return f"""
    Title: {movie['title']}
    Director: {movie['director']}
    Rating: {movie['rating']}
    Release: {movie['release_date']}
    Overview: {movie['overview']}
    PosterPath: {movie['poster_path']}
    """


# ===== Qdrant Setup =====
def init_qdrant(text_dim):
    client = QdrantClient(path="qdrant_data")
    collections = [c.name for c in client.get_collections().collections]

    if "movies" not in collections:
        client.create_collection(
            collection_name="movies",
            vectors_config=VectorParams(size=text_dim, distance=Distance.COSINE),
            hnsw_config=HnswConfigDiff(m=64, ef_construct=512)
        )

    return client


if __name__ == "__main__":
    movies = get_movies(limit=500)

    text_model = SentenceTransformer("all-MiniLM-L6-v2")
    text_dim = len(text_model.encode("test"))

    # batch embedding
    texts = [build_text(m) for m in movies]
    vectors = text_model.encode(texts)

    # Qdrant
    client = init_qdrant(text_dim)

    points = []
    for m, vector in zip(movies, vectors):
        points.append(
            PointStruct(
                id=m["id"],
                vector=vector.tolist(),
                payload=m
            )
        )

    # upsert
    client.upsert(
        collection_name="movies",
        points=points
    )

    print(f"Inserted {len(points)} movies into Qdrant")
