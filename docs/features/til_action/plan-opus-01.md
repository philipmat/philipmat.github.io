# Plan: TIL Post Automation via GitHub Issues

## Overview

When you create an issue on the repo, a GitHub Action will:

1. Check you're the repo owner
2. Extract any URL from the issue body
3. Fetch and extract article content (if URL present)
4. Use OpenRouter (GPT-4o) to generate a title, slug, summary, and tags
5. Create a PR with the new TIL post in `_posts/`

## Files to Create

```
.github/
  workflows/
    til.yml              # GitHub Actions workflow
  scripts/
    create_til.py        # Main Python script
    requirements.txt     # Python dependencies
```

No existing files need to be modified.

## Workflow: `.github/workflows/til.yml`

**Trigger:** `issues` event, `opened` action only.

**Steps:**

| # | Step | Details |
|---|------|---------|
| 1 | **Filter by author** | `if:` condition checks `github.event.issue.user.login == github.repository_owner`. Exit early if not the owner. |
| 2 | **Checkout repo** | `actions/checkout@v4` |
| 3 | **Set up Python** | `actions/setup-python@v5`, Python 3.12 |
| 4 | **Install dependencies** | `pip install -r .github/scripts/requirements.txt` |
| 5 | **Run script** | Execute `create_til.py` with env vars: `GITHUB_TOKEN`, `OPENROUTER_API_KEY`, issue number, repo name |
| 6 | **Script creates branch + PR** | Uses `gh` CLI (pre-installed on runners) |

**Required Secrets:**

- `OPENROUTER_API_KEY` -- must be added to repo Settings > Secrets and variables > Actions

**Permissions:**

- `contents: write` (to push branch)
- `pull-requests: write` (to create PR)
- `issues: write` (to comment on issue with PR link)

## Script: `.github/scripts/create_til.py`

### Input

- Environment variables set by the workflow:
  - `ISSUE_NUMBER` -- the issue that triggered the workflow
  - `GITHUB_REPOSITORY` -- `owner/repo`
  - `GITHUB_TOKEN` -- for GitHub API calls and `gh` CLI
  - `OPENROUTER_API_KEY` -- for LLM calls
  - `REPO_OWNER` -- the repository owner's login, used for author filtering

### Logic Flow

```
1. Fetch issue data via GitHub REST API
   - GET /repos/{owner}/{repo}/issues/{number}
   - Extract: title, body, user.login

2. Parse issue body:
   a. Extract first URL found (regex: https?://...)
   b. Remaining text (body minus the URL line) = user's comments/notes

3. IF URL found:
   a. Fetch article content using trafilatura
      - trafilatura.fetch_url() to download
      - trafilatura.extract() to get main content as plain text
      - Strips navigation, ads, sidebars, footers automatically
   b. Send to OpenRouter (POST https://openrouter.ai/api/v1/chat/completions):
      - Model: openai/gpt-4o
      - System prompt: instructs the LLM to return structured JSON
      - User prompt contains:
        * Article content (truncated to ~8000 chars to stay within context)
        * User's comments from the issue body (if any)
        * Issue title (if non-empty and not a default like "New TIL")
      - Requested output: { title, slug, summary, tags }
   c. Assemble post body:
      - LLM-generated summary (1-2 paragraphs)
      - User's comments section (if any), under a "My thoughts:" heading or similar
      - Footer link: "Source: [Article Title](url)"

4. IF no URL:
   a. Post body = issue body text (used as-is)
   b. Send body to OpenRouter to generate: title, slug, tags only
      - No summarization needed; the content IS the post

5. Generate filename:
   - Date: today's date in YYYY-MM-DD format
   - Slug: from LLM response, sanitized (lowercase, hyphens, no special chars)
   - Result: _posts/YYYY-MM-DD-{slug}.md

6. Check for slug collision:
   - If _posts/YYYY-MM-DD-{slug}.md already exists, append issue number
   - e.g., _posts/YYYY-MM-DD-{slug}-42.md

7. Assemble markdown file with front matter (see Post Output Format below)

8. Create git branch:
   - Branch name: til/{slug}
   - git checkout -b til/{slug}

9. Commit and push:
   - git add _posts/YYYY-MM-DD-{slug}.md
   - git commit -m "Add TIL: {title}"
   - git push -u origin til/{slug}

10. Create PR via `gh pr create`:
    - Title: "TIL: {title}"
    - Body: summary + link to source issue
    - Base: main (or master, detected from repo)

11. Comment on the original issue:
    - POST /repos/{owner}/{repo}/issues/{number}/comments
    - Body: "Created PR #{pr_number}: {pr_url}"
```

