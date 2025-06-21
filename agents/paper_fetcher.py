from __future__ import annotations
import requests
from pathlib import Path
from typing import Dict, List
from urllib.parse import quote_plus
import sqlite3
import hashlib
from .base import BasePipelineAgent

CROSSREF_ENDPOINT = "https://api.crossref.org/works?query.bibliographic={q}&rows=1"
PUBMED_SEARCH = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&"
    "term={q}&retmax=1&retmode=json"
)
PUBMED_SUMMARY = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/summary.fcgi?db=pubmed&"
    "id={pid}&retmode=json"
)

class PaperFetcherAgent(BasePipelineAgent):
    """Fetch title & abstract for a list of citation tokens via CrossRef/PubMed."""

    def __init__(self, cache_db: str = "cache/papers.db", **kwargs):
        super().__init__(**kwargs)
        self.cache_db = Path(cache_db)
        self._init_cache()

    def get(self, key: str, default=None):
        """Provide access to configuration values."""
        return self.config.get(key, default)

    def _init_cache(self):
        conn = sqlite3.connect(self.cache_db)
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS papers (
                digest TEXT PRIMARY KEY,
                title TEXT,
                abstract TEXT
            )"""
        )
        conn.commit()
        conn.close()

    def _digest(self, query: str) -> str:
        return hashlib.sha256(query.encode()).hexdigest()

    def _lookup_cache(self, query: str):
        conn = sqlite3.connect(self.cache_db)
        cur = conn.cursor()
        cur.execute("SELECT title, abstract FROM papers WHERE digest=?", (self._digest(query),))
        row = cur.fetchone()
        conn.close()
        if row:
            return {"title": row[0], "abstract": row[1]}
        return None

    def _save_cache(self, query: str, meta: Dict[str, str]):
        conn = sqlite3.connect(self.cache_db)
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO papers (digest, title, abstract) VALUES (?,?,?)",
            (self._digest(query), meta["title"], meta["abstract"]),
        )
        conn.commit()
        conn.close()

    # ----------------------------------------------------------
    # public API
    # ----------------------------------------------------------
    def run(self, tokens: List[str]) -> List[Dict]:
        out: List[Dict] = []
        for tok in tokens:
            cached = self._lookup_cache(tok)
            if cached:
                out.append({"token": tok, **cached})
                continue
            meta = self._query_crossref(tok) or self._query_pubmed(tok) or {}
            if meta:
                self._save_cache(tok, meta)
            out.append({"token": tok, **meta})
        return out

    # ----------------------------------------------------------
    # helpers
    # ----------------------------------------------------------
    def _query_crossref(self, query: str):
        try:
            resp = requests.get(CROSSREF_ENDPOINT.format(q=quote_plus(query)), timeout=10)
            resp.raise_for_status()
            items = resp.json()["message"].get("items", [])
            if items:
                item = items[0]
                return {
                    "title": item.get("title", [""])[0] if item.get("title") else "",
                    "abstract": item.get("abstract", ""),
                }
        except Exception:
            pass
        return None

    def _query_pubmed(self, query: str):
        try:
            search = requests.get(PUBMED_SEARCH.format(q=quote_plus(query)), timeout=10).json()
            ids = search.get("esearchresult", {}).get("idlist", [])
            if not ids:
                return None
            pid = ids[0]
            summary = requests.get(PUBMED_SUMMARY.format(pid=pid), timeout=10).json()
            result = summary.get("result", {}).get(pid, {})
            return {
                "title": result.get("title", ""),
                "abstract": result.get("summary", ""),
            }
        except Exception:
            pass
        return None
