# `create_til.py`

`create_til.py` powers a GitHub-issue-driven TIL publishing flow.

It reads an issue, optionally extracts article text from a URL in the issue body,
asks an OpenRouter model to generate metadata (title/slug/tags/snippet/summary),
writes a new Jekyll post into `_posts`,
downloads referenced images into `media/images`,
and opens a pull request that closes the source issue.

When a source URL has enough extractable content,
the script builds a short summary block and appends a source link.
If extraction fails or there is no URL, it falls back to treating the issue body as notes.

It also supports separate model selection for article-summary generation vs final-post generation,
with sensible defaults.

## Environment variables

**Configurable in GH Actions**

- `OPENROUTER_API_KEY` (required): API key used for OpenRouter chat completion requests.
- `REPO_OWNER` (optional): If set, the script exits unless the issue author matches this owner.
- `OPENROUTER_MODEL` (optional): Base/default OpenRouter model name. Defaults to `openai/gpt-4o`.
- `OPENROUTER_SUMMARY_MODEL` (optional): Model for URL/article summary generation. Defaults to `OPENROUTER_MODEL`, then `openai/gpt-4o`.
- `OPENROUTER_POST_MODEL` (optional): Model for final post metadata generation in notes/fallback flows. Defaults to `OPENROUTER_MODEL`, then `openai/gpt-4o`.

**Coming from GH Actions**:

- `GITHUB_TOKEN` (required): GitHub token used to read issue/repo data, create comments, and create the pull request.
- `ISSUE_NUMBER` (required): The numeric GitHub issue number to process.
- `GITHUB_REPOSITORY` (required): Repository slug in `owner/repo` format.

---

# `update_til_summary.py`

`update_til_summary.py` handles PR review-driven summary updates for TIL posts.

When you submit a "Request changes" review on a TIL PR, the workflow
reads your review body and updates the post's summary accordingly.

## Two modes

| Review body prefix | Behavior |
|---|---|
| `Change summary to:` | Replaces the summary blockquote with the exact text you provide. |
| `Suggestion:` | Re-fetches the source article, sends the current summary + your feedback to the LLM, and replaces the summary with the LLM's revision. |

Both modes also update the `snippet` in front matter to match the new summary.

Reviews that don't start with either prefix are ignored (the workflow exits cleanly).

### Examples

**Direct replacement:**

```
Change summary to: This article covers three techniques for optimizing
database queries in Rails: eager loading, counter caches, and query objects.
```

**LLM-assisted revision:**

```
Suggestion: Focus more on the security scanning recommendations
and less on the stakeholder interview process.
```

## Constraints

- Only runs on PRs whose branch name starts with `til/`.
- Only runs when the reviewer is the repository owner.
- `Suggestion:` mode requires a `source_url` in front matter (URL-based posts only).
  For notes-based posts, use `Change summary to:` instead.
- `Suggestion:` mode requires the `OPENROUTER_API_KEY` secret.

## Environment variables

**Configurable in GH Actions**

- `OPENROUTER_API_KEY` (required for `Suggestion:` mode): API key for OpenRouter.
- `OPENROUTER_MODEL` / `OPENROUTER_SUMMARY_MODEL` (optional): Model for summary regeneration.

**Coming from GH Actions**:

- `GITHUB_TOKEN` (required): GitHub token for API access and pushing commits.
- `PR_NUMBER` (required): The pull request number.
- `REVIEW_ID` (required): The review ID, used to fetch the review body via the API.
- `GITHUB_REPOSITORY` (required): Repository slug in `owner/repo` format.
