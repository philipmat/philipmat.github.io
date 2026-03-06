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
