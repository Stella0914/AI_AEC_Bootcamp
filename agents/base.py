"""Common mixin for all non-LLM agents – thin wrapper around plain Python."""
from pathlib import Path
from typing import Any, Dict, List, Sequence
import json

class BasePipelineAgent:
    """Base class providing a uniform run() interface."""

    def __init__(self, **kwargs):
        self.config = kwargs
        # ensure dirs exist
        Path(self.config.get("cache_dir", "cache")).mkdir(exist_ok=True)
        Path(self.config.get("output_dir", "output")).mkdir(exist_ok=True)

    # subclasses must implement
    def run(self, *args, **kwargs):
        raise NotImplementedError

    # optional helper to persist JSON artefacts for inspection
    def _dump_json(self, data: Any, file_path: Path):
        with file_path.open("w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)
