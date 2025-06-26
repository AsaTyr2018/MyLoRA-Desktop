"""Wrapper functions for the MyLoRA REST API."""

from urllib.parse import urljoin
import requests

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
