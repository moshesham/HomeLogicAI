from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


def domain_matches(url: str, domain: str) -> bool:
    hostname = (urlparse(url).hostname or "").lower().strip(".")
    domain = domain.lower().strip(".")
    return hostname == domain or hostname.endswith(f".{domain}")


def validate_outbound_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only HTTP/HTTPS URLs are allowed")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL must include a hostname")

    if hostname in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Localhost targets are not allowed")

    try:
        infos = socket.getaddrinfo(hostname, parsed.port or 443)
    except socket.gaierror as exc:
        raise ValueError("Could not resolve hostname") from exc

    for info in infos:
        ip = info[4][0]
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            continue
        if (
            addr.is_private
            or addr.is_loopback
            or addr.is_link_local
            or addr.is_reserved
        ):
            raise ValueError("Private or non-routable target addresses are not allowed")

    return url
