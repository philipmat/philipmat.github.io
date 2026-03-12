"""Handle PR review requests to update TIL post summaries.

Triggered when a 'Request changes' review is submitted on a TIL PR.
Supports two modes based on the review body prefix:

- "Change summary to:" — replaces the summary blockquote with the provided text
- "Suggestion:" — regenerates the summary via LLM incorporating the feedback
"""

import glob
import os
import re
import subprocess
import sys
from typing import Optional

import trafilatura

# Allow importing from the same directory as this script,
# since the workflow runs from the repo root.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from create_til import (  # noqa: E402
    GITHUB_API,
    DEFAULT_OPENROUTER_MODEL,
    get_env,
    load_prompt_text,
    make_summary_blockquote,
    openrouter_request,
    request_json,
    run_git,
    truncate_text,
)

# Regex to match the summary blockquote in the post body.
# The blockquote starts with "> **Summary**" and continues through
# consecutive lines that start with ">" (including blank ">").
SUMMARY_BLOCK_RE = re.compile(
    r"^(?=> \*\*Summary\*\*)"  # lookahead: first line starts with "> **Summary**"
    r"((?:>.*\n?)+)",  # capture all consecutive ">" lines
    re.MULTILINE,
)

CHANGE_SUMMARY_PREFIX = re.compile(r"(?i)^change\s+summary\s+to:\s*", re.MULTILINE)
SUGGESTION_PREFIX = re.compile(r"(?i)^suggestion:\s*", re.MULTILINE)


def find_post_file() -> Optional[str]:
    """Find the TIL post file in _posts/ that was added/modified in this branch."""
    # Look for markdown files in _posts/ that were changed relative to the base branch
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "origin/master...HEAD", "--", "_posts/"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]
        if files:
            return files[0]
    except subprocess.CalledProcessError:
        pass

    # Fallback: find the most recent .md file in _posts/
    posts = sorted(glob.glob("_posts/*.md"), reverse=True)
    return posts[0] if posts else None


def parse_front_matter(content: str) -> tuple[str, str]:
    """Split a post into front matter and body.

    Returns (front_matter_with_delimiters, body).
    """
    if not content.startswith("---"):
        return "", content
    end = content.find("---", 3)
    if end == -1:
        return "", content
    # Include the closing "---" and the newline after it
    end_of_fm = content.index("\n", end) + 1
    return content[:end_of_fm], content[end_of_fm:]


def extract_source_url(front_matter: str) -> Optional[str]:
    """Extract source_url from YAML front matter."""
    match = re.search(r"^source_url:\s*(.+)$", front_matter, re.MULTILINE)
    return match.group(1).strip() if match else None


def replace_summary_block(body: str, new_summary_text: str) -> str:
    """Replace the summary blockquote in the post body with a new one."""
    new_block = make_summary_blockquote(new_summary_text)
    new_body, count = SUMMARY_BLOCK_RE.subn(new_block + "\n", body, count=1)
    if count == 0:
        raise SystemExit(
            "Could not find a summary blockquote (> **Summary** ...) in the post. "
            "This command only works on URL-based TIL posts that have a summary."
        )
    return new_body


def update_snippet(front_matter: str, new_summary: str) -> str:
    """Update the snippet in front matter based on new summary text.

    Truncates to 200 chars.
    """
    snippet = re.sub(r"\s+", " ", new_summary).strip()
    if len(snippet) > 200:
        snippet = snippet[:200].rstrip()
    # Escape for YAML double-quoted string
    snippet = snippet.replace("\\", "\\\\").replace('"', '\\"')
    return re.sub(
        r'^snippet:\s*".*"$',
        f'snippet: "{snippet}"',
        front_matter,
        count=1,
        flags=re.MULTILINE,
    )


def build_revision_prompt(
    article_text: str, current_summary: str, feedback: str
) -> str:
    """Build a prompt asking the LLM to revise the summary based on feedback."""
    return "\n".join(
        [
            "I have a blog post summary that needs revision based on reviewer feedback.",
            "",
            "Original article content:",
            "---",
            article_text,
            "---",
            "",
            "Current summary:",
            "---",
            current_summary,
            "---",
            "",
            "Reviewer feedback:",
            "---",
            feedback,
            "---",
            "",
            "Please produce a revised 1-2 paragraph summary of the article that addresses "
            "the reviewer's feedback. Summarize the article itself only — do not incorporate "
            "personal comments.",
            "",
            'Respond with a JSON object containing a single key "summary" with the revised text.',
            "Respond with ONLY the JSON object, no markdown fences or other text.",
        ]
    )


def extract_current_summary(body: str) -> Optional[str]:
    """Extract the current summary text from the blockquote."""
    match = SUMMARY_BLOCK_RE.search(body)
    if not match:
        return None
    block = match.group(1)
    lines = block.strip().splitlines()
    # Skip "> **Summary**" and the blank ">" line after it
    text_lines = []
    past_header = False
    for line in lines:
        stripped = line.lstrip("> ").strip()
        if not past_header:
            if stripped.startswith("**Summary**"):
                continue
            if not stripped:
                past_header = True
                continue
            past_header = True
        # Remove the leading "> " prefix
        text = re.sub(r"^>\s?", "", line)
        text_lines.append(text)
    return "\n".join(text_lines).strip()


