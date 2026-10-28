#!/usr/bin/env python3
"""Find possible references to a retired company name in exported page content.

Reads pages from a JSON file, searches titles, bodies and attachment text for
the terms in config.json, and writes a CSV for a human reviewer. Nothing is
changed in the input.

Usage:
    python3 find_outdated_refs.py --input sample_content/pages.json --output findings.csv
"""
import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

from refs_common import iter_locations

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
CONTEXT_CHARS = 40
COLUMNS = [
    "finding_id", "priority", "source_type", "page_id", "title", "last_modified",
    "audience", "location", "start", "match_type", "matched_text", "context",
    "suggested_replacement", "review_decision", "reviewer_notes",
]


def phrase_regex(phrase):
    """Case-insensitive pattern for a literal phrase; spaces match any whitespace."""
    escaped = re.escape(phrase).replace(r"\ ", r"\s+")
    return rf"\b{escaped}\b"


def build_patterns(config):
    """Return a list of (match_type, compiled regex)."""
    # Longest first, so "Orbitwell Systems" wins over "Orbitwell".
    names = sorted(config["old_names"], key=len, reverse=True)
    variants = sorted(config["variants"], key=len, reverse=True)
    patterns = [
        ("old-name", re.compile("|".join(phrase_regex(n) for n in names), re.I)),
        ("variant", re.compile("|".join(phrase_regex(v) for v in variants), re.I)),
        ("ticket-reference", re.compile(rf"\b{re.escape(config['ticket_prefix'])}-\d+\b")),
        ("ambiguous", re.compile("|".join(phrase_regex(a) for a in config["ambiguous_phrases"]), re.I)),
    ]
    return patterns


def find_matches(text, patterns):
    """Return non-overlapping (start, end, match_type) tuples, earliest first."""
    candidates = []
    for match_type, regex in patterns:
        for m in regex.finditer(text):
            candidates.append((m.start(), m.end(), match_type))
    candidates.sort(key=lambda c: (c[0], -(c[1] - c[0])))
    kept, last_end = [], -1
    for start, end, match_type in candidates:
        if start >= last_end:
            kept.append((start, end, match_type))
            last_end = end
    return kept


def context_around(text, start, end):
    snippet = text[max(0, start - CONTEXT_CHARS): end + CONTEXT_CHARS]
    return " ".join(snippet.split())


def classify(match_type, context, config):
    """Downgrade ambiguous matches whose context contains generic words."""
    if match_type == "ambiguous":
        lowered = context.lower()
        if any(word in lowered for word in config["generic_context_words"]):
            return "ambiguous-likely-generic"
    return match_type


def priority_for(match_type, audience):
    if match_type in ("old-name", "variant"):
        return "high" if audience == "public" else "medium"
    if match_type == "ambiguous":
        return "medium"
    return "low"  # ticket-reference, ambiguous-likely-generic


def scan(pages, config):
    patterns = build_patterns(config)
    findings = []
    for page in pages:
        for location, text in iter_locations(page):
            for start, end, match_type in find_matches(text, patterns):
                context = context_around(text, start, end)
                match_type = classify(match_type, context, config)
                replace = config["new_name"] if match_type in ("old-name", "variant") else ""
                findings.append({
                    "priority": priority_for(match_type, page.get("audience", "internal")),
                    "source_type": page["source_type"],
                    "page_id": page["id"],
                    "title": page.get("title", ""),
                    "last_modified": page.get("last_modified", ""),
                    "audience": page.get("audience", "internal"),
                    "location": location,
                    "start": start,
                    "match_type": match_type,
                    "matched_text": text[start:end],
                    "context": context,
                    "suggested_replacement": replace,
                    "review_decision": "",
                    "reviewer_notes": "",
                })
    # Newest first within each group; the stable second sort keeps that order.
    findings.sort(key=lambda f: f["last_modified"], reverse=True)
    findings.sort(key=lambda f: (PRIORITY_RANK[f["priority"]], f["source_type"]))
    for number, finding in enumerate(findings, start=1):
        finding["finding_id"] = f"F{number:03d}"
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", required=True, type=Path, help="pages JSON file")
    parser.add_argument("--output", required=True, type=Path, help="CSV file to write")
    parser.add_argument("--config", default=Path(__file__).with_name("config.json"), type=Path)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    pages = json.loads(args.input.read_text(encoding="utf-8"))
    findings = scan(pages, config)

    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(findings)

    pages_with_findings = len({f["page_id"] for f in findings})
    print(f"Scanned {len(pages)} pages; {pages_with_findings} contain possible references.")
    print(f"Wrote {len(findings)} findings to {args.output}")
    for label, counts in (("By priority", Counter(f["priority"] for f in findings)),
                          ("By match type", Counter(f["match_type"] for f in findings))):
        print(f"{label}: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    sys.exit(main())
