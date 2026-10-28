# Outdated-reference finder

A small Python tool that finds possible references to a retired company name in exported wiki pages and tickets, and prepares them for human review.

> **About this demo:** The company, product, ticket keys, and content here are fictional and were created for this portfolio. The approach is based on my professional experience. The code and data were written from scratch for this demo and contain no employer content.

## Why this exists

When a company renames itself, the old name lingers in documentation, ticket descriptions, and attached files. Stale names confuse readers and erode trust in the rest of the documentation. Finding every occurrence by hand across hundreds of pages is slow, and a plain text search returns many matches that are not references at all.

This tool does the searching and ranking. A person decides what changes.

## What it does

1. **Find.** `find_outdated_refs.py` searches page titles, page bodies, and attachment text for:
   - the old company name (`Orbitwell Systems`)
   - variants (`Orbitwell`, `OrbSys`, `Orbit-Well`), case-insensitively
   - legacy ticket keys (`OWS-142`)
   - ambiguous phrases that may or may not be the old name (`Orbit Systems`)
2. **Report.** It writes a CSV, sorted by priority, then source type, then newest first.
3. **Review.** A reviewer opens the CSV and enters `approve` or `reject` for each row.
4. **Apply.** `apply_approved.py` writes a corrected **copy** of the content, changing only approved rows. The original is never modified.

## Quick start

Tested with Python 3.14. The scripts use only the standard library, so there is nothing to install.

```bash
python3 find_outdated_refs.py --input sample_content/pages.json --output findings.csv
```

Expected output:

```text
Scanned 7 pages; 6 contain possible references.
Wrote 15 findings to findings.csv
By priority: high=6, low=4, medium=5
By match type: ambiguous=1, ambiguous-likely-generic=1, old-name=5, ticket-reference=3, variant=5
```

Open `findings.csv` in a spreadsheet. For each row you accept, type `approve` in the `review_decision` column. Optionally, edit `suggested_replacement` or add a note in `reviewer_notes`. Then run:

```bash
python3 apply_approved.py --input sample_content/pages.json --reviewed findings.csv --output updated_pages.json
```

An example of the unreviewed report is in `examples/findings.csv`.

## Files

| File | Purpose |
|---|---|
| `find_outdated_refs.py` | Searches content and writes the findings CSV. |
| `apply_approved.py` | Applies approved rows to a copy of the content. |
| `refs_common.py` | Helper functions shared by both scripts. |
| `config.json` | The new name, old names, variants, ticket prefix, ambiguous phrases, and generic-context words. |
| `sample_content/pages.json` | Seven fictional pages, issues, and attachments. |
| `examples/findings.csv` | Report generated from the sample content. |

## The report columns

| Column | Meaning |
|---|---|
| `finding_id` | Row number in this report. |
| `priority` | `high`, `medium`, or `low` (see below). |
| `source_type`, `page_id`, `title`, `last_modified`, `audience` | Where the match was found. |
| `location` | `title`, `body`, or `attachment:<filename>`. |
| `start` | Character offset of the match within that location. |
| `match_type` | `old-name`, `variant`, `ticket-reference`, `ambiguous`, or `ambiguous-likely-generic`. |
| `matched_text`, `context` | The match and about 40 characters on each side. |
| `suggested_replacement` | The new name for names and variants. Empty for everything else. |
| `review_decision`, `reviewer_notes` | Filled in by the reviewer. |

## How priority is assigned

These rules are illustrative. Adjust them to your own content.

| Match type | Priority | Reason |
|---|---|---|
| Old name or variant on a public page | High | Customers see it. |
| Old name or variant on an internal page | Medium | Less visible, still confusing. |
| Ambiguous phrase | Medium | Needs a person to decide. |
| Ambiguous phrase with generic context words nearby | Low | Probably unrelated. |
| Legacy ticket key | Low | The key is a historical identifier and usually should not be renamed. A reviewer may want to add context instead. |

## Handling false positives

The old name contains a common word, "Systems". Searching for that word alone would flag every page about operating systems or embedded systems. The tool avoids this in two ways:

- **Common words are never searched alone.** In the sample content, the page `CONF-1004` talks about operating systems and embedded systems and produces no findings.
- **Ambiguous phrases are kept separate.** `Orbit Systems` could be the old name or a generic engineering phrase. If words from `generic_context_words` appear nearby, the match is downgraded to `ambiguous-likely-generic`. Otherwise it stays `ambiguous` for a reviewer to judge. In the sample, `Orbit Systems Engineering team` stays `ambiguous`, while `orbit systems dashboards for satellite trajectory data` is downgraded.

## Safety checks

- **The input is never modified.** `apply_approved.py` always writes a new file.
- **Only approved rows with a replacement are applied.** A row marked `approve` with an empty `suggested_replacement` is ignored. A reviewer can type a replacement in that column to apply one.
- **Stale offsets are skipped.** Each change is applied only if the text at the recorded offset still equals `matched_text`. If the page changed after the report was made, the row is skipped and reported, not guessed. I tested this by editing a page after generating the report. The three affected rows were skipped.

## Limitations

- **Replacement does not fix grammar.** The sample page `CONF-1001` says "an ORBITWELL account key". After replacement it reads "an Nimbra account key". The reviewer must correct the article, so the tool cannot be trusted to finish the job on its own.
- **No live connection.** The demo reads a local JSON file. A real deployment would first fetch content through the Jira and Confluence REST APIs. That fetching step is not included here.
- **Plain-text attachments only.** The sample attachments are `.txt` and `.csv`. Extracting text from PDFs and Office files needs separate libraries and is not covered.
- **Case-insensitive matching.** `ORBITWELL` and `Orbitwell` both match. If capitalization matters for your content, review the replacements.
- **One replacement per row.** The tool does not detect duplicates across pages or attachments that share content.

## Testing

I ran both scripts on Ubuntu 26.04.1 LTS with Python 3.14.4, using the sample content. I checked that:

- the finder produces the 15 findings shown in `examples/findings.csv`;
- `CONF-1004` produces no findings;
- approving nine rows, rejecting one, and leaving the rest blank changes only the nine approved rows;
- the input file is byte-for-byte unchanged after applying;
- re-scanning the corrected copy no longer reports the approved names;
- editing a page after the scan causes the affected rows to be skipped.

I did not test this against live Jira or Confluence, PDF or Office attachments, or large datasets.
