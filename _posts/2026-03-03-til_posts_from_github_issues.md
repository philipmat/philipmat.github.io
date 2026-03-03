---
layout: post
title: Automating TIL Posts from GitHub Issues
snippet: A GitHub Actions workflow that turns a GitHub issue into a TIL blog post using an LLM to fetch, summarize, and tag the content.
---

I read a lot of things on the internet and rarely write about them.
The friction of opening an editor, writing front matter, crafting a summary,
and opening a PR is just high enough that it doesn't happen.
So I set up a workflow to do most of it for me.

The idea: create a GitHub issue with a link (or just some notes), and a
GitHub Action kicks off, fetches the article, asks an LLM to summarize it
and generate tags, then opens a PR with a ready-to-publish TIL post.
All I have to do is review and merge.

## How It Works

The workflow lives in `.github/workflows/til.yml` and triggers on any
issue I open on the repository (it checks the issue author against the
repo owner, so it ignores issues from anyone else).

When it fires, a Python script (`.github/scripts/create_til.py`) does
the following:

1. **Fetches the issue** via the GitHub API -- title and body.
2. **Extracts a URL** from the body if one is present.
   If found, [trafilatura] fetches the page and strips it down to
   the main article text, dropping nav, ads, and boilerplate.
3. **Calls OpenRouter** (GPT-4o) with the article content and any notes
   I added to the issue body. The LLM returns a JSON object with a title,
   URL slug, 1-2 paragraph summary, a one-line snippet, and a set of tags.
4. **Assembles the post** -- front matter plus body -- and writes it to
   `_posts/YYYY-MM-DD-{slug}.md`.
5. **Opens a PR** and posts a comment on the original issue with a link to it.

If there's no URL in the issue, the body text is used directly as the post content
and the LLM only generates the metadata (title, slug, tags).

## The Post Format

Each generated post gets the standard `layout: post` front matter plus
a few extra fields:

```yaml
---
layout: post
title: "TIL: How Vector Databases Work"
tags: [databases, ai, embeddings]
source_url: https://example.com/the-article
snippet: A look at approximate nearest neighbor search in vector databases.
---
```

The `snippet` field is already used by the archive page template,
so TIL posts show up with descriptions in the archive without
any template changes. The `tags` are stored for future use --
the site doesn't render them yet.

## What I Had to Set Up

One secret in the repo: `OPENROUTER_API_KEY`.
That's it. The `GITHUB_TOKEN` is provided automatically by Actions.

The full plan for this workflow is in [plan-opus.md] in the repo root,
including edge case handling, prompt design, and cost estimates.

This work was done using Claude Opus for planning,
Codex for implementation (with an alternative by Kimi),
and Sonnet for review.

[trafilatura]: https://trafilatura.readthedocs.io/
[plan-opus.md]: /docs/features/til_action/plan-opus-01.md
