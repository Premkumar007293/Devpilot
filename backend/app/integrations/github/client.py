"""Official GitHub REST API integration client with robust error handling and rate-limit tracking."""

import urllib.parse
from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger


class GitHubAPIException(Exception):
    """Base exception for GitHub API communication errors."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class GitHubClient:
    """Client for GitHub OAuth, user profile, repositories, and git tree traversal."""

    BASE_URL = "https://api.github.com"
    OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    OAUTH_TOKEN_URL = "https://github.com/login/oauth/access_token"

    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.client_id = settings.GITHUB_CLIENT_ID
        self.client_secret = settings.GITHUB_CLIENT_SECRET
        self.callback_url = settings.GITHUB_CALLBACK_URL or settings.GITHUB_REDIRECT_URI
        self.redirect_uri = settings.GITHUB_REDIRECT_URI or self.callback_url

    def get_authorization_url(self, state: str, login: Optional[str] = None) -> str:
        """Generate GitHub OAuth authorization URL with state CSRF token."""
        if not self.client_id:
            raise GitHubAPIException(
                "GitHub OAuth is not configured. GITHUB_CLIENT_ID is missing.",
                status_code=503,
            )

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.callback_url,
            "scope": "repo,read:user,user:email",
            "state": state,
        }
        if login:
            params["login"] = login
        return f"{self.OAUTH_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange temporary authorization code for user access token."""
        if not self.client_id or not self.client_secret:
            raise GitHubAPIException(
                "GitHub OAuth client credentials are not configured.",
                status_code=503,
            )

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.callback_url,
        }
        headers = {"Accept": "application/json"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(self.OAUTH_TOKEN_URL, json=payload, headers=headers)
                data = response.json()
            except Exception as exc:
                logger.error("Failed to exchange OAuth code: %s", str(exc))
                raise GitHubAPIException(f"Failed to communicate with GitHub OAuth service: {exc}", status_code=502)

            if "error" in data:
                error_desc = data.get("error_description", data.get("error"))
                logger.warning("GitHub OAuth exchange rejected: %s", error_desc)
                raise GitHubAPIException(f"OAuth code exchange failed: {error_desc}", status_code=400, details=data)

            if "access_token" not in data:
                raise GitHubAPIException("Malformed OAuth response: missing access_token", status_code=502)

            return data

    def _get_headers(self) -> Dict[str, str]:
        """Generate standard GitHub API headers."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "DevPilot-Platform/1.0",
        }
        if getattr(self, "token"):
            headers["Authorization"] = "Bearer " + str(getattr(self, "token"))
        return headers


    def _check_rate_limit(self, response: httpx.Response) -> None:
        """Inspect rate limit response headers."""
        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining is not None and int(remaining) == 0:
            reset_ts = response.headers.get("X-RateLimit-Reset", "soon")
            logger.warning("GitHub API rate limit exceeded. Reset at %s", reset_ts)
            raise GitHubAPIException(
                f"GitHub API rate limit exceeded. Resets at timestamp {reset_ts}.",
                status_code=429,
            )

    async def get_user_profile(self) -> Dict[str, Any]:
        """Fetch profile information for authenticated user."""
        headers = self._get_headers()
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(f"{self.BASE_URL}/user", headers=headers)
                self._check_rate_limit(resp)
            except httpx.RequestError as exc:
                raise GitHubAPIException(f"Network error querying GitHub API: {exc}", status_code=502)

            if resp.status_code == 401:
                raise GitHubAPIException("Invalid or expired GitHub access token", status_code=401)
            if resp.status_code >= 400:
                raise GitHubAPIException(f"GitHub API error: {resp.text}", status_code=resp.status_code)

            user_data = resp.json()

            # If email is not public, retrieve verified emails
            if not user_data.get("email"):
                user_data["email"] = await self._get_primary_email(client, headers)

            return user_data

    async def _get_primary_email(self, client: httpx.AsyncClient, headers: Dict[str, str]) -> str:
        """Retrieve verified primary email from /user/emails."""
        try:
            resp = await client.get(f"{self.BASE_URL}/user/emails", headers=headers)
            if resp.status_code == 200:
                emails = resp.json()
                for item in emails:
                    if item.get("primary") and item.get("verified"):
                        return item["email"]
                if emails:
                    return emails[0].get("email", "")
        except Exception as exc:
            logger.debug("Failed to fetch user emails: %s", exc)
        return ""

    async def list_user_repositories(self, per_page: int = 100) -> List[Dict[str, Any]]:
        """Retrieve all repositories accessible by the authenticated user."""
        headers = self._get_headers()
        params = {"sort": "updated", "per_page": min(per_page, 100), "affiliation": "owner,collaborator,organization_member"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(f"{self.BASE_URL}/user/repos", headers=headers, params=params)
                self._check_rate_limit(resp)
            except httpx.RequestError as exc:
                raise GitHubAPIException(f"Network error querying user repositories: {exc}", status_code=502)

            if resp.status_code == 401:
                raise GitHubAPIException("Invalid or expired GitHub access token", status_code=401)
            if resp.status_code >= 400:
                raise GitHubAPIException(f"GitHub repository query error: {resp.text}", status_code=resp.status_code)

            return resp.json()

    async def get_repository_details(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch metadata for a single repository."""
        headers = self._get_headers()
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(f"{self.BASE_URL}/repos/{owner}/{repo}", headers=headers)
                self._check_rate_limit(resp)
            except httpx.RequestError as exc:
                raise GitHubAPIException(f"Network error querying repository details: {exc}", status_code=502)

            if resp.status_code == 404:
                raise GitHubAPIException(f"Repository {owner}/{repo} not found or access denied", status_code=404)
            if resp.status_code >= 400:
                raise GitHubAPIException(f"GitHub repository error: {resp.text}", status_code=resp.status_code)

            return resp.json()

    async def get_repository_tree(self, owner: str, repo: str, branch: str = "main") -> Dict[str, Any]:
        """Retrieve recursive git tree object for a repository branch."""
        headers = self._get_headers()
        async with httpx.AsyncClient(timeout=25.0) as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/git/trees/{branch}",
                    headers=headers,
                    params={"recursive": "1"},
                )
                self._check_rate_limit(resp)
            except httpx.RequestError as exc:
                raise GitHubAPIException(f"Network error querying repository tree: {exc}", status_code=502)

            if resp.status_code == 404:
                # Fallback check if branch doesn't exist or repo is empty
                raise GitHubAPIException(f"Branch '{branch}' or tree not found for {owner}/{repo}", status_code=404)
            if resp.status_code >= 400:
                raise GitHubAPIException(f"GitHub git tree error: {resp.text}", status_code=resp.status_code)

            return resp.json()

    async def get_file_contents(self, owner: str, repo: str, path: str, ref: Optional[str] = None) -> Optional[str]:
        """Fetch a repository file's text content from the GitHub contents API."""
        headers = self._get_headers()
        params = {"ref": ref} if ref else None
        async with httpx.AsyncClient(timeout=25.0) as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}",
                    headers=headers,
                    params=params,
                )
                self._check_rate_limit(resp)
            except httpx.RequestError as exc:
                raise GitHubAPIException(f"Network error fetching repository file: {exc}", status_code=502)

            if resp.status_code == 404:
                return None
            if resp.status_code >= 400:
                raise GitHubAPIException(f"GitHub file fetch error: {resp.text}", status_code=resp.status_code)

            payload = resp.json()
            if isinstance(payload, dict) and payload.get("type") == "file":
                content = payload.get("content") or ""
                encoding = payload.get("encoding")
                if not content:
                    return ""
                if encoding == "base64":
                    import base64
                    raw = base64.b64decode(content.encode("utf-8"))
                    return raw.decode("utf-8", errors="replace")
                return str(content)
            return None

    async def list_repository_branches(self, owner: str, repo: str, per_page: int = 100) -> List[Dict[str, Any]]:
        """List repository branches for the authenticated user."""
        headers = self._get_headers()
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/branches",
                    headers=headers,
                    params={"per_page": min(per_page, 100)},
                )
                self._check_rate_limit(resp)
            except httpx.RequestError as exc:
                raise GitHubAPIException(f"Network error querying repository branches: {exc}", status_code=502)

            if resp.status_code == 404:
                raise GitHubAPIException(f"Repository {owner}/{repo} not found or access denied", status_code=404)
            if resp.status_code >= 400:
                raise GitHubAPIException(f"GitHub branches query error: {resp.text}", status_code=resp.status_code)

            return resp.json()

    async def list_repository_commits(self, owner: str, repo: str, per_page: int = 10) -> List[Dict[str, Any]]:
        """List recent commits for a repository."""
        headers = self._get_headers()
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/commits",
                    headers=headers,
                    params={"per_page": min(per_page, 100)},
                )
                self._check_rate_limit(resp)
            except httpx.RequestError as exc:
                raise GitHubAPIException(f"Network error querying repository commits: {exc}", status_code=502)

            if resp.status_code == 404:
                raise GitHubAPIException(f"Repository {owner}/{repo} not found or access denied", status_code=404)
            if resp.status_code >= 400:
                raise GitHubAPIException(f"GitHub commits query error: {resp.text}", status_code=resp.status_code)

            return resp.json()

    async def get_repository_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Fetch language breakdown for a repository."""
        headers = self._get_headers()
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(f"{self.BASE_URL}/repos/{owner}/{repo}/languages", headers=headers)
                self._check_rate_limit(resp)
            except httpx.RequestError as exc:
                raise GitHubAPIException(f"Network error querying repository languages: {exc}", status_code=502)

            if resp.status_code == 404:
                raise GitHubAPIException(f"Repository {owner}/{repo} not found or access denied", status_code=404)
            if resp.status_code >= 400:
                raise GitHubAPIException(f"GitHub languages query error: {resp.text}", status_code=resp.status_code)

            return resp.json()
