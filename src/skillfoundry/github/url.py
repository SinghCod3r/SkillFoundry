from __future__ import annotations

from skillfoundry.security.urls import validate_url


def is_github_url(url: str) -> bool:
    """Checks if a URL is a valid GitHub URL."""
    try:
        validate_url(url)
        return "github.com" in url
    except Exception:
        return False


def normalize_github_url(url: str) -> str:
    """Normalizes a GitHub URL."""
    url = url.strip().rstrip("/")
    if not url.endswith(".git"):
        url = f"{url}.git"
    return url
