from pydantic_ai import Embedder
from pydantic_ai.embeddings.google import GoogleEmbeddingSettings


def new_embedder() -> Embedder:
    embedder: Embedder = Embedder(
        "google-gla:gemini-embedding-001",
        settings=GoogleEmbeddingSettings(
            dimensions=768,
            google_task_type="SEMANTIC_SIMILARITY",  # Optimized for similarity comparisons
        ),
    )

    return embedder
