"""Base class for resource cleaners."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from azure.core.credentials import TokenCredential
from azurewipe.core.config import Config


class ResourceCleaner(ABC):
    """Abstract base class for Azure resource cleaners."""

    resource_type: str = ""
    dependencies: List[str] = []  # Must be deleted before this

    def __init__(self, credential: TokenCredential, config: Config):
        self.credential = credential
        self.config = config
        self.report = {"deleted": [], "failed": [], "skipped": []}

    @abstractmethod
    def discover(self, subscriptions: List[str]) -> List[Dict[str, Any]]:
        """Discover resources to clean."""
        pass

    @abstractmethod
    def delete(self, resource: Dict[str, Any]) -> bool:
        """Delete a single resource. Returns True on success."""
        pass

    def should_delete(self, resource: Dict[str, Any]) -> bool:
        """Check if resource should be deleted based on config."""
        name = resource.get("name", "")
        tags = resource.get("tags") or {}
        rg = resource.get("resourceGroup", "")

        if self.config.matches_exclude_pattern(name):
            return False
        if not self.config.matches_tag_filters(tags):
            return False
        if not self.config.should_include_rg(rg):
            return False
        return True

    def clean(self, subscriptions: List[str]) -> Dict[str, List]:
        """Discover and delete resources."""
        resources = self.discover(subscriptions)
        for res in resources:
            if not self.should_delete(res):
                self.report["skipped"].append(res["id"])
                continue
            if self.config.dry_run:
                self.report["deleted"].append(res["id"])  # Would delete
            else:
                if self.delete(res):
                    self.report["deleted"].append(res["id"])
                else:
                    self.report["failed"].append(res["id"])
        return self.report
