"""Technique Registry - Centralized access to technique definitions.

This module provides a singleton registry for accessing technique definitions
with validation, caching, and efficient lookup by ID or category.
"""

import threading
from pathlib import Path
from typing import Dict, List, Optional, Set

from app.core.logging import logger
from app.techniques.loader import DEFAULT_TECHNIQUES_DIR, load_techniques
from app.techniques.schema import TechniqueDefinition


class TechniqueNotFoundError(Exception):
    """Raised when a technique ID is not found in the registry."""

    def __init__(self, technique_id: str, available_ids: Optional[List[str]] = None):
        self.technique_id = technique_id
        self.available_ids = available_ids
        msg = f"Technique not found: '{technique_id}'"
        if available_ids:
            similar = [
                t for t in available_ids if technique_id in t or t in technique_id
            ]
            if similar:
                msg += f". Did you mean: {', '.join(similar[:5])}?"
        super().__init__(msg)


class TechniqueValidationError(Exception):
    """Raised when technique definitions fail validation."""

    def __init__(self, errors: List[str]):
        self.errors = errors
        msg = f"Technique validation failed with {len(errors)} error(s):\n"
        msg += "\n".join(f"  - {e}" for e in errors[:10])
        if len(errors) > 10:
            msg += f"\n  ... and {len(errors) - 10} more errors"
        super().__init__(msg)


