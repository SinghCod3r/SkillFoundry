"""URL validation for SSRF prevention."""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


def validate_url(url: str) -> str:
    """Validate and return cleaned URL. Raise ValueError on unsafe URLs."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Unsafe URL scheme: {parsed.scheme}")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Invalid URL: missing hostname")

    try:
        ip = ipaddress.ip_address(socket.gethostbyname(hostname))

        if ip.is_loopback:
            raise ValueError(f"Loopback addresses are not allowed: {hostname}")
        if ip.is_private:
            raise ValueError(f"Private network addresses are not allowed: {hostname}")
        if ip.is_link_local:
            raise ValueError(f"Link-local addresses are not allowed: {hostname}")
        if str(ip) == "169.254.169.254":
            raise ValueError(f"Metadata endpoints are not allowed: {hostname}")
        if ip.is_unspecified:
            raise ValueError(f"Unspecified addresses are not allowed: {hostname}")

    except (socket.gaierror, ValueError):
        if hostname in ("localhost", "metadata.google.internal"):
            raise ValueError(f"Blocked hostname: {hostname}")

    # Note: httpx client should set max_redirects to prevent redirect loops and SSRF via redirects.
    return url

def is_github_url(url: str) -> bool:
    """Check if URL is a valid GitHub repo URL."""
    try:
        parsed = urlparse(url)
        return parsed.hostname == "github.com"
    except Exception:
        return False

def parse_github_url(url: str) -> tuple[str, str, str | None]:
    """Extract (owner, repo, branch) from GitHub URL."""
    if not is_github_url(url):
        raise ValueError(f"Not a valid GitHub URL: {url}")

    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        raise ValueError("Invalid GitHub URL path")

    parts = path.split("/")
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL path: missing repo")

    owner = parts[0]
    repo = parts[1]

    if repo.endswith(".git"):
        repo = repo[:-4]

    branch = None
    if len(parts) >= 4 and parts[2] == "tree":
        branch = parts[3]

    return owner, repo, branch
