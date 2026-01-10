"""Mixin for adding tags to Honeycomb resources."""

from __future__ import annotations

from typing_extensions import Self


class TagsMixin:
    """Mixin providing tag management methods.

    Tags are key-value pairs used to identify and organize resources.
    Supported by: Triggers, Boards, SLOs.
    """

    def __init__(self) -> None:
        """Initialize tag storage."""
        self._tags: list[dict[str, str]] = []

    def tag(self, key: str, value: str) -> Self:
        """Add a tag to the resource.

        Args:
            key: Tag key (lowercase letters only, max 32 chars).
            value: Tag value (must start with lowercase letter,
                   alphanumeric + / and -, max 128 chars).

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If key or value format is invalid.
        """
        # Validate key
        if not key or len(key) > 32:
            raise ValueError("Tag key must be 1-32 characters")
        if not key.isalpha() or not key.islower():
            raise ValueError("Tag key must contain only lowercase letters")

        # Validate value
        if not value or len(value) > 128:
            raise ValueError("Tag value must be 1-128 characters")
        if not value[0].islower():
            raise ValueError("Tag value must start with a lowercase letter")

        # Allow lowercase letters, numbers, /, and -
        allowed_chars = set("abcdefghijklmnopqrstuvwxyz0123456789/-")
        if not all(c in allowed_chars for c in value):
            raise ValueError("Tag value can only contain lowercase letters, numbers, / and -")

        # Check max tags limit (10)
        if len(self._tags) >= 10:
            raise ValueError("Maximum of 10 tags allowed")

        self._tags.append({"key": key, "value": value})
        return self

    def tags(self, tags: dict[str, str]) -> Self:
        """Add multiple tags from a dictionary.

        Args:
            tags: Dictionary of key-value pairs.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If any key or value format is invalid.
        """
        for key, value in tags.items():
            self.tag(key, value)
        return self

    def _get_all_tags(self) -> list[dict[str, str]] | None:
        """Get tags for API (None if empty).

        Returns:
            List of tag dictionaries or None if no tags.
        """
        return self._tags if self._tags else None
