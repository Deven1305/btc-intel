# scripts/ingest_archive.py
"""
[Anaconda Prompt] python scripts/ingest_archive.py --input-dir path\to\html_files

Populates dark_web_records from HTML files you already have on disk —
e.g. pages exported from the DUTA-10K academic darknet-text corpus, or any
other already-acquired/legitimately-licensed local archive. This script
does NOT crawl anything: it only reads .html/.htm files that already exist
under --input-dir and runs the same extraction pipeline (address regex +
checksum validation, PGP fingerprint extraction, context/topic
classification, alias extraction) that the rest of BTC-Intel uses.

This is the "process pre-crawled archives instead of live Tor" path the
architecture doc calls out as the POC simplification (see Section 6's note
and the Week 6 build-schedule entry). It is also the right default for a
demo: no live network dependency, no flaky exit node, fully reproducible.

How to point this at DUTA-10K / Gwern data:
  1. Request/obtain the corpus through its own legitimate access process
     (see README.md "Datasets" section for the exact request links).
  2. Export or copy the page text/HTML you're licensed to use into a local
     folder.
  3. Run this script against that folder.

Each file is treated as one "page" with:
  onion_domain = the file's parent directory name (your own labelling)
  page_url     = a synthetic local reference, NOT a live URL
  archive_key  = the original filename, for traceability
"""
import argparse
import os
import sys
from pathlib import Path

import psycopg2

# repo root on sys.path so `services.*` imports work when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.common.btc_patterns import find_candidate_addresses
from services.common.btc_validate import is_valid_btc_address, classify_address_type
from services.content.pgp_extract import extract_pgp_fingerprints
from services.content.context import classify_context, classify_topic
from services.content.aliases import extract_aliases


def _context_window(text: str, idx: int, addr_len: int, radius: int = 250) -> str:
    start = max(0, idx - radius)
    end = min(len(text), idx + addr_len + radius)
    return text[start:end]


def process_one_file(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    records: list[dict] = []
    pgp_fps = extract_pgp_fingerprints(raw)
    aliases = extract_aliases(raw)
    topic = classify_topic(raw)

    seen_in_file: set[str] = set()
    for addr, addr_type in find_candidate_addresses(raw):
        if addr in seen_in_file:
            continue
        if not is_valid_btc_address(addr):
            continue
        seen_in_file.add(addr)
        idx = raw.find(addr)
        window = _context_window(raw, idx, len(addr)) if idx >= 0 else raw[:500]
        context_type, confidence = classify_context(window)
        records.append({
            "address": addr,
            "address_type": classify_address_type(addr) or addr_type,
            "context_type": context_type,
            "context_window": window,
            "confidence": confidence,
            "page_topic": topic,
            "onion_domain": path.parent.name,
            "page_url": f"local-archive://{path.name}",
            "archive_key": path.name,
            "pgp_fingerprints": pgp_fps,
            "aliases": aliases,
        })
    return records


def store_records(conn, records: list[dict]) -> int:
    if not records:
        return 0
    with conn.cursor() as cur:
        for r in records:
            cur.execute("""
                INSERT INTO dark_web_records
                    (address, address_type, context_type, context_window, confidence,
                     page_topic, onion_domain, page_url, archive_key, pgp_fingerprints, aliases)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (r["address"], r["address_type"], r["context_type"], r["context_window"],
                  r["confidence"], r["page_topic"], r["onion_domain"], r["page_url"],
                  r["archive_key"], r["pgp_fingerprints"], r["aliases"]))
    conn.commit()
    return len(records)


def main():
    ap = argparse.ArgumentParser(description="Ingest already-acquired archive HTML into dark_web_records.")
    ap.add_argument("--input-dir", required=True, help="Folder containing .html/.htm files to process")
    args = ap.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.is_dir():
        print(f"ERROR: {input_dir} is not a directory.")
        sys.exit(1)

    files = list(input_dir.rglob("*.html")) + list(input_dir.rglob("*.htm"))
    if not files:
        print(f"No .html/.htm files found under {input_dir}.")
        sys.exit(0)

    conn = psycopg2.connect(os.environ["POSTGRES_URI"])
    total = 0
    for f in files:
        try:
            recs = process_one_file(f)
            total += store_records(conn, recs)
        except Exception as e:
            print(f"  skip {f}: {e}")
    print(f"[OK] Ingested {total} dark_web_records from {len(files)} archive files.")


if __name__ == "__main__":
    main()
