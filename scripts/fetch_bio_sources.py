"""
Local fetcher for allowed biomedical sources (arXiv + PubMed).

- Pulls open literature (metadata only, no PDFs) for offline ingestion.
- Outputs JSONL records compatible with ingest_biomedical_corpus.py.
- Respects allowlist in config/hermes_bio_sources.json (if present).

Usage:
  python scripts/fetch_bio_sources.py --query "protein folding" --sources arxiv,pubmed --max-results 10 --out data/fetched/biomed.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree

import requests

CONFIG_PATH = Path("config/hermes_bio_sources.json")
DEFAULT_SOURCES = ["arxiv", "pubmed"]


def _load_allowlist() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"sources": []}


def _source_allowed(name: str, allowlist: Dict[str, Any]) -> bool:
    allowed = {
        s.get("name")
        for s in allowlist.get("sources", [])
        if str(s.get("status", "")).startswith("allowed")
    }
    return not allowed or name in allowed


def fetch_arxiv(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch metadata from arXiv Atom API (open, metadata only).
    """
    url = (
        "https://export.arxiv.org/api/query"
        f"?search_query=all:{requests.utils.quote(query)}&start=0&max_results={max_results}"
    )
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    root = ElementTree.fromstring(resp.content)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    records: List[Dict[str, Any]] = []
    for entry in root.findall("a:entry", ns):
        arxiv_id = entry.findtext("a:id", default="", namespaces=ns)
        title = (entry.findtext("a:title", default="", namespaces=ns) or "").strip()
        summary = (entry.findtext("a:summary", default="", namespaces=ns) or "").strip()
        published = entry.findtext("a:published", default="", namespaces=ns)
        authors = [a.findtext("a:name", default="", namespaces=ns) for a in entry.findall("a:author", ns)]
        records.append(
            {
                "id": arxiv_id or f"arxiv_{len(records)}",
                "source": "arXiv",
                "title": title,
                "snippet": summary,
                "authors": [a for a in authors if a],
                "published": published,
                "url": arxiv_id,
                "license": "open",
                "tags": ["arxiv", "preprint"],
            }
        )
    return records


def fetch_pubmed(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch metadata from PubMed (ESearch + ESummary, metadata only).
    """
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    search_url = f"{base}/esearch.fcgi"
    params = {"db": "pubmed", "retmode": "json", "term": query, "retmax": max_results}
    s_resp = requests.get(search_url, params=params, timeout=30)
    s_resp.raise_for_status()
    s_json = s_resp.json()
    ids = s_json.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []
    summary_url = f"{base}/esummary.fcgi"
    p_resp = requests.get(summary_url, params={"db": "pubmed", "retmode": "json", "id": ",".join(ids)}, timeout=30)
    p_resp.raise_for_status()
    p_json = p_resp.json().get("result", {})
    records: List[Dict[str, Any]] = []
    for pid in ids:
        rec = p_json.get(pid) or {}
        title = rec.get("title", "").strip()
        snippet = rec.get("elocationid", "") or rec.get("source", "")
        records.append(
            {
                "id": f"pubmed_{pid}",
                "source": "PubMed",
                "title": title,
                "snippet": snippet,
                "authors": rec.get("authors", []),
                "published": rec.get("pubdate", ""),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
                "license": "open",
                "tags": ["pubmed", "journal"],
            }
        )
    return records


FETCHERS = {
    "arxiv": fetch_arxiv,
    "pubmed": fetch_pubmed,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch biomedical literature metadata (arXiv, PubMed) for local ingestion.")
    parser.add_argument("--query", action="append", required=True, help="Query string (repeatable).")
    parser.add_argument("--sources", type=str, default="arxiv,pubmed", help="Comma-separated sources: arxiv,pubmed")
    parser.add_argument("--max-results", type=int, default=10, help="Max results per source per query.")
    parser.add_argument("--out", type=str, default="data/fetched/biomed.jsonl", help="Output JSONL path.")
    args = parser.parse_args()

    allowlist = _load_allowlist()
    sources = [s.strip().lower() for s in args.sources.split(",") if s.strip()]
    output: List[Dict[str, Any]] = []

    for src in sources:
        if src not in FETCHERS:
            print(f"[WARN] Skipping unsupported source: {src}", file=sys.stderr)
            continue
        src_name = "arXiv" if src == "arxiv" else "PubMed"
        if not _source_allowed(src_name, allowlist):
            print(f"[WARN] Source not allowlisted in config: {src_name}", file=sys.stderr)
            continue
        fetch_fn = FETCHERS[src]
        for q in args.query:
            try:
                recs = fetch_fn(q, max_results=args.max_results)
                output.extend(recs)
                print(f"[OK] {src_name} fetched {len(recs)} records for query '{q}'")
            except Exception as e:
                print(f"[WARN] {src_name} fetch failed for '{q}': {e}", file=sys.stderr)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for rec in output:
            f.write(json.dumps(rec) + "\n")
    print(f"[DONE] Wrote {len(output)} records to {out_path}")


if __name__ == "__main__":
    main()
