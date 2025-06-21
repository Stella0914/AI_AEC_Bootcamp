"""Define CrewAI Tasks that invoke our pipeline agents directly via tools."""
from crewai import Task
from typing import List, Dict

class FetchPapersTask(Task):
    """Fetch metadata for a sample of citation tokens."""

    def __init__(self, agent, tokens: List[str]):
        super().__init__(
            description="Fetch paper title & abstract for sampled tokens.",
            expected_output="List of dicts with token, title, abstract.",
            agent=agent,
        )
        self.tokens = tokens

    def run(self):
        return self.agent.run(self.tokens)

class CompareSemanticTask(Task):
    def __init__(self, agent, pairs: List[Dict]):
        super().__init__(
            description="Compute semantic similarity between sentence and abstract.",
            expected_output="List[float] similarities.",
            agent=agent,
        )
        self.pairs = pairs

    def run(self):
        return self.agent.run(self.pairs)

class LogMismatchTask(Task):
    def __init__(self, agent, records: List[Dict]):
        super().__init__(
            description="Log mismatching citations to CSV.",
            expected_output="Same list of records for downstream stats.",
            agent=agent,
        )
        self.records = records

    def run(self):
        return self.agent.run(self.records)

class ComputeErrorTask(Task):
    def __init__(self, agent, mismatch_count: int, sample_size: int):
        super().__init__(
            description="Compute error percentage.",
            expected_output="Float error percent.",
            agent=agent,
        )
        self.mismatch_count = mismatch_count
        self.sample_size = sample_size

    def run(self):
        return self.agent.run(self.mismatch_count, self.sample_size)

class MapScoreTask(Task):
    def __init__(self, agent, error_percent: float):
        super().__init__(
            description="Map error percentage to quality score and band.",
            expected_output="Dict with quality_score and band.",
            agent=agent,
        )
        self.error_percent = error_percent

    def run(self):
        return self.agent.run(self.error_percent)
