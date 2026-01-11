"""Tool description validation utilities.

Description requirements:
1. What it does (1 sentence)
2. When to use it (1 sentence)
3. Key parameters explained (1-2 sentences)
4. Important caveats/limitations (if any)

Note: Tool descriptions are now defined in individual resource modules
(e.g., src/honeycomb/tools/resources/triggers.py) rather than centrally.
This module only provides validation utilities.
"""


def validate_description(description: str, min_length: int = 50) -> None:
    """Validate a description meets quality requirements.

    Args:
        description: The description to validate
        min_length: Minimum character count (default 50)

    Raises:
        ValueError: If description is invalid
    """
    if not description:
        raise ValueError("Description cannot be empty")

    if len(description) < min_length:
        raise ValueError(
            f"Description must be at least {min_length} characters (got {len(description)})"
        )

    # Check for placeholder text
    placeholders = ["TODO", "TBD", "FIXME", "XXX"]
    for placeholder in placeholders:
        if placeholder in description.upper():
            raise ValueError(f"Description contains placeholder text: {placeholder}")
