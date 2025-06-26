"""Wrapper functions for the MyLoRA REST API."""

from urllib.parse import urljoin
import io
import requests
from safetensors import safe_open

import config


def _request(path: str, params=None):
    url = urljoin(config.API_BASE_URL + '/', path.lstrip('/'))
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


def search(query: str, limit: int | None = None, offset: int = 0):
    params = {"query": query, "limit": limit, "offset": offset}
    return _request('search', params)


def grid_data(q: str = '*', category: int | None = None, offset: int = 0, limit: int = 50):
    params = {"q": q, "offset": offset, "limit": limit}
    if category is not None:
        params["category"] = category
    return _request('grid_data', params)


def categories():
    return _request('categories')

def download_file(filename: str, dest_path: str):
    """Download ``filename`` from the server to ``dest_path``."""
    url = urljoin(config.API_BASE_URL + '/', f'uploads/{filename}')
    with requests.get(url, stream=True) as resp:
        resp.raise_for_status()
        with open(dest_path, 'wb') as fh:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)
    return dest_path


def preview_url(path: str) -> str:
    """Return absolute URL for a preview image or safetensors file."""
    return urljoin(config.API_BASE_URL + '/', path.lstrip('/'))


def _head(path: str) -> bool:
    """Return ``True`` if ``/uploads/path`` exists on the server."""
    url = urljoin(config.API_BASE_URL + '/', f'uploads/{path}')
    try:
        resp = requests.head(url)
    except requests.RequestException:
        # some servers (e.g. behind certain proxies) may not allow HEAD
        resp = requests.get(url, stream=True)
    finally:
        # ensure we close the connection to avoid leaking sockets
        try:
            resp.close()
        except Exception:
            pass
    return resp.status_code == 200


def list_previews(stem: str, max_files: int = 10) -> list[str]:
    """Return all preview image URLs for ``stem``."""
    exts = ["png", "jpg", "jpeg", "gif"]
    files: list[str] = []
    for ext in exts:
        name = f"{stem}.{ext}"
        if _head(name):
            files.append(f"uploads/{name}")
    for i in range(1, max_files + 1):
        for ext in exts:
            name = f"{stem}_{i}.{ext}"
            if _head(name):
                files.append(f"uploads/{name}")
    return [preview_url(f) for f in files]


def fetch_metadata(filename: str) -> dict:
    """Download ``filename`` and return its embedded metadata."""
    url = urljoin(config.API_BASE_URL + '/', f'uploads/{filename}')
    resp = requests.get(url)
    resp.raise_for_status()
    try:
        with safe_open(io.BytesIO(resp.content), framework="pt") as f:
            return f.metadata() or {}
    except Exception as exc:
        return {"error": str(exc)}
