import json
import os
import re
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests
import trafilatura

GITHUB_API = "https://api.github.com"
OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"

TRAILING_URL_PUNCT = ")].,!?:;\"'"
KNOWN_ACRONYMS = {"til", "ai", "llm", "api", "sql", "url", "html", "css", "js", "cli"}


def get_env(name: str, required: bool = True) -> Optional[str]:
    value = os.getenv(name)
    if required and not value:
        raise SystemExit(f"Missing required env var: {name}")
    return value


def github_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def request_json(method: str, url: str, token: str, **kwargs: Any) -> Dict[str, Any]:
    response = requests.request(
        method, url, headers=github_headers(token), timeout=30, **kwargs
    )
    if response.status_code >= 400:
        raise SystemExit(f"GitHub API error {response.status_code}: {response.text}")
    return response.json()


def post_comment(
    owner: str, repo: str, issue_number: int, token: str, body: str
) -> None:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{issue_number}/comments"
    request_json("POST", url, token, json={"body": body})


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


def is_meaningful_title(title: str) -> bool:
    if not title or not title.strip():
        return False
    lower = title.strip().lower()
    return lower not in {"new til", "til", "today i learned", "today i learned post"}


def sanitize_slug(raw_slug: str, fallback: str) -> str:
    base = raw_slug or fallback or "til"
    base = base.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    if not slug:
        slug = "til"
    if len(slug) > 60:
        slug = slug[:60].rstrip("-")
    return slug


def normalize_tags(tags: Any) -> List[str]:
    if not isinstance(tags, list):
        return ["til"]
    cleaned: List[str] = []
    for tag in tags:
        if not isinstance(tag, str):
            continue
        normalized = re.sub(r"[^a-z0-9-]+", "-", tag.lower()).strip("-")
        if normalized:
            cleaned.append(normalized)
        if len(cleaned) >= 5:
            break
    if "til" not in cleaned:
        cleaned.insert(0, "til")
    return cleaned or ["til"]


def collapse_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def ensure_snippet(snippet: str, fallback_text: str) -> str:
    value = snippet or ""
    value = collapse_spaces(value)
    if not value:
        value = collapse_spaces(fallback_text)[:200]
    if len(value) > 200:
        value = value[:200].rstrip()
    return value


def yaml_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def format_category_word(word: str) -> str:
    """Title-case a word, or uppercase it if it's a known acronym."""
    return word.upper() if word.lower() in KNOWN_ACRONYMS else word.title()


def tag_to_category(tag: str) -> str:
    """Convert a lowercase hyphenated tag to a display category name."""
    return " ".join(format_category_word(word) for word in tag.split("-"))


def tags_to_categories(tags: List[str]) -> List[str]:
    return [tag_to_category(tag) for tag in tags]


def parse_llm_json(raw_text: str) -> Dict[str, Any]:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        stripped = raw_text.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```[a-zA-Z]*", "", stripped).strip()
            if stripped.endswith("```"):
                stripped = stripped[:-3].strip()
        return json.loads(stripped)


