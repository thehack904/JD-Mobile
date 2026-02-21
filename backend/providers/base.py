from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class Provider(ABC):
    @abstractmethod
    def get_packages(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def add_links(self, links: str, package: str, dest: Optional[str], autostart: bool) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def remove_packages(self, package_ids: List[int], link_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        raise NotImplementedError
