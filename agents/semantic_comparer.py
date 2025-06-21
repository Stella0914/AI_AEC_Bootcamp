from __future__ import annotations
import openai
import numpy as np
from typing import Dict, List
from .base import BasePipelineAgent

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

class SemanticComparerAgent(BasePipelineAgent):
    """Compute sentence↔abstract cosine similarity using OpenAI embeddings."""

    def __init__(self, model: str = "text-embedding-3-small", **kwargs):
        super().__init__(**kwargs)
        openai.api_key = kwargs.get("openai_api_key") or openai.api_key
        self.model = model

    def _embed(self, texts: List[str]):
        resp = openai.Embedding.create(model=self.model, input=texts)
        return [np.array(r["embedding"], dtype=np.float32) for r in resp["data"]]

    # input: List[{token, sentence, abstract}]
    def run(self, pairs: List[Dict]):
        sims = []
        for item in pairs:
            sent = item.get("sentence", "")
            abstract = item.get("abstract", "")
            if not abstract or not sent:
                sims.append(0.0)
                continue
            vecs = self._embed([sent, abstract])
            sims.append(cosine(vecs[0], vecs[1]))
        return sims
