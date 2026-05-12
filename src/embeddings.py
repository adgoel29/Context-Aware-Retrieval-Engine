from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer


@dataclass
class EmbeddingResult:
    values: np.ndarray



VERTEX_TO_ST_MODEL = {
    "textembedding-gecko@001": "all-MiniLM-L6-v2",
}


class TextEmbeddingModelWrapper:
    """
    Drop-in local replacement for vertexai.language_models.TextEmbeddingModel.
    Interface is identical — swap in the real Vertex AI class for production.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model_name = model_name
        self._model = SentenceTransformer(model_name)

    @classmethod
    def from_pretrained(cls, model_name: str) -> "TextEmbeddingModelWrapper":
        """Mirrors vertexai.language_models.TextEmbeddingModel.from_pretrained()."""
        st_model_name = VERTEX_TO_ST_MODEL.get(model_name, model_name)
        return cls(model_name=st_model_name)

    def get_embeddings(self, texts: list) -> list:
        """
        Mirrors Vertex AI's get_embeddings().
        Returns a list of EmbeddingResult objects — access vector via .values
        """
        vectors = self._model.encode(texts)
        return [EmbeddingResult(values=vec) for vec in vectors]

    def embed_single(self, text: str) -> np.ndarray:
        """Convenience method — returns a flat numpy array for one text."""
        return self.get_embeddings([text])[0].values
    
# ans=TextEmbeddingModelWrapper()
# print(ans.get_embeddings(["hello","my"]))