from __future__ import annotations
import csv
from pathlib import Path
from typing import Dict, List
from .base import BasePipelineAgent

class MismatchLoggerAgent(BasePipelineAgent):
    """Append mismatches to CSV for manual audit."""

    def __init__(self, csv_path: str = "output/mismatches.csv", **kwargs):
        super().__init__(**kwargs)
        self.csv_path = Path(csv_path)
        # header will be added if file doesn't exist
        if not self.csv_path.exists():
            with self.csv_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(
                    fp,
                    fieldnames=["token", "section", "sentence", "abstract", "score"],
                )
                writer.writeheader()

    def run(self, records: List[Dict]):
        if not records:
            return records
        with self.csv_path.open("a", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(
                fp,
                fieldnames=["token", "section", "sentence", "abstract", "score"],
            )
            writer.writerows(records)
        return records
