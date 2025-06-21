from typing import Dict
from .base import BasePipelineAgent

class ErrorCalculatorAgent(BasePipelineAgent):
    """Compute error percentage."""

    def run(self, mismatches: int, sample_size: int) -> float:
        if sample_size == 0:
            return 0.0
        return mismatches / sample_size
