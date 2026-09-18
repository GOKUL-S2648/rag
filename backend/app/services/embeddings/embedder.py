from fastembed import TextEmbedding


MODEL_NAME = "BAAI/bge-small-en-v1.5"

_embedding_model = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TextEmbedding(model_name=MODEL_NAME)
    return _embedding_model


def generate_embedding(text: str) -> list[float]:
    model = get_embedding_model()
    embeddings = list(model.embed([text]))
    return embeddings[0].tolist()