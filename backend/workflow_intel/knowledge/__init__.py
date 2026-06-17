"""Curated knowledge catalogs that ground the deterministic analysis."""

from workflow_intel.knowledge.platforms import PLATFORM_PROFILES, recommend_platform
from workflow_intel.knowledge.systems import SYSTEM_CATALOG, match_systems

__all__ = ["PLATFORM_PROFILES", "recommend_platform", "SYSTEM_CATALOG", "match_systems"]
