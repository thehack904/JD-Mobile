from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import Provider

class MyJDProvider(Provider):
    """Stub provider (v0.4 roadmap).

    This exists so the app structure is ready for the fallback provider without refactoring.
    """

    def __init__(self, *args, **kwargs):
        raise RuntimeError("MyJDownloader provider is not implemented yet (roadmap v0.4).")

    def get_packages(self) -> List[Dict[str, Any]]:
        raise RuntimeError("Not implemented")

    def add_links(self, links: str, package: str, dest: Optional[str], autostart: bool) -> Dict[str, Any]:
        raise RuntimeError("Not implemented")
