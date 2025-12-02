"""YAML configuration loader."""
import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Any
import yaml


@dataclass
class TagFilters:
    include: Dict[str, List[str]] = field(default_factory=dict)
    exclude: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class Config:
    subscriptions: List[str] = field(default_factory=lambda: ["all"])
    resource_groups: List[str] = field(default_factory=lambda: ["all"])
    resource_types: List[str] = field(default_factory=lambda: ["all"])
    tag_filters: TagFilters = field(default_factory=TagFilters)
    exclude_patterns: List[str] = field(default_factory=list)
    dry_run: bool = True
    json_logs: bool = False
    verbosity: int = 0

    def should_include_subscription(self, sub_id: str) -> bool:
        if "all" in self.subscriptions:
            return True
        return sub_id in self.subscriptions

    def should_include_rg(self, rg_name: str) -> bool:
        if "all" in self.resource_groups:
            return True
        return any(fnmatch.fnmatch(rg_name, p) for p in self.resource_groups)

    def should_include_resource_type(self, res_type: str) -> bool:
        if "all" in self.resource_types:
            return True
        return res_type in self.resource_types

    def matches_tag_filters(self, tags: Dict[str, str]) -> bool:
        tags = tags or {}
        for key, values in self.tag_filters.exclude.items():
            if key in tags and tags[key] in values:
                return False
        if self.tag_filters.include:
            for key, values in self.tag_filters.include.items():
                if key in tags and tags[key] in values:
                    return True
            return False
        return True

    def matches_exclude_pattern(self, name: str) -> bool:
        return any(fnmatch.fnmatch(name, p) for p in self.exclude_patterns)


def load_config(path: Optional[str] = None) -> Config:
    if path is None:
        return Config()
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(config_path) as f:
        data = yaml.safe_load(f) or {}
    return _parse_config(data)


def _parse_config(data: Dict[str, Any]) -> Config:
    tag_data = data.get("tag_filters", {})
    tag_filters = TagFilters(
        include=tag_data.get("include", {}),
        exclude=tag_data.get("exclude", {}),
    )
    return Config(
        subscriptions=data.get("subscriptions", ["all"]),
        resource_groups=data.get("resource_groups", ["all"]),
        resource_types=data.get("resource_types", ["all"]),
        tag_filters=tag_filters,
        exclude_patterns=data.get("exclude_patterns", []),
        dry_run=data.get("dry_run", True),
        json_logs=data.get("json_logs", False),
        verbosity=data.get("verbosity", 0),
    )
