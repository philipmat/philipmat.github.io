# Plan: TIL Action Enhancements (v2)

Builds on plan-opus-01.md. All changes target existing files:

- `.github/workflows/til.yml`
- `.github/scripts/create_til.py`

No new files needed. No new dependencies.

---

## Enhancement 1: Skip Issues Labeled `enhancement`

### Workflow change (`.github/workflows/til.yml`)

Add a label exclusion to the existing `if` condition on the job:

```yaml
jobs:
  create-til:
    if: >-
      github.event.issue.user.login == github.repository_owner
      && !contains(github.event.issue.labels.*.name, 'enhancement')
```

### Script safety net (`create_til.py`)

Add a secondary check after fetching the issue via API (after the repo-owner check
at line 259), in case labels are added between the event firing and the script
running, or if the workflow is re-run manually:

```python
issue_labels = [label.get("name", "") for label in issue.get("labels", [])]
if "enhancement" in issue_labels:
    print("Issue is labeled 'enhancement'. Skipping TIL creation.")
    return
```

---

## Enhancement 3 & 4: Categories in Post Body and Front Matter

Categories are the same values as the existing LLM-generated tags, displayed
in a human-readable form. No additional LLM output is needed.

### Display casing rules

Tags are stored lowercase with hyphens (e.g. `web-development`, `ai`, `til`).
When converting to display categories:

1. Split on hyphens and title-case each word — except
2. Words that match a known acronym list are fully uppercased instead.

**Hardcoded acronym set:**

```python
KNOWN_ACRONYMS = {"til", "ai", "llm", "api", "sql", "url", "html", "css", "js", "cli"}
```

### New helper functions

```python
KNOWN_ACRONYMS = {"til", "ai", "llm", "api", "sql", "url", "html", "css", "js", "cli"}


def format_category_word(word: str) -> str:
    """Title-case a word, or uppercase it if it's a known acronym."""
    return word.upper() if word.lower() in KNOWN_ACRONYMS else word.title()


def tag_to_category(tag: str) -> str:
    """Convert a lowercase hyphenated tag to a display category name.

    Examples:
        "til"             -> "TIL"
        "ai"              -> "AI"
        "web-development" -> "Web Development"
        "llm-tools"       -> "LLM Tools"
    """
    return " ".join(format_category_word(word) for word in tag.split("-"))


def tags_to_categories(tags: List[str]) -> List[str]:
    return [tag_to_category(tag) for tag in tags]
```

### Ensure `til` is always in tags

In `normalize_tags`, after cleaning, insert `"til"` at position 0 if absent:

```python
def normalize_tags(tags: Any) -> List[str]:
    # ... existing cleaning logic ...
    if "til" not in cleaned:
        cleaned.insert(0, "til")
    return cleaned or ["til"]
```

This ensures the `TIL` category always appears in the output.

### Front matter — add `categories` field

Add after the `tags` line in the front matter assembly:

```yaml
tags: [til, databases, ai]
categories: [TIL, Databases, AI]
```

In the script:

```python
categories = tags_to_categories(tags)
category_yaml_list = ", ".join(categories)

front_matter_lines = [
    "---",
    "layout: post",
    f'title: "TIL: {yaml_escape(title)}"',
    f"tags: [{tag_list}]",
    f"categories: [{category_yaml_list}]",
    f'snippet: "{yaml_escape(snippet)}"',
]
```

### Post body — append categories footer

After the post body is finalized (all paths: with URL, unfetched URL, no URL),
append the categories line before writing to file:

```python
categories = tags_to_categories(tags)
post_body = post_body.rstrip() + f"\n\n*Categories: {', '.join(categories)}*"
```

This produces a line like `*Categories: TIL, Databases, AI*` rendered as
italic text, visually distinct from the post content.

---

## Enhancement 5: URL Summary as Blockquote with Positioned Comments

The most involved change. Touches URL parsing, LLM prompts, and post body
assembly.

### 5a. Replace URL extraction with body splitting

Replace `find_first_url` + `remove_first_url` with a single function that
captures the text before and after the URL:

```python
def split_body_around_url(text: str) -> Tuple[Optional[str], str, str]:
    """Split issue body into (url, text_before_url, text_after_url).

    Returns (None, full_text, "") if no URL is found.
    """
    match = re.search(r"https?://\S+", text)
    if not match:
        return None, text.strip(), ""
    raw = match.group(0)
    cleaned = raw.rstrip(TRAILING_URL_PUNCT)
    before = text[: match.start()].strip()
    after = text[match.start() + len(raw) :].strip()
    return cleaned, before, after
```

The existing `find_first_url` and `remove_first_url` functions can be removed.
Update call sites in `main()` accordingly:

```python
# Before (two separate calls):
raw_url, cleaned_url = find_first_url(issue_body)
url = cleaned_url
body_without_url = issue_body
if raw_url and cleaned_url:
    body_without_url = remove_first_url(issue_body, raw_url, cleaned_url)

# After (one call):
url, comments_before, comments_after = split_body_around_url(issue_body)
# comments_before = text before the URL; comments_after = text after the URL
```

### 5b. Update system prompt

