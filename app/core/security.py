"""API key / registration-token generation and hashing, SSRF-safe URL checks.

Raw API keys are shown to the user exactly once at subscribe time; only
hashes are stored. Keys are ``rn_`` followed by 32 URL-safe random chars.
"""

import hashlib
import hmac
import secrets
from ipaddress import IPv4Address, IPv6Address, ip_address, ip_network
from urllib.parse import urlparse

KEY_PREFIX = "rn_"
KEY_RANDOM_BITS = 192  # 32 base64url chars

_TRUSTED = [
    ip_network("127.0.0.0/8"),
    ip_network("10.0.0.0/8"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"),
    ip_network("169.254.0.0/16"),
    ip_network("100.64.0.0/10"),  # CGNAT
    ip_network("0.0.0.0/8"),
    ip_network("::1/128"),
    ip_network("fe80::/10"),
    ip_network("fc00::/7"),
    ip_network("::ffff:0:0/96"),
]


def generate_api_key() -> str:
    return KEY_PREFIX + secrets.token_urlsafe(KEY_RANDOM_BITS // 8)


def hash_key(raw_key: str, pepper: str = "") -> str:
    salted = f"{pepper}{raw_key}".encode("utf-8")
    return hashlib.sha256(salted).hexdigest()


def verify_api_key(raw_key: str, stored_hash: str, pepper: str = "") -> bool:
    return hmac.compare_digest(hash_key(raw_key, pepper), stored_hash)


def generate_registration_token() -> str:
    return secrets.token_urlsafe(32)


def is_private_ip(host: str) -> bool:
    """True when *host* is an IP literal in a private/restricted range.

    Plain hostnames (not IP literals) return ``False``; DNS-rebinding
    protections are documented — outbound sends never follow redirects.
    """
    try:
        addr: IPv4Address | IPv6Address = ip_address(host)
    except ValueError:
        return False
    return any(addr in net for net in _TRUSTED)


def is_ssrf_safe_url(url: str, allow_http: bool = False) -> bool:
    """Validate an outbound webhook URL: scheme and host IP.

    - scheme must be ``https`` (or ``http`` when *allow_http* is True)
    - a host that is an IP literal must not be private/restricted
    - hostname hosts are permitted; redirection is disabled in senders so a
      user-supplied URL cannot be redirected into an internal address
    """
    parsed = urlparse(url)
    allowed_schemes = ("https",) if not allow_http else ("http", "https")
    if parsed.scheme not in allowed_schemes:
        return False
    host = parsed.hostname
    if not host:
        return False
    if is_private_ip(host):
        return False
    return True
