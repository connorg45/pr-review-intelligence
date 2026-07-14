from __future__ import annotations

import requests
from flask import current_app

from app.utils.time import parse_github_datetime


class GitHubSyncError(Exception):
    pass


class GitHubClient:
    def __init__(self) -> None:
        token = current_app.config.get("GITHUB_TOKEN", "")
        if not token:
            raise GitHubSyncError("GITHUB_TOKEN is not configured.")

        self.base_url = current_app.config["GITHUB_API_BASE_URL"].rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "pr-review-intelligence-platform",
            }
        )

    def _get(self, path: str, params: dict | None = None):
        try:
            response = self.session.get(f"{self.base_url}{path}", params=params, timeout=20)
        except requests.Timeout as exc:
            raise GitHubSyncError("GitHub API request timed out. Try again or lower the sync limit.") from exc
        except requests.RequestException as exc:
            raise GitHubSyncError("Could not reach the GitHub API. Check your network connection and token settings.") from exc

        if response.status_code >= 400:
            raise GitHubSyncError(self._build_error_message(response, path))
        return response.json()

    def _get_paginated(self, path: str, params: dict | None = None, max_items: int | None = None) -> list[dict]:
        items: list[dict] = []
        page = 1
        page_size = 100

        while True:
            page_params = {**(params or {}), "page": page, "per_page": page_size}
            payload = self._get(path, params=page_params)
            if not isinstance(payload, list):
                raise GitHubSyncError("GitHub returned an unexpected response while reading paginated data.")

            items.extend(payload)
            if max_items is not None and len(items) >= max_items:
                return items[:max_items]
            if len(payload) < page_size:
                return items
            page += 1

    def _build_error_message(self, response: requests.Response, path: str) -> str:
        try:
            payload = response.json()
            message = payload.get("message", response.text)
        except ValueError:
            message = response.text

        if response.status_code == 401:
            return "GitHub rejected the token. Confirm that GITHUB_TOKEN is valid and not expired."
        if response.status_code == 403:
            if response.headers.get("X-RateLimit-Remaining") == "0":
                return "GitHub API rate limit exceeded for this token. Wait a bit and try again."
            return "GitHub denied access. Confirm the token has repository metadata, pull request, and contents read access."
        if response.status_code == 404:
            return f"GitHub could not find '{path}'. Check the owner, repository name, and token access."
        return f"GitHub API error ({response.status_code}): {message}"

    def fetch_repository(self, owner: str, name: str) -> dict:
        payload = self._get(f"/repos/{owner}/{name}")
        return {
            "github_repo_id": payload["id"],
            "owner": payload["owner"]["login"],
            "name": payload["name"],
            "full_name": payload["full_name"],
        }

    def fetch_pull_requests(self, owner: str, name: str, limit: int) -> list[dict]:
        return self._get_paginated(
            f"/repos/{owner}/{name}/pulls",
            params={"state": "all", "sort": "updated", "direction": "desc"},
            max_items=limit,
        )

    def fetch_pull_request_files(self, owner: str, name: str, number: int) -> list[dict]:
        return self._get_paginated(f"/repos/{owner}/{name}/pulls/{number}/files")

    def fetch_first_review_at(self, owner: str, name: str, number: int):
        reviews = self._get_paginated(f"/repos/{owner}/{name}/pulls/{number}/reviews")
        if not reviews:
            return None
        ordered = sorted((review for review in reviews if review.get("submitted_at")), key=lambda review: review["submitted_at"])
        if not ordered:
            return None
        return parse_github_datetime(ordered[0]["submitted_at"])
