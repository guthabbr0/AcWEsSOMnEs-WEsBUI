from __future__ import annotations

from urllib.parse import urlparse


def normalize_proxy_url(proxy_url: str | None) -> str | None:
    proxy_url = str(proxy_url or '').strip()
    if not proxy_url:
        return None

    if urlparse(proxy_url).scheme:
        return proxy_url

    return f'http://{proxy_url}'


def requests_proxy_kwargs(proxy_url: str | None) -> dict:
    proxy_url = normalize_proxy_url(proxy_url)
    if not proxy_url:
        return {}

    return {'proxies': {'http': proxy_url, 'https': proxy_url}}


def aiohttp_proxy_kwargs(proxy_url: str | None) -> dict:
    proxy_url = normalize_proxy_url(proxy_url)
    if not proxy_url:
        return {}

    return {'proxy': proxy_url}


def playwright_proxy_config(proxy_url: str | None) -> dict | None:
    proxy_url = normalize_proxy_url(proxy_url)
    if not proxy_url:
        return None

    return {'server': proxy_url}
