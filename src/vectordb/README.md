# VectorDB Layer

## Responsibility
This layer is responsible for:
- Fetching movie data from external APIs (TMDb)
- Transforming raw data into structured documents
- Generating embeddings from text
- Ingesting data into the vector database (Qdrant)

---
## run
Start the Qdrant server:

```bash
docker compose up -d
```

Then run the ingestion pipeline:
```
bashpython3 -m src.vectordb.download_upsert
```

The ingestion pipeline fetches movie data from TMDb, generates embeddings, and uploads the data to the Dockerized Qdrant instance.

## Components

### TMDb Fetching
- `fetch_movies()`
  - Retrieves movie data using TMDb discover API
- `fetch_director()`
  - Fetches director information for each movie

### Data Processing
- `build_movie_doc()`
  - Constructs structured movie objects
  - Includes metadata such as title, rating, director, and poster URL

### Text Builder
- `build_text()`
  - Converts structured movie data into embedding-friendly text format

### Embedding
- Uses `SentenceTransformer (all-MiniLM-L6-v2)`
- Generates dense vector representations of movie descriptions

### Qdrant Initialization
- `init_qdrant()`
  - Creates collection if not exists
  - Configures vector size and similarity metric (COSINE)
  - Applies HNSW indexing parameters

---
## Flow
```mermaid
flowchart TB
    TMDb[TMDb API]
    --> Fetch[Fetch Movies & Credits]
    --> Transform[Build Movie Document]
    --> Text[Build Text Representation]
    --> Embed[Generate Embedding]
    --> Ingest[Ingest into Qdrant]
    --> Qdrant[Dockerized Qdrant]
```

---
## Design Principles
- Separate data ingestion from query logic
- Keep embedding pipeline simple and reproducible
- Store raw metadata as payload for flexible filtering
- Make ingestion safe to re-run

---

## Notes
- Uses TMDb API (/discover/movie and /credits)
- Language is currently set to en-US
- Rate limiting is handled via time.sleep(0.2)
- Embedding model dimension is inferred dynamically
- Qdrant runs as a Docker container
- Qdrant is accessed through localhost:6333

---
## Future Improvements
- Add multi-language support (e.g., ja-JP)
- Support batch ingestion / parallel API requests
- Introduce hybrid search (dense + sparse retrieval)
- Add payload indexes for structured filtering
- Move embedding and ingestion into dedicated pipeline jobs
- Introduce image embeddings for poster-based search
- Evaluate retrieval quality with a dedicated evaluation pipeline
