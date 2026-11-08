---
title: "Case study: keeping docs current at release speed"
description: A small working pipeline that checks docs against product facts, prepares AI drafting prompts and keeps a person in charge of what gets published.
---

# Case study: keeping docs current at release speed

**What this is:** a working demo, built on a fictional product and synthetic
data, of how I would keep documentation in step with frequent releases.
Code: [docs-pipeline-demo on GitHub](https://github.com/dagmar-tech/docs-pipeline-demo).

## The problem

When a product ships often, docs and help content fall behind, and any AI
assistant that answers customers from those docs repeats the mistakes.
Rewriting by hand does not scale. Letting an AI rewrite pages without checks
is not safe.

## The approach

Three layers, each with a clear owner.

1. **Detect.** A script compares every page with a product-facts file and the
   release notes. It flags renamed terms still in use, numbers that changed,
   broken links and pages a release touched that nobody has re-verified. It is
   deterministic: it reports only what it can prove.
2. **Draft.** For each affected page, the pipeline builds a prompt with the
   rules, the facts, the release changes and the current page. Claude returns a
   draft, a change summary and a list of questions it could not answer. The
   prompt says to ask rather than guess.
3. **Review.** A person checks every draft, whether a human or an AI wrote it,
   against a short checklist, tries the steps in the product, and only then
   marks the page as verified. Every mistake goes into a log and becomes a rule
   in the next prompt.

A fourth script ranks the most-asked support topics and their trend, so the
next fix is chosen from data.

## What happened on the sample data

The repository's history is staged to show one release going through the
pipeline. Each step is a commit on a pull request, and the GitHub Action runs
the drift check on every push.

| Step | Drift check |
|---|---|
| Baseline, all pages verified for 2026.10 | Passes, 0 findings |
| Release notes and new product facts added | Fails: 5 stale, 5 need review |
| Claude-drafted updates applied | Fails: 1 error. The draft linked to a page that does not exist. |
| A person fixes the link | Passes, 5 pages still wait for verification |
| New page added, pages verified for 2026.11 | Passes, 0 findings |

The history is replayed with a script, so it demonstrates the process rather
than recording real work. The sample tickets are synthetic, so no claims are
made about real ticket reduction.

The pull request, with every run: [Release 2026.11 docs update](https://github.com/dagmar-tech/docs-pipeline-demo/pull/1).

Related: [Outdated reference finder](../outdated-reference-finder/README.md), the real-work project this demo builds on.

## Decisions and trade-offs

- **Deterministic checks, not AI checks.** A check that can be wrong in
  unpredictable ways is hard to trust. Scripts prove facts, the AI drafts, a
  person decides.
- **One facts file.** Docs, drafts and any customer-facing AI can read the same
  source of truth.
- **Draft and publish are separate steps.** The AI never marks a page as current.
- **Structured release notes.** Mapping each change to the pages it affects is
  what makes the rest automatic.

## Limits and next steps

- No live AI call yet, by choice. The review step is the point.
- No screenshot or in-app tour checks. That needs a browser tool such as
  Playwright and a real product.
- Next: feed release notes from a real changelog, measure the time between a
  release and each page's verification, and compare topic counts before and
  after a fix.
