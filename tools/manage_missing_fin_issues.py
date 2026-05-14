#!/usr/bin/env python3
"""Open/close Mac-mini issues for InvestorConference audio missing FIN.srt."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


SOURCE_REPO = "wenchiehlee-money/InvestorConference"
TARGET_REPO = "ZhongZheng782/Mac-mini"
API_ROOT = "https://api.github.com"
LABELS = ["generate-FIN", "auto-generated", "InvestorConference"]
STEM_RE = re.compile(r"^([A-Za-z0-9]+)_(\d{4})_q([1-4])$", re.I)


class GitHubClient:
    def __init__(self, token: str) -> None:
        self.token = token

    def request(self, method: str, path: str, payload: dict | None = None) -> dict | list | None:
        data = None
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(f"{API_ROOT}{path}", data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API {method} {path} failed: {exc.code} {detail}") from exc
        if not body:
            return None
        return json.loads(body.decode("utf-8"))


def issue_title(stem: str) -> str:
    return f"Generate FIN.srt: {stem}"


def issue_body(stem: str, audio_url: str, fin_path: str) -> str:
    m = STEM_RE.match(stem)
    if not m:
        raise ValueError(f"Invalid stem: {stem}")
    stock_id, year, quarter = m.groups()
    metadata = {
        "task_type": "generate_fin_srt",
        "source_repo": SOURCE_REPO,
        "stock_id": stock_id.upper() if not stock_id.isdigit() else stock_id,
        "year": year,
        "quarter": quarter,
        "stem": stem,
        "audio_url": audio_url,
        "expected_fin_srt_path": fin_path,
    }
    yaml_lines = [f'{key}: "{value}"' for key, value in metadata.items()]
    return (
        "InvestorConference detected audio with no FIN.srt.\n\n"
        "```yaml\n"
        + "\n".join(yaml_lines)
        + "\n```\n"
    )


def load_manifest(repo: Path) -> dict[str, str]:
    manifest_path = repo / "audio_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing {manifest_path}")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {str(k): str(v) for k, v in data.items() if str(v).startswith("https://")}


def list_open_issues(client: GitHubClient) -> dict[str, dict]:
    labels = urllib.parse.quote(",".join(["generate-FIN", "InvestorConference"]))
    issues_by_title: dict[str, dict] = {}
    page = 1
    while True:
        path = f"/repos/{TARGET_REPO}/issues?state=open&labels={labels}&per_page=100&page={page}"
        issues = client.request("GET", path)
        if not isinstance(issues, list) or not issues:
            break
        for issue in issues:
            if "pull_request" not in issue:
                issues_by_title[issue.get("title", "")] = issue
        page += 1
    return issues_by_title


def ensure_labels(client: GitHubClient) -> None:
    colors = {
        "generate-FIN": "0E8A16",
        "auto-generated": "C5DEF5",
        "InvestorConference": "5319E7",
    }
    for label in LABELS:
        try:
            client.request("GET", f"/repos/{TARGET_REPO}/labels/{urllib.parse.quote(label)}")
        except RuntimeError:
            client.request(
                "POST",
                f"/repos/{TARGET_REPO}/labels",
                {"name": label, "color": colors[label], "description": "Managed by InvestorConference automation"},
            )


def comment_and_close(client: GitHubClient, issue: dict, stem: str, fin_path: str) -> None:
    number = issue["number"]
    client.request(
        "POST",
        f"/repos/{TARGET_REPO}/issues/{number}/comments",
        {"body": f"Fixed: `{SOURCE_REPO}` now contains `{fin_path}` for `{stem}`."},
    )
    client.request("PATCH", f"/repos/{TARGET_REPO}/issues/{number}", {"state": "closed"})


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    token = (
        os.environ.get("ZhongZheng782_REPO_FILE_SYNC_ACT")
        or os.environ.get("ZHONGZHENG782_REPO_FILE_SYNC_ACT")
        or os.environ.get("GH_TOKEN")
    )
    if not token:
        print("ZhongZheng782_REPO_FILE_SYNC_ACT or GH_TOKEN is required", file=sys.stderr)
        return 2

    manifest = load_manifest(repo)
    client = GitHubClient(token)
    ensure_labels(client)
    open_issues = list_open_issues(client)

    created = 0
    closed = 0
    skipped = 0

    for stem, audio_url in sorted(manifest.items()):
        m = STEM_RE.match(stem)
        if not m:
            skipped += 1
            continue
        stock_id = m.group(1).upper() if not m.group(1).isdigit() else m.group(1)
        fin_path = f"{stock_id}/{stem}_FIN.srt"
        title = issue_title(stem)
        issue = open_issues.get(title)

        if (repo / fin_path).exists():
            if issue:
                comment_and_close(client, issue, stem, fin_path)
                closed += 1
            continue

        if issue:
            skipped += 1
            continue

        client.request(
            "POST",
            f"/repos/{TARGET_REPO}/issues",
            {
                "title": title,
                "body": issue_body(stem, audio_url, fin_path),
                "labels": LABELS,
            },
        )
        created += 1

    print(f"[missing-fin] created={created} closed={closed} skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