def openrouter_request(
    api_key: str, system_prompt: str, user_prompt: str
) -> Dict[str, Any]:
    response = requests.post(
        OPENROUTER_API,
        headers={
            "Authorization": f"Bearer {api_key}",
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
        timeout=60,
    )
    if response.status_code >= 400:
        raise SystemExit(f"OpenRouter error {response.status_code}: {response.text}")
    data = response.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    if not content:
        raise SystemExit("OpenRouter returned empty content")
    return parse_llm_json(content)


def build_user_prompt_with_url(
    article_text: str,
    comments: str,
    issue_title: Optional[str],
) -> str:
    prompt = [
        'I want to create a short "Today I Learned" blog post based on the following article.',
        "",
        "Article content:",
        "---",
        article_text,
        "---",
        "",
    ]
    if comments:
        prompt.extend(
            [
                "My additional thoughts/comments:",
                "---",
                comments,
                "---",
                "",
            ]
        )
    if issue_title and is_meaningful_title(issue_title):
        prompt.append(f"Suggested title: {issue_title}")
        prompt.append("")
    prompt.extend(
        [
            "Please respond with a JSON object containing:",
            '- "title": A concise, descriptive title for the blog post (do NOT prefix with "TIL:")',
            '- "slug": A URL-friendly slug (lowercase, hyphens only, no special characters, max 60 chars)',
            '- "summary": A 1-2 paragraph summary of the article\'s key points.',
            "  Do NOT weave in my comments -- summarize the article itself only.",
            "  My comments will appear separately in the post.",
            '- "tags": An array of 1-5 lowercase tags categorizing the content',
            '  (e.g., ["python", "web-development", "security"])',
            '- "snippet": A single sentence (max 200 chars) summarizing the post for an archive listing',
            "",
            "Respond with ONLY the JSON object, no markdown fences or other text.",
        ]
    )
    return "\n".join(prompt)


def build_user_prompt_no_url(body_text: str, issue_title: Optional[str]) -> str:
    prompt = [
        'I want to create a short "Today I Learned" blog post from my notes below.',
        "",
        "My notes:",
        "---",
        body_text,
        "---",
        "",
    ]
    if issue_title and is_meaningful_title(issue_title):
        prompt.append(f"Suggested title: {issue_title}")
        prompt.append("")
    prompt.extend(
        [
            "Please respond with a JSON object containing:",
            '- "title": A concise, descriptive title for the blog post (do NOT prefix with "TIL:")',
            '- "slug": A URL-friendly slug (lowercase, hyphens only, no special characters, max 60 chars)',
            '- "tags": An array of 1-5 lowercase tags categorizing the content',
            '- "snippet": A single sentence (max 200 chars) summarizing the post for an archive listing',
            "",
            'Do NOT include a "summary" field -- I will use my notes directly as the post body.',
            "Respond with ONLY the JSON object, no markdown fences or other text.",
        ]
    )
    return "\n".join(prompt)


def truncate_text(text: str, max_chars: int = 8000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars]


def run_git(args: List[str]) -> None:
    subprocess.run(["git", *args], check=True)


def make_summary_blockquote(summary: str) -> str:
    lines = summary.strip().split("\n")
    quoted = "\n".join(f"> {line}" if line.strip() else ">" for line in lines)
    return f"> **Summary**\n>\n{quoted}"


def main() -> None:
    github_token = get_env("GITHUB_TOKEN")
    openrouter_api_key = get_env("OPENROUTER_API_KEY")
    issue_number = int(get_env("ISSUE_NUMBER"))
    repository = get_env("GITHUB_REPOSITORY")
    repo_owner_env = get_env("REPO_OWNER", required=False)

    if not repository or "/" not in repository:
        raise SystemExit("Invalid GITHUB_REPOSITORY value")

    owner, repo = repository.split("/", 1)

    issue = request_json(
        "GET", f"{GITHUB_API}/repos/{owner}/{repo}/issues/{issue_number}", github_token
    )
    issue_user = issue.get("user", {}).get("login", "")
    issue_title = issue.get("title") or ""
    issue_body = issue.get("body") or ""

    if repo_owner_env and issue_user != repo_owner_env:
        print("Issue author is not repository owner. Exiting.")
        return

    issue_labels = [label.get("name", "") for label in issue.get("labels", [])]
    if "enhancement" in issue_labels:
        print("Issue is labeled 'enhancement'. Skipping TIL creation.")
        return

    url, comments_before, comments_after = split_body_around_url(issue_body)

    if not issue_body.strip():
        post_comment(
            owner,
            repo,
            issue_number,
            github_token,
            "Could not create TIL: issue body is empty.",
        )
        return

    system_prompt = (
        "You are a helpful assistant that creates blog post metadata and summaries. "
        "When summarizing articles, produce a standalone summary of the article's "
        "key points -- do NOT incorporate the user's personal comments into the summary. "
        "The user's comments will be displayed separately around the summary. "
        "You always respond with valid JSON and nothing else."
    )

    llm_data: Dict[str, Any]
    post_body: str
    has_url = bool(url)
    used_article = False

    if has_url:
        downloaded = trafilatura.fetch_url(url)
        extracted = (
            trafilatura.extract(
                downloaded, include_comments=False, include_tables=False
            )
            if downloaded
            else None
        )
        if extracted:
            extracted = extracted.strip()
        if extracted and len(extracted) >= 100:
            used_article = True
            article_text = truncate_text(extracted)
            all_comments = "\n\n".join(
                part for part in [comments_before, comments_after] if part
            )
            user_prompt = build_user_prompt_with_url(
                article_text, all_comments, issue_title
            )
            llm_data = openrouter_request(
                openrouter_api_key, system_prompt, user_prompt
            )
            summary = (llm_data.get("summary") or "").strip()
            if not summary:
                summary = all_comments or extracted[:400].strip()
            source_title = (
                issue_title
                if is_meaningful_title(issue_title)
                else llm_data.get("title", "Source")
            )
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
        else:
            notes_text = issue_body.strip()
            notes_for_prompt = notes_text or issue_title.strip()
            user_prompt = build_user_prompt_no_url(notes_for_prompt, issue_title)
            llm_data = openrouter_request(
                openrouter_api_key, system_prompt, user_prompt
            )
            post_body = notes_text
    else:
        notes_text = issue_body.strip()
        if not notes_text:
            post_comment(
                owner,
                repo,
                issue_number,
                github_token,
                "Could not create TIL: issue body is empty.",
            )
            return
        user_prompt = build_user_prompt_no_url(notes_text, issue_title)
        llm_data = openrouter_request(openrouter_api_key, system_prompt, user_prompt)
        post_body = notes_text

    if is_meaningful_title(issue_title):
        title = collapse_spaces(issue_title).strip()
    else:
        title = collapse_spaces(str(llm_data.get("title") or "Untitled")).strip()
    slug = sanitize_slug(str(llm_data.get("slug") or ""), title)
    tags = normalize_tags(llm_data.get("tags"))
    categories = tags_to_categories(tags)

    summary_text = llm_data.get("summary") if used_article else ""
    snippet_source = summary_text or post_body
    snippet = ensure_snippet(str(llm_data.get("snippet") or ""), snippet_source)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"{date_str}-{slug}.md"
    posts_dir = "_posts"
    os.makedirs(posts_dir, exist_ok=True)
    file_path = os.path.join(posts_dir, filename)
    if os.path.exists(file_path):
        filename = f"{date_str}-{slug}-{issue_number}.md"
        file_path = os.path.join(posts_dir, filename)

    tag_list = ", ".join(tags)
    category_yaml_list = ", ".join(categories)

    front_matter_lines = [
        "---",
        f"layout: post",
        f'title: "TIL: {yaml_escape(title)}"',
        f"tags: [{tag_list}]",
        f"categories: [{category_yaml_list}]",
        f'snippet: "{yaml_escape(snippet)}"',
    ]
    if url:
        front_matter_lines.append(f"source_url: {url}")
    front_matter_lines.append("---")

    post_body = post_body.rstrip() + f"\n\n*Categories: {', '.join(categories)}*"
    content = "\n".join(front_matter_lines) + "\n\n" + post_body.strip() + "\n"
    with open(file_path, "w", encoding="utf-8") as handle:
        handle.write(content)

    branch_name = f"til/{slug}-{issue_number}"

    run_git(["config", "user.name", "github-actions[bot]"])
    run_git(
        [
            "config",
            "user.email",
            "41898282+github-actions[bot]@users.noreply.github.com",
        ]
    )

    run_git(["checkout", "-b", branch_name])
    run_git(["add", file_path])
    run_git(["commit", "-m", f"Add TIL: {title}"])
    run_git(["push", "-u", "origin", branch_name])

    repo_info = request_json("GET", f"{GITHUB_API}/repos/{owner}/{repo}", github_token)
    base_branch = repo_info.get("default_branch", "main")

    pr_body_lines = [
        f"Closes #{issue_number}.",
    ]
    if url:
        pr_body_lines.append(f"Source: {url}")
    pr_body = "\n".join(pr_body_lines)

    pr_payload = {
        "title": f"TIL: {title}",
        "head": branch_name,
        "base": base_branch,
        "body": pr_body,
    }

    pr = request_json(
        "POST",
        f"{GITHUB_API}/repos/{owner}/{repo}/pulls",
        github_token,
        json=pr_payload,
    )
    pr_number = pr.get("number")
    pr_url = pr.get("html_url")

    if pr_number and pr_url:
        post_comment(
            owner,
            repo,
            issue_number,
            github_token,
            f"Created PR #{pr_number}: {pr_url}",
        )
    else:
        post_comment(
            owner,
            repo,
            issue_number,
            github_token,
            "Created a PR, but could not determine its URL.",
        )


if __name__ == "__main__":
    main()
