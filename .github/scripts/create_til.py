import json
import os
import re
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
import trafilatura

GITHUB_API = "https://api.github.com"
OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"
# other options:
# - openrouter/auto -- automatically selects the model
# - ?
# See https://gist.github.com/philipmat/bb8d3b7a6269191e693b8930044094d9
#   for experiments in summarizing.
DEFAULT_OPENROUTER_MODEL = "openai/gpt-5-mini"

TRAILING_URL_PUNCT = ")].,!?:;\"'"
PROMPT_DIR = os.path.join(os.path.dirname(__file__), "prompts")
IMAGE_PLACEHOLDER_RE = re.compile(r"\[\[IMAGE_\d+\]\]")
STANDALONE_URL_RE = re.compile(r"(?m)^(https?://\S+)\s*$")

MD_IMAGE_RE = re.compile(
    r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", re.IGNORECASE
)
HTML_IMAGE_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)


def load_prompt_text(filename: str) -> str:
    path = os.path.join(PROMPT_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing prompt file: {path}") from exc


def load_prompt_lines(filename: str) -> List[str]:
    return load_prompt_text(filename).splitlines()


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

    Only treats a URL as the article source when it is on its own line and
    starts at the beginning of that line.

    Returns (None, full_text, "") if no standalone URL line is found.
    """
    match = STANDALONE_URL_RE.search(text)
    if not match:
        return None, text.strip(), ""
    raw = match.group(1)
    cleaned = raw.rstrip(TRAILING_URL_PUNCT)
    before = text[: match.start()].strip()
    after = text[match.end() :].strip()
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


def has_til_prefix(title: str) -> bool:
    return collapse_spaces(title).lower().startswith("til: ")


def format_til_title(title: str, add_prefix: bool) -> str:
    normalized = collapse_spaces(title)
    if add_prefix and normalized and not has_til_prefix(normalized):
        return f"TIL: {normalized}"
    return normalized


def extract_images(body: str) -> Tuple[str, List[Dict[str, str]]]:
    matches: List[Dict[str, str]] = []

    for match in MD_IMAGE_RE.finditer(body):
        matches.append(
            {
                "start": match.start(),
                "end": match.end(),
                "url": match.group(2).strip(),
                "alt": match.group(1).strip(),
            }
        )

    for match in HTML_IMAGE_RE.finditer(body):
        tag = match.group(0)
        src_match = re.search(r"\bsrc=(['\"])(.*?)\1", tag, re.IGNORECASE)
        if not src_match:
            continue
        alt_match = re.search(r"\balt=(['\"])(.*?)\1", tag, re.IGNORECASE)
        matches.append(
            {
                "start": match.start(),
                "end": match.end(),
                "url": src_match.group(2).strip(),
                "alt": alt_match.group(2).strip() if alt_match else "",
            }
        )

    if not matches:
        return body, []

    matches.sort(key=lambda item: item["start"])
    updated = body
    for idx, match in enumerate(matches, start=1):
        match["placeholder"] = f"[[IMAGE_{idx}]]"

    for match in sorted(matches, key=lambda item: item["start"], reverse=True):
        updated = updated[: match["start"]] + match["placeholder"] + updated[match["end"] :]

    return updated, matches


def strip_image_placeholders(text: str) -> str:
    return IMAGE_PLACEHOLDER_RE.sub("", text).strip()


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
    api_key: str, system_prompt: str, user_prompt: str, model: str
) -> Dict[str, Any]:
    response = requests.post(
        OPENROUTER_API,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
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
    prompt.extend(load_prompt_lines("user_prompt_with_url_tail.txt"))
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
    prompt.extend(load_prompt_lines("user_prompt_no_url_tail.txt"))
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


def guess_image_extension(url: str, content_type: Optional[str]) -> str:
    if content_type:
        mime = content_type.split(";", 1)[0].strip().lower()
        mapping = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/svg+xml": ".svg",
        }
        if mime in mapping:
            return mapping[mime]
        if mime.startswith("image/"):
            suffix = mime.split("/", 1)[1].split("+", 1)[0]
            if suffix:
                return f".{suffix}"

    parsed = urlparse(url)
    ext = os.path.splitext(parsed.path)[1].lower()
    if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
        return ".jpg" if ext == ".jpeg" else ext
    return ".png"


def insert_images_into_body(
    post_body: str, images: List[Dict[str, str]], filename: str
) -> Tuple[str, List[str], List[str]]:
    if not images:
        return post_body, [], []

    images_dir = os.path.join("media", "images")
    os.makedirs(images_dir, exist_ok=True)
    base_stem = os.path.splitext(filename)[0]
    saved_paths: List[str] = []
    failures: List[str] = []

    for idx, image in enumerate(images, start=1):
        url = image["url"]
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            failures.append(f"{image['placeholder']} -> {url} ({exc})")
            continue

        extension = guess_image_extension(url, response.headers.get("Content-Type"))
        image_name = f"{base_stem}-{idx}{extension}"
        image_path = os.path.join(images_dir, image_name)
        with open(image_path, "wb") as handle:
            handle.write(response.content)
        saved_paths.append(image_path)

        alt_text = collapse_spaces(image.get("alt", "")) or "image"
        markdown = f"![{alt_text}](/media/images/{image_name})"
        post_body = post_body.replace(image["placeholder"], markdown)

    return post_body, saved_paths, failures


def main() -> None:
    github_token = get_env("GITHUB_TOKEN")
    openrouter_api_key = get_env("OPENROUTER_API_KEY")
    openrouter_model = get_env("OPENROUTER_MODEL", required=False) or DEFAULT_OPENROUTER_MODEL
    openrouter_summary_model = (
        get_env("OPENROUTER_SUMMARY_MODEL", required=False) or openrouter_model
    )
    openrouter_post_model = (
        get_env("OPENROUTER_POST_MODEL", required=False) or openrouter_model
    )
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
    raw_issue_body = issue.get("body") or ""
    issue_body, images = extract_images(raw_issue_body)
    issue_body_for_prompt = strip_image_placeholders(issue_body)

    if repo_owner_env and issue_user != repo_owner_env:
        print("Issue author is not repository owner. Exiting.")
        return

    issue_labels = [str(label.get("name", "")).lower() for label in issue.get("labels", [])]
    if "enhancement" in issue_labels or "bug" in issue_labels:
        print("Issue is labeled 'enhancement' or 'bug'. Skipping TIL creation.")
        return

    url, comments_before, comments_after = split_body_around_url(issue_body)
    comments_before_prompt = strip_image_placeholders(comments_before)
    comments_after_prompt = strip_image_placeholders(comments_after)

    if not issue_body.strip():
        post_comment(
            owner,
            repo,
            issue_number,
            github_token,
            "Could not create TIL: issue body is empty.",
        )
        return

    system_prompt = load_prompt_text("system_prompt.txt").strip()

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
                part for part in [comments_before_prompt, comments_after_prompt] if part
            )
            user_prompt = build_user_prompt_with_url(
                article_text, all_comments, issue_title
            )
            llm_data = openrouter_request(
                openrouter_api_key,
                system_prompt,
                user_prompt,
                openrouter_summary_model,
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
            notes_for_prompt = issue_body_for_prompt or issue_title.strip()
            user_prompt = build_user_prompt_no_url(notes_for_prompt, issue_title)
            llm_data = openrouter_request(
                openrouter_api_key,
                system_prompt,
                user_prompt,
                openrouter_post_model,
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
        notes_for_prompt = issue_body_for_prompt or issue_title.strip()
        user_prompt = build_user_prompt_no_url(notes_for_prompt, issue_title)
        llm_data = openrouter_request(
            openrouter_api_key,
            system_prompt,
            user_prompt,
            openrouter_post_model,
        )
        post_body = notes_text

    if is_meaningful_title(issue_title):
        title = collapse_spaces(issue_title).strip()
    else:
        title = collapse_spaces(str(llm_data.get("title") or "Untitled")).strip()
    display_title = format_til_title(title, add_prefix=used_article)
    slug = sanitize_slug(str(llm_data.get("slug") or ""), title)
    tags = normalize_tags(llm_data.get("tags"))
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"{date_str}-{slug}.md"
    posts_dir = "_posts"
    os.makedirs(posts_dir, exist_ok=True)
    file_path = os.path.join(posts_dir, filename)
    if os.path.exists(file_path):
        filename = f"{date_str}-{slug}-{issue_number}.md"
        file_path = os.path.join(posts_dir, filename)

    post_body, image_paths, image_failures = insert_images_into_body(
        post_body, images, filename
    )

    summary_text = llm_data.get("summary") if used_article else ""
    snippet_source = summary_text or post_body
    snippet = ensure_snippet(str(llm_data.get("snippet") or ""), snippet_source)

    tag_list = ", ".join(tags)
    front_matter_lines = [
        "---",
        f"layout: post",
        f'title: "{yaml_escape(display_title)}"',
        f"tags: [{tag_list}]",
        f'snippet: "{yaml_escape(snippet)}"',
    ]
    if url:
        front_matter_lines.append(f"source_url: {url}")
    front_matter_lines.append("---")

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
    run_git(["add", file_path, *image_paths])
    run_git(["commit", "-m", f"Add {display_title}"])
    run_git(["push", "-u", "origin", branch_name])

    repo_info = request_json("GET", f"{GITHUB_API}/repos/{owner}/{repo}", github_token)
    base_branch = repo_info.get("default_branch", "main")

    pr_body_lines = [f"Closes #{issue_number}."]
    if url:
        pr_body_lines.append(f"Source: {url}")
    if image_failures:
        pr_body_lines.append("")
        pr_body_lines.append("Image download failures (placeholders left in post):")
        pr_body_lines.extend(f"- {failure}" for failure in image_failures)
    pr_body = "\n".join(pr_body_lines)

    pr_payload = {
        "title": display_title,
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
