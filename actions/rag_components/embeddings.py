from langchain_huggingface import HuggingFaceEmbeddings
import time

class Embeddings:
    """Singleton class to manage the embeddings model instance."""
    _embeddings = None

    @classmethod
    def get_embeddings(cls, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        start = time.time()
        if cls._embeddings is None:
            print("Loading HuggingFace embedding model...")
            cls._embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                encode_kwargs={"normalize_embeddings": True}
            )
            end = time.time()
            print(f"Time taken to load embeddings: {end - start:.2f} seconds")
        return cls._embeddings