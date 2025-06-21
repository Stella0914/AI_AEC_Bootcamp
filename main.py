"""CLI entry-point – parse PDF, extract citations, run Crew audit."""
from __future__ import annotations
import argparse
import re
from pathlib import Path
from typing import List
from pdfminer.high_level import extract_text

from crew_pipeline import CitationAuditCrew, CitationToken, TOKEN_REGEX

# crude sentence splitter
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

def extract_tokens(pdf_text: str) -> List[CitationToken]:
    tokens = []
    for section in ["Introduction", "Methods", "Results", "Discussion"]:
        # we won't parse structured sections; placeholder
        pass
    matches = list(re.finditer(TOKEN_REGEX, pdf_text))
    for m in matches:
        token = m.group(0)
        start = pdf_text.rfind("\n", 0, m.start()) + 1
        end = pdf_text.find("\n", m.end())
        sentence = pdf_text[start:end].strip()
        tokens.append(CitationToken(token=token, sentence=sentence, section="unknown"))
    return tokens

def main():
    parser = argparse.ArgumentParser(description="Audit citation consistency in a PDF.")
    parser.add_argument("pdf", type=Path, help="Path to PDF file")
    args = parser.parse_args()

    print("[*] Extracting text …")
    pdf_text = extract_text(str(args.pdf))
    citation_tokens = extract_tokens(pdf_text)
    print(f"[*] Found {len(citation_tokens)} citation tokens.")

    crew = CitationAuditCrew()
    result = crew.audit(citation_tokens)

    print("\n======== SUMMARY ========")
    for k, v in result.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
