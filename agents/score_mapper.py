from typing import Dict
from .base import BasePipelineAgent

class ScoreMapperAgent(BasePipelineAgent):
    """Convert error % to quality_score and band."""

    def run(self, error_percent: float) -> Dict[str, float | str]:
        quality_score = 1.0 - error_percent
        band = (
            "green" if quality_score >= 0.9 else "amber" if quality_score >= 0.75 else "red"
        )
        return {"quality_score": quality_score, "band": band}
