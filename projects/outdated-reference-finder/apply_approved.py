#!/usr/bin/env python3
"""Apply reviewer-approved replacements to a COPY of the pages file.

Only rows whose review_decision is "approve" and whose suggested_replacement is
not empty are applied. The input file is never modified.

Usage:
    python3 apply_approved.py --input sample_content/pages.json \
        --reviewed findings.csv --output updated_pages.json
"""
import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from refs_common import iter_locations, set_location


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--reviewed", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    pages = json.loads(args.input.read_text(encoding="utf-8"))
    by_id = {page["id"]: page for page in pages}

    with args.reviewed.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    approved = [r for r in rows
                if r["review_decision"].strip().lower() == "approve"
                and r["suggested_replacement"].strip()]

    grouped = defaultdict(list)
    for row in approved:
        grouped[(row["page_id"], row["location"])].append(row)

    applied, skipped = 0, []
    for (page_id, location), group in grouped.items():
        page = by_id.get(page_id)
        if page is None:
            skipped.extend((r["finding_id"], "page not found") for r in group)
            continue
        text = dict(iter_locations(page)).get(location)
        if text is None:
            skipped.extend((r["finding_id"], "location not found") for r in group)
            continue
        # Work from the end of the text so earlier offsets stay valid.
        for row in sorted(group, key=lambda r: int(r["start"]), reverse=True):
            start = int(row["start"])
            end = start + len(row["matched_text"])
            if text[start:end] != row["matched_text"]:
                skipped.append((row["finding_id"], "text at offset no longer matches"))
                continue
            text = text[:start] + row["suggested_replacement"] + text[end:]
            applied += 1
        set_location(page, location, text)

    args.output.write_text(json.dumps(pages, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Rows reviewed: {len(rows)}; approved: {len(approved)}; applied: {applied}; skipped: {len(skipped)}")
    for finding_id, reason in skipped:
        print(f"  skipped {finding_id}: {reason}")
    print(f"Wrote {args.output} (input unchanged)")


if __name__ == "__main__":
    sys.exit(main())
