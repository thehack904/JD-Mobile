from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import requests

from .base import Provider

class LocalProvider(Provider):
    def __init__(self, base_url: str, timeout_ms: int = 800):
        self.base_url = (base_url or "").strip().rstrip("/")
        self.timeout = max(0.1, timeout_ms / 1000.0)

    def _get(self, path: str, query: Optional[dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        params = {}
        if query is not None:
            params["query"] = json.dumps(query)
        r = requests.get(url, params=params, timeout=self.timeout)
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            # Some JD endpoints may respond with plain text; wrap it.
            return {"data": r.text}

    def _action(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Call a JD2 action endpoint that takes named parameters as individual
        JSON-encoded query string values (e.g. removePackages(long[] linkIds, long[] packageIds)).
        Each kwarg value is JSON-encoded regardless of type."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        params = {k: json.dumps(v) for k, v in kwargs.items()}
        r = requests.get(url, params=params, timeout=self.timeout)
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return {"data": r.text}

    def get_packages(self) -> List[Dict[str, Any]]:
        q = {
            "name": True,
            "uuid": True,
            "bytesTotal": True,
            "bytesLoaded": True,
            "enabled": True,
            "running": True,
            "finished": True,
            "eta": True,
            "speed": True,
        }
        data = self._get("downloadsV2/queryPackages", q)
        return data.get("data", []) if isinstance(data, dict) else []

    def add_links(self, links: str, package: str, dest: Optional[str], autostart: bool) -> Dict[str, Any]:
        q: Dict[str, Any] = {
            "assignJobID": True,
            "autostart": autostart,
            "links": links,
            "packageName": package,
        }
        if dest:
            q["destinationFolder"] = dest
        return self._get("linkgrabberv2/addLinks", q)

    def remove_packages(self, package_ids: List[int], link_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        return self._action("downloadsV2/removeLinks", linkIds=link_ids or [], packageIds=package_ids)