### LLM Prompt Design

**System prompt:**

```
You are a helpful assistant that creates blog post metadata and summaries.
You always respond with valid JSON and nothing else.
```

**User prompt (when URL content is present):**

```
I want to create a short "Today I Learned" blog post based on the following article.

Article content:
---
{article_text (truncated to ~8000 chars)}
---

{IF user_comments}
My additional thoughts/comments:
---
{user_comments}
---
{ENDIF}

{IF issue_title and issue_title is meaningful}
Suggested title: {issue_title}
{ENDIF}

Please respond with a JSON object containing:
- "title": A concise, descriptive title for the blog post (do NOT prefix with "TIL:")
- "slug": A URL-friendly slug (lowercase, hyphens only, no special characters, max 60 chars)
- "summary": A 1-2 paragraph summary of the article's key points. Write in first person
  as if I'm sharing what I learned. If I provided comments above, naturally weave
  them into the summary.
- "tags": An array of 1-5 lowercase tags categorizing the content
  (e.g., ["python", "web-development", "security"])
- "snippet": A single sentence (max 200 chars) summarizing the post for an archive listing

Respond with ONLY the JSON object, no markdown fences or other text.
```

**User prompt (when no URL, just text):**

```
I want to create a short "Today I Learned" blog post from my notes below.

My notes:
---
{issue_body}
---

{IF issue_title and issue_title is meaningful}
Suggested title: {issue_title}
{ENDIF}

Please respond with a JSON object containing:
- "title": A concise, descriptive title for the blog post (do NOT prefix with "TIL:")
- "slug": A URL-friendly slug (lowercase, hyphens only, no special characters, max 60 chars)
- "tags": An array of 1-5 lowercase tags categorizing the content
- "snippet": A single sentence (max 200 chars) summarizing the post for an archive listing

Do NOT include a "summary" field -- I will use my notes directly as the post body.
Respond with ONLY the JSON object, no markdown fences or other text.
```

**OpenRouter API call:**

```python
response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "openai/gpt-4o",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    },
)
```

Temperature 0.3 keeps output focused and consistent while allowing slight creativity in phrasing.

### Dependencies (`requirements.txt`)

```
trafilatura>=1.12
requests>=2.31
```

`trafilatura` handles both HTTP fetching and content extraction.
`requests` is used for the OpenRouter and GitHub API calls.

## Post Output Format

### With a source URL

```yaml
---
layout: post
title: "TIL: How Vector Databases Actually Work"
tags: [databases, ai, embeddings]
source_url: https://example.com/vector-databases-explained
snippet: A look at how vector databases use approximate nearest neighbor search.
---

Vector databases store high-dimensional embeddings and use algorithms like
HNSW to perform approximate nearest neighbor searches efficiently. Unlike
traditional databases that rely on exact matching, vector DBs find the
"closest" items in high-dimensional space...

This explains why pgvector, while convenient, is slower than purpose-built
solutions like Pinecone or Weaviate for large-scale similarity search.

Source: [How Vector Databases Actually Work](https://example.com/vector-databases-explained)
```

### Without a source URL

