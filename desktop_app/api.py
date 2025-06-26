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
