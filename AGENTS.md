# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Jekyll-based personal blog hosted at philipm.at (GitHub Pages). Posts live in `_posts/`, drafts in `drafts/`. The site uses Kramdown (GFM mode) + Rouge for syntax highlighting, with no JavaScript build pipeline.

## Build & Development Commands

Run via Docker (preferred, no Ruby setup needed):
```bash
./run.sh   # starts Jekyll with --watch on http://localhost:4000
```

Or via Rake (requires system Ruby):
```bash
rake dev       # Jekyll --watch
rake build     # one-shot build
rake rebuild   # clean + build
rake clean     # remove _site/
```

Publishing workflow:
```bash
rake drafts           # list/manage drafts interactively
rake publish[file]    # promote draft → _posts/ with today's date
rake pmat:upload      # rsync built site to philipm.at
```

## Post Format

Published posts go in `_posts/YYYY-MM-DD-slug.md`. Front matter:
```yaml
---
layout: post
title: "Title Here"
tags: [tag1, tag2]
snippet: "One-sentence summary shown in archives."
# Optional fields:
has_tldr: yes
source_url: "https://..."   # for TIL posts that summarize an article
---
```

TIL posts that summarize an article use a blockquote immediately after front matter for the summary paragraph.

Markdown line limit: 120 chars (per `.markdownlint.json`).

## TIL Automation Pipeline

The primary content creation path is via GitHub Issues → automated PR:

1. **Create issue** — title = post idea, body = URL and/or notes
2. **`til.yml` workflow** fires → runs `.github/scripts/create_til.py`
   - Fetches article text via `trafilatura`
   - Downloads referenced images to `media/images/`
   - Calls OpenRouter LLM (default: `openai/gpt-5-mini`) to generate title, slug, tags, snippet, and summary
   - Creates `_posts/YYYY-MM-DD-slug.md` on branch `til/<slug>`
   - Opens a PR that closes the issue
3. **Review PR** — if summary needs changes, comment with `Change summary to: <text>` or `Suggestion: <feedback>` → `til_review.yml` updates the post
4. **Approve PR** → `auto-merge-on-approval.yml` auto-merges

Required secrets for automation: `OPENROUTER_API_KEY`, `GITHUB_TOKEN`.

Python scripts entry points: `.github/scripts/create_til.py`, `.github/scripts/update_til_summary.py`. Prompts: `.github/scripts/prompts/`.

## Tags

Reuse existing tags where possible — the automation explicitly tries to match existing tags. Tags are listed in posts' front matter as a YAML list.

## Layouts & Includes

- `_layouts/base.html` — root HTML shell
- `_layouts/post.html` — wraps `base.html`, renders date + tags
- `_includes/sidebar.html` — bio + project links
- `_includes/post.html` — post list item (used on index/archive)

Static pages (about, contact, categories, archive) live at repo root.