```yaml
---
layout: post
title: "TIL: Python's walrus operator in list comprehensions"
tags: [python]
snippet: The walrus operator can eliminate redundant function calls in list comprehensions.
---

You can use the walrus operator (:=) in list comprehensions to avoid
calling an expensive function twice -- once in the filter and once
in the output expression:

results = [y for x in data if (y := expensive(x)) is not None]

This is way cleaner than the nested generator alternative.
```

### Front Matter Fields

| Field | Required | Source | Description |
|-------|----------|--------|-------------|
| `layout` | Always | Hardcoded | Always `post` |
| `title` | Always | LLM | Prefixed with `TIL: ` |
| `tags` | Always | LLM | Array of 1-5 lowercase tags |
| `source_url` | If URL present | Issue body | The original URL from the issue |
| `snippet` | Always | LLM | One-sentence summary for archive listing |

Notes:

- The `title` is prefixed with `TIL: ` by the script, not the LLM, to ensure consistency.
- The `snippet` field is already supported by the existing `_includes/arc_post.html` template,
  so TIL posts will display descriptions in the archive page automatically.
- The `source_url` is stored in front matter for potential future template use
  (e.g., rendering a link icon next to TIL posts).
- Tags are stored in front matter only; the site does not currently render them,
  but they're available for future use.

## Edge Cases

| Scenario | Handling |
|----------|----------|
| **Multiple URLs in body** | Only the first URL is extracted as the source. Others remain in the user's comments text. |
| **URL fetch failure** | trafilatura returns `None`. Fall back to treating it like a no-URL issue: use the issue body as the post content. Log a warning. Include the URL as `source_url` in front matter and as a link in the post body, but note the content couldn't be fetched. |
| **LLM API failure** | Script exits with non-zero code. The workflow fails. No partial PR is created. GitHub shows the failure on the Actions tab. |
| **LLM returns invalid JSON** | Attempt `json.loads()`. If it fails, try stripping markdown code fences and retry. If still invalid, exit with error. |
| **Slug collision** | Check if `_posts/YYYY-MM-DD-{slug}.md` exists. If so, append `-{issue_number}` to the slug. |
| **Very long articles** | Truncate article text to ~8000 characters before sending to LLM. This keeps the prompt within reasonable token limits and cost. |
| **Issue body is empty** | Exit gracefully with a comment on the issue: "Could not create TIL: issue body is empty." |
| **Non-article URLs** | trafilatura may return minimal content for PDFs, videos, etc. If extracted content is < 100 chars, treat it as a no-URL issue and use the issue body + title. |

## Workflow YAML Outline

```yaml
name: Create TIL Post

on:
  issues:
    types: [opened]

permissions:
  contents: write
  pull-requests: write
  issues: write

jobs:
  create-til:
    # Only run for issues created by the repo owner
    if: github.event.issue.user.login == github.repository_owner
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r .github/scripts/requirements.txt

      - name: Create TIL post
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
          ISSUE_NUMBER: ${{ github.event.issue.number }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          REPO_OWNER: ${{ github.repository_owner }}
        run: python .github/scripts/create_til.py
```

## Setup Required

1. **Add OpenRouter API key:**
   - Go to repo **Settings > Secrets and variables > Actions**
   - Click **New repository secret**
   - Name: `OPENROUTER_API_KEY`
   - Value: your OpenRouter API key

2. **Ensure GitHub Actions is enabled** on the repository
   (Settings > Actions > General > Allow all actions)

3. **No changes to existing files needed** --
   the new workflow and script are entirely additive.

## Cost Estimate

- **OpenRouter / GPT-4o:** ~$0.005-0.02 per TIL post
  (depends on article length; most will use < 10K input tokens)
- **GitHub Actions:** Free for public repos; ~0.5-1 minute per run on private repos

## Future Enhancements (Not in Scope)

- Render tags on the post layout or create tag index pages
- Add a distinct visual indicator for TIL posts (e.g., a "link" icon)
- Support re-running the workflow on issue edits (not just creation)
- Support for issue comments triggering updates to the PR
- Auto-merge the PR if the build passes
- Use `source_url` in templates to show an external link indicator
