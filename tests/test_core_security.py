"""Unit tests for app.core.security and app.core.config."""

from app.core.config import Settings
from app.core.security import (
    generate_api_key,
    generate_registration_token,
    hash_key,
    is_ssrf_safe_url,
    verify_api_key,
)


def test_api_key_format_is_prefix_and_urlsafe() -> None:
    key = generate_api_key()
    assert key.startswith("rn_")
    assert len(key) == 35  # rn_ + 32 urlsafe chars
    assert key[3:] == key[3:].replace("+", "").replace("/", "")


def test_hash_and_verify_roundtrip() -> None:
    key = generate_api_key()
    stored = hash_key(key, pepper="pepper")
    assert stored != key
    assert stored == hash_key(key, pepper="pepper")
    assert stored != hash_key(key, pepper="other")
    assert verify_api_key(key, stored, pepper="pepper")
    assert not verify_api_key("rn_wrong", stored, pepper="pepper")


def test_registration_token_is_long_random() -> None:
    a, b = generate_registration_token(), generate_registration_token()
    assert a != b
    assert len(a) >= 32


def test_ssrf_blocks_private_ip_literal_hosts() -> None:
    assert is_ssrf_safe_url("https://127.0.0.1/hook") is False
    assert is_ssrf_safe_url("https://10.1.2.3/hook") is False
    assert is_ssrf_safe_url("https://192.168.0.5/hook") is False
    assert is_ssrf_safe_url("https://172.16.5.5/hook") is False
    assert is_ssrf_safe_url("https://169.254.1.1/hook") is False
    assert is_ssrf_safe_url("https://100.64.0.9/hook") is False
    assert is_ssrf_safe_url("https://[::1]/hook") is False
    assert is_ssrf_safe_url("https://0.0.0.0/hook") is False


def test_ssrf_blocks_localhost_hostname_and_fails_closed_on_unresolvable() -> None:
    # Hostname that resolves to loopback must be blocked now that hostnames
    # are resolved (e.g. 127.0.0.1.nip.io style bypasses are closed by DNS check).
    assert is_ssrf_safe_url("https://localhost/hook") is False
    assert is_ssrf_safe_url("http://localhost:9000/hook", allow_http=True) is False
    assert is_ssrf_safe_url("https://this-host-does-not-resolve.invalid/hook") is False


def test_ssrf_allows_public_https_and_blocks_other_schemes() -> None:
    assert is_ssrf_safe_url("https://hooks.slack.com/services/a/b/c") is True
    assert is_ssrf_safe_url("https://8.8.8.8/hook") is True
    assert is_ssrf_safe_url("file:///etc/passwd") is False
    assert is_ssrf_safe_url("ftp://example.com/x") is False
    assert is_ssrf_safe_url("http://8.8.8.8/hook") is False
    assert is_ssrf_safe_url("http://8.8.8.8/hook", allow_http=True) is True
    assert is_ssrf_safe_url("https://") is False


def test_settings_reads_defaults_without_env() -> None:
    s = Settings(_env_file=None)
    assert s.rate_limit_requests == 60
    assert s.rate_limit_window_seconds == 60
    assert s.max_payload_bytes == 8192