class TechniqueRegistry:
    """Singleton registry for technique definitions.

    Provides efficient access to techniques with:
    - Lazy loading on first access
    - Caching for performance
    - Lookup by ID or category
    - Validation at load time

    Usage:
        registry = TechniqueRegistry()
        technique = registry.get("five-whys")
        aroma_techniques = registry.get_by_category("aroma")
    """

    _instance: Optional["TechniqueRegistry"] = None
    _initialized: bool = False
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "TechniqueRegistry":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if TechniqueRegistry._initialized:
            return

        with TechniqueRegistry._lock:
            if TechniqueRegistry._initialized:
                return

            self._definitions_dir = DEFAULT_TECHNIQUES_DIR
            self._techniques: List[TechniqueDefinition] = []
            self._by_id: Dict[str, TechniqueDefinition] = {}
            self._by_category: Dict[str, List[TechniqueDefinition]] = {}
            self._categories: Set[str] = set()
            self._loaded = False
            self._load_errors: List[str] = []

            TechniqueRegistry._initialized = True

    def _ensure_loaded(self) -> None:
        """Ensure techniques are loaded before access."""
        if self._loaded:
            return

        logger.info(
            "Loading technique definitions",
            extra={"dir": str(self._definitions_dir)},
        )

        techniques, errors = load_techniques(self._definitions_dir)

        if errors:
            self._load_errors = errors
            logger.warning(
                "Technique loading completed with errors",
                extra={"loaded": len(techniques), "errors": len(errors)},
            )

        # Check for duplicate IDs and filter them out
        seen_ids: Dict[str, str] = {}
        unique_techniques: List[TechniqueDefinition] = []
        for tech in techniques:
            if tech.id in seen_ids:
                errors.append(
                    f"Duplicate technique ID '{tech.id}' "
                    f"(first in {seen_ids[tech.id]}, duplicate in {tech.category})"
                )
            else:
                seen_ids[tech.id] = tech.category
                unique_techniques.append(tech)

        if errors and not unique_techniques:
            raise TechniqueValidationError(errors)

        # Build indexes (using deduplicated list)
        self._techniques = unique_techniques
        self._by_id = {t.id: t for t in unique_techniques}
        self._categories = {t.category for t in unique_techniques}

        for tech in unique_techniques:
            if tech.category not in self._by_category:
                self._by_category[tech.category] = []
            self._by_category[tech.category].append(tech)

        self._loaded = True

        logger.info(
            "Technique registry initialized",
            extra={
                "total": len(techniques),
                "categories": len(self._categories),
                "errors": len(self._load_errors),
            },
        )

    def list_techniques(self) -> List[TechniqueDefinition]:
        """Return all loaded techniques in deterministic order.

        Returns:
            List of all technique definitions, sorted by ID.
        """
        self._ensure_loaded()
        return sorted(self._techniques, key=lambda t: t.id)

    def get_technique(self, technique_id: str) -> Optional[TechniqueDefinition]:
        """Get a technique by its ID.

        Args:
            technique_id: The unique technique identifier.

        Returns:
            The technique definition, or None if not found.
        """
        self._ensure_loaded()
        return self._by_id.get(technique_id)

    def get(self, technique_id: str) -> TechniqueDefinition:
        """Get a technique by ID, raising an error if not found.

        Args:
            technique_id: The unique technique identifier.

        Returns:
            The technique definition.

        Raises:
            TechniqueNotFoundError: If the technique is not found.
        """
        self._ensure_loaded()
        technique = self._by_id.get(technique_id)
        if technique is None:
            raise TechniqueNotFoundError(technique_id, list(self._by_id.keys()))
        return technique

    def exists(self, technique_id: str) -> bool:
        """Check if a technique exists in the registry.

        Args:
            technique_id: The unique technique identifier.

        Returns:
            True if the technique exists, False otherwise.
        """
        self._ensure_loaded()
        return technique_id in self._by_id

    def get_techniques_by_category(self, category: str) -> List[TechniqueDefinition]:
        """Get all techniques in a specific category.

        Args:
            category: The category name (e.g., "aroma", "palate").

        Returns:
            List of techniques in that category, sorted by ID.
            Returns empty list if category doesn't exist.
        """
        self._ensure_loaded()
        techniques = self._by_category.get(category, [])
        return sorted(techniques, key=lambda t: t.id)

    def list_categories(self) -> List[str]:
        """Return all available categories.

        Returns:
            Sorted list of category names.
        """
        self._ensure_loaded()
        return sorted(self._categories)

    def get_load_errors(self) -> List[str]:
        """Return any errors encountered during loading.

        Returns:
            List of error messages from the loading process.
        """
        self._ensure_loaded()
        return self._load_errors.copy()

    def count(self) -> int:
        """Return the total number of techniques.

        Returns:
            Number of loaded techniques.
        """
        self._ensure_loaded()
        return len(self._techniques)

    def count_by_category(self) -> Dict[str, int]:
        """Return technique counts per category.

        Returns:
            Dictionary mapping category names to technique counts.
        """
        self._ensure_loaded()
        return {cat: len(techs) for cat, techs in self._by_category.items()}

    def validate(self) -> bool:
        """Validate the registry state.

        Returns:
            True if all techniques are valid and loaded.

        Raises:
            TechniqueValidationError: If there are critical validation errors.
        """
        self._ensure_loaded()
        if self._load_errors:
            # Non-critical errors (some files failed but we have techniques)
            logger.warning(
                "Registry has load errors",
                extra={"errors": len(self._load_errors)},
            )
        return len(self._techniques) > 0

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (mainly for testing)."""
        cls._instance = None
        cls._initialized = False


# Module-level convenience functions
def get_registry() -> TechniqueRegistry:
    """Get the singleton technique registry instance.

    Returns:
        The global TechniqueRegistry instance.
    """
    return TechniqueRegistry()


def list_techniques() -> List[TechniqueDefinition]:
    """List all techniques from the global registry.

    Returns:
        List of all technique definitions.
    """
    return get_registry().list_techniques()


def get_technique(technique_id: str) -> Optional[TechniqueDefinition]:
    """Get a technique by ID from the global registry.

    Args:
        technique_id: The unique technique identifier.

    Returns:
        The technique definition, or None if not found.
    """
    return get_registry().get_technique(technique_id)


def get_techniques_by_category(category: str) -> List[TechniqueDefinition]:
    """Get techniques by category from the global registry.

    Args:
        category: The category name.

    Returns:
        List of techniques in that category.
    """
    return get_registry().get_techniques_by_category(category)


def list_available_categories() -> List[str]:
    """List all available technique categories.

    Returns:
        Sorted list of category names.
    """
    return get_registry().list_categories()
