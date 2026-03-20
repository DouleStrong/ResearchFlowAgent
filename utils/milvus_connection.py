import os
from contextlib import contextmanager
from ipaddress import ip_address
from urllib.parse import urlparse

from pymilvus import MilvusClient


PROXY_ENV_KEYS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "NO_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
    "no_proxy",
)


def _normalize_uri(uri: str) -> str:
    return uri if "://" in uri else f"http://{uri}"


def _is_local_milvus_host(host: str) -> bool:
    if host == "localhost":
        return True

    try:
        parsed_host = ip_address(host)
    except ValueError:
        return False

    return parsed_host.is_loopback or parsed_host.is_private


def _build_no_proxy_value(original_value: str | None, host: str) -> str:
    entries = [entry.strip() for entry in (original_value or "").split(",") if entry.strip()]

    for candidate in (host, "127.0.0.1", "localhost"):
        if candidate and candidate not in entries:
            entries.append(candidate)

    return ",".join(entries)


@contextmanager
def _temporary_local_proxy_bypass(uri: str):
    parsed_uri = urlparse(_normalize_uri(uri))
    host = parsed_uri.hostname or ""

    if parsed_uri.scheme == "https" or not _is_local_milvus_host(host):
        yield
        return

    original_env = {key: os.environ.get(key) for key in PROXY_ENV_KEYS}

    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        os.environ[key] = ""

    os.environ["NO_PROXY"] = _build_no_proxy_value(original_env.get("NO_PROXY"), host)
    os.environ["no_proxy"] = _build_no_proxy_value(original_env.get("no_proxy"), host)

    try:
        yield
    finally:
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def create_milvus_client(uri: str, **kwargs) -> MilvusClient:
    with _temporary_local_proxy_bypass(uri):
        return MilvusClient(uri=uri, **kwargs)