```python
system_prompt = (
    "You are a helpful assistant that creates blog post metadata and summaries. "
    "When summarizing articles, produce a standalone summary of the article's "
    "key points — do NOT incorporate the user's personal comments into the summary. "
    "The user's comments will be displayed separately around the summary. "
    "You always respond with valid JSON and nothing else."
)
```

### 5c. Update `build_user_prompt_with_url` summary instruction

Change the `"summary"` field description from:

```
- "summary": A 1-2 paragraph summary of the article's key points. Write in first person
  as if I'm sharing what I learned. If I provided comments above, naturally weave
  them into the summary.
```

To:

```
- "summary": A 1-2 paragraph summary of the article's key points. Write in first person
  as if I'm sharing what I learned. Do NOT weave in my comments — summarize the article
  itself only. My comments will appear separately in the post.
```

The comments are still passed in the prompt (they help the LLM generate better
title/tags/slug), but the summary must stand alone.

Also update what is passed as "comments" to the prompt: pass the full surrounding
text (before + after combined) so the LLM has context, but label it clearly:

```python
all_comments = "\n\n".join(
    part for part in [comments_before, comments_after] if part
)
user_prompt = build_user_prompt_with_url(article_text, all_comments, issue_title)
```

### 5d. Assemble post body with positioned comments and blockquote

Replace the current post body assembly (lines 319-323 in the original):

```python
# Build blockquote from summary
def make_summary_blockquote(summary: str) -> str:
    lines = summary.strip().split("\n")
    quoted = "\n".join(f"> {line}" if line.strip() else ">" for line in lines)
    return f"> **Summary**\n>\n{quoted}"

post_body_parts = []

if comments_before:
    post_body_parts.append(comments_before)
    post_body_parts.append("")

post_body_parts.append(make_summary_blockquote(summary))
post_body_parts.append("")

if comments_after:
    post_body_parts.append(comments_after)
    post_body_parts.append("")

post_body_parts.append(f"Source: [{source_title}]({url})")
post_body = "\n".join(post_body_parts).strip()
```

### Example output

**Issue body:**
```
I found this really interesting.

https://example.com/vector-databases

This changes how I think about similarity search.
```

**Generated post:**
```markdown
I found this really interesting.

> **Summary**
>
> Vector databases store high-dimensional embeddings and use algorithms
> like HNSW to perform approximate nearest neighbor searches efficiently.
> Unlike traditional databases, they find the "closest" items in
> high-dimensional space rather than exact matches.

This changes how I think about similarity search.

Source: [How Vector Databases Work](https://example.com/vector-databases)

*Categories: TIL, Databases, AI*
```

### Edge cases

| Scenario | Behaviour |
|----------|-----------|
| No comments at all (URL only) | Summary blockquote + source link; no empty sections |
| All comments before URL | Comments → blockquote → source |
| All comments after URL | Blockquote → comments → source |
| Comments on both sides | Before → blockquote → after → source |
| URL fetch fails | Falls back to no-URL path; no blockquote; full issue body as content |

---

## Enhancement 6: Favor Issue Title for Post Title

Current code (line 355-357) prefers the LLM title. Flip priority so the issue
title is used when it is meaningful:

```python
# Before:
title = collapse_spaces(
    str(llm_data.get("title") or issue_title or "Untitled")
).strip()

# After:
if is_meaningful_title(issue_title):
    title = collapse_spaces(issue_title).strip()
else:
    title = collapse_spaces(
        str(llm_data.get("title") or "Untitled")
    ).strip()
```

The LLM still receives the issue title as "Suggested title:" in the prompt,
which helps it produce a coherent slug, tags, and summary. The script simply
overrides the returned title with the issue title when it's meaningful.

---

## Summary of All Changes

| File | Change | Enhancement |
|------|--------|-------------|
| `til.yml` | Add `enhancement` label exclusion to `if` condition | #1 |
| `create_til.py` | Add label check after issue fetch | #1 |
| `create_til.py` | Add `KNOWN_ACRONYMS` constant | #3, #4 |
| `create_til.py` | Add `format_category_word`, `tag_to_category`, `tags_to_categories` helpers | #3, #4 |
| `create_til.py` | Ensure `til` always in tags in `normalize_tags` | #3, #4 |
| `create_til.py` | Add `categories` field to front matter | #4 |
| `create_til.py` | Append `*Categories: ...*` footer to post body | #3 |
| `create_til.py` | Replace `find_first_url`/`remove_first_url` with `split_body_around_url` | #5 |
| `create_til.py` | Update system prompt (no comment weaving into summary) | #5 |
| `create_til.py` | Update `build_user_prompt_with_url` summary instruction | #5 |
| `create_til.py` | Add `make_summary_blockquote` helper | #5 |
| `create_til.py` | Assemble post body with before/after comments and blockquote summary | #5 |
| `create_til.py` | Flip title priority: issue title → LLM title fallback | #6 |

### Files NOT changed

- `_layouts/post.html` — No changes needed; categories appear as markdown
  text in the post body, not as template logic.
- `_includes/arc_post.html` — No changes needed.
- `.github/scripts/requirements.txt` — No new dependencies.
