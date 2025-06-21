"""Orchestrate the end-to-end CrewAI flow."""
from __future__ import annotations
import random
import yaml
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass
import pandas as pd
from tqdm import tqdm

# Local imports
from agents import (
    PaperFetcherAgent,
    SemanticComparerAgent,
    MismatchLoggerAgent,
    ErrorCalculatorAgent,
    ScoreMapperAgent,
)
from tasks import (
    FetchPapersTask,
    CompareSemanticTask,
    LogMismatchTask,
    ComputeErrorTask,
    MapScoreTask,
)

TOKEN_REGEX = r"\[[0-9]+\]|\([A-Za-z]+ et al\.?,? \d{4}\)"

@dataclass
class CitationToken:
    token: str
    sentence: str
    section: str  # e.g. Methods, Results etc.

class CitationAuditCrew:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r", encoding="utf-8") as fp:
            cfg = yaml.safe_load(fp)
        self.cfg = cfg
        # instantiate agents with shared config
        self.paper_fetcher = PaperFetcherAgent(**cfg["paths"], **cfg.get("openai", {}))
        self.semantic_comparer = SemanticComparerAgent(
            openai_api_key=cfg["openai"]["api_key"], model=cfg["similarity"]["model"]
        )
        self.mismatch_logger = MismatchLoggerAgent(csv_path=cfg["paths"]["mismatch_csv"])
        self.error_calculator = ErrorCalculatorAgent()
        self.score_mapper = ScoreMapperAgent()
        self.threshold = cfg["similarity"]["threshold"]
        self.sample_ratio = cfg["sampling"]["ratio"]
        self.seed = cfg["sampling"]["seed"]

    # ----------------------------------------------------------
    # public API
    # ----------------------------------------------------------
    def audit(self, tokens: List[CitationToken]):
        # Step 1+2: sample 5 %
        random.seed(self.seed)
        sample_size = max(1, int(len(tokens) * self.sample_ratio))
        sample = random.sample(tokens, sample_size)

        # Fetch paper metadata
        fetch_task = FetchPapersTask(agent=self.paper_fetcher, tokens=[t.token for t in sample])
        papers = fetch_task.run()

        # Merge pairs
        pairs = []
        for tok, meta in zip(sample, papers):
            pairs.append(
                {
                    "token": tok.token,
                    "sentence": tok.sentence,
                    "section": tok.section,
                    "title": meta.get("title", ""),
                    "abstract": meta.get("abstract", ""),
                }
            )

        # Semantic comparison
        compare_task = CompareSemanticTask(agent=self.semantic_comparer, pairs=pairs)
        sims = compare_task.run()

        # Flag mismatches
        mismatch_records = []
        for p, score in zip(pairs, sims):
            p["score"] = score
            if score < self.threshold:
                mismatch_records.append(p)

        # Log mismatches
        log_task = LogMismatchTask(agent=self.mismatch_logger, records=mismatch_records)
        log_task.run()

        # Error percentage
        error_task = ComputeErrorTask(
            agent=self.error_calculator,
            mismatch_count=len(mismatch_records),
            sample_size=sample_size,
        )
        error_percent = error_task.run()

        # Map score
        map_task = MapScoreTask(agent=self.score_mapper, error_percent=error_percent)
        score_dict = map_task.run()

        return {
            "sample_size": sample_size,
            "mismatches": len(mismatch_records),
            "error_percent": error_percent,
            **score_dict,
        }