def post_pr_comment(
    owner: str, repo: str, pr_number: int, token: str, body: str
) -> None:
    """Post a comment on the PR."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{pr_number}/comments"
    request_json("POST", url, token, json={"body": body})


def fetch_review_body(
    owner: str, repo: str, pr_number: int, review_id: int, token: str
) -> str:
    """Fetch the review body from the GitHub API to avoid env-var escaping issues."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}/reviews/{review_id}"
    data = request_json("GET", url, token)
    return (data.get("body") or "").strip()


def main() -> None:
    github_token = get_env("GITHUB_TOKEN")
    openrouter_api_key = get_env("OPENROUTER_API_KEY", required=False)
    openrouter_model = (
        get_env("OPENROUTER_MODEL", required=False)
        or get_env("OPENROUTER_SUMMARY_MODEL", required=False)
        or DEFAULT_OPENROUTER_MODEL
    )
    pr_number = int(get_env("PR_NUMBER"))
    review_id = int(get_env("REVIEW_ID"))
    repository = get_env("GITHUB_REPOSITORY")

    if not repository or "/" not in repository:
        raise SystemExit("Invalid GITHUB_REPOSITORY value")

    owner, repo = repository.split("/", 1)
    review_body = fetch_review_body(owner, repo, pr_number, review_id, github_token)

    if not review_body:
        print("Review body is empty. Nothing to do.")
        return

    # Determine mode based on prefix
    change_match = CHANGE_SUMMARY_PREFIX.match(review_body)
    suggestion_match = SUGGESTION_PREFIX.match(review_body)

    if not change_match and not suggestion_match:
        print(
            "Review body does not start with 'Change summary to:' or 'Suggestion:'. "
            "Skipping."
        )
        return

    # Find the post file
    post_path = find_post_file()
    if not post_path or not os.path.exists(post_path):
        raise SystemExit(f"Could not find TIL post file in _posts/. Found: {post_path}")

    with open(post_path, "r", encoding="utf-8") as f:
        content = f.read()

    front_matter, body = parse_front_matter(content)

    if change_match:
        # Direct replacement mode
        new_summary = review_body[change_match.end() :].strip()
        if not new_summary:
            raise SystemExit(
                "No summary text provided after 'Change summary to:' prefix."
            )
        new_body = replace_summary_block(body, new_summary)
        new_front_matter = update_snippet(front_matter, new_summary)
        commit_msg = "Update TIL summary (direct replacement)"

    elif suggestion_match:
        # LLM regeneration mode
        if not openrouter_api_key:
            raise SystemExit("OPENROUTER_API_KEY is required for 'Suggestion:' mode.")

        feedback = review_body[suggestion_match.end() :].strip()
        if not feedback:
            raise SystemExit("No feedback provided after 'Suggestion:' prefix.")

        source_url = extract_source_url(front_matter)
        if not source_url:
            raise SystemExit(
                "Cannot regenerate summary: post has no source_url in front matter. "
                "Use 'Change summary to:' for posts without a source URL."
            )

        current_summary = extract_current_summary(body)
        if not current_summary:
            raise SystemExit("Cannot find current summary blockquote in the post.")

        # Fetch the original article
        downloaded = trafilatura.fetch_url(source_url)
        extracted = (
            trafilatura.extract(
                downloaded, include_comments=False, include_tables=False
            )
            if downloaded
            else None
        )
        if not extracted or len(extracted) < 100:
            raise SystemExit(
                f"Could not extract sufficient article text from {source_url}. "
                "Use 'Change summary to:' to provide the summary directly."
            )

        article_text = truncate_text(extracted.strip())
        system_prompt = load_prompt_text("system_prompt.txt").strip()
        user_prompt = build_revision_prompt(article_text, current_summary, feedback)

        llm_data = openrouter_request(
            openrouter_api_key, system_prompt, user_prompt, openrouter_model
        )
        new_summary = (llm_data.get("summary") or "").strip()
        if not new_summary:
            raise SystemExit("LLM returned empty summary.")

        new_body = replace_summary_block(body, new_summary)
        new_front_matter = update_snippet(front_matter, new_summary)
        commit_msg = "Update TIL summary (LLM revision)"

    else:
        # Unreachable — early return above guards this
        return

    # Write updated file
    new_content = new_front_matter + new_body
    with open(post_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    # Commit and push
    run_git(["config", "user.name", "github-actions[bot]"])
    run_git(
        [
            "config",
            "user.email",
            "41898282+github-actions[bot]@users.noreply.github.com",
        ]
    )
    run_git(["add", post_path])

    # Check if there are actually changes to commit
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
    if result.returncode == 0:
        print("No changes detected after update. The summary may already match.")
        post_pr_comment(
            owner,
            repo,
            pr_number,
            github_token,
            "No changes were needed — the summary already matches the requested update.",
        )
        return

    run_git(["commit", "-m", commit_msg])
    run_git(["push"])

    post_pr_comment(
        owner,
        repo,
        pr_number,
        github_token,
        f"Summary updated. {commit_msg}.",
    )
    print(f"Done. {commit_msg}.")


if __name__ == "__main__":
    main()
