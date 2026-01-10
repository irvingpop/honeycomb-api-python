"""Unit tests for TagInput validation."""

import pytest
from pydantic import ValidationError

from honeycomb.models.tool_inputs import BoardToolInput, TagInput


class TestTagInputValidation:
    """Test TagInput field-level validation."""

    def test_valid_tag_simple(self):
        """Test valid simple tag."""
        tag = TagInput(key="team", value="platform")
        assert tag.key == "team"
        assert tag.value == "platform"

    def test_invalid_key_with_underscore(self):
        """Test that underscores in key are rejected (API requires lowercase letters only)."""
        with pytest.raises(ValidationError) as exc_info:
            TagInput(key="service_type", value="api")

        error_str = str(exc_info.value)
        assert "key" in error_str.lower()

    def test_valid_tag_with_slash_in_value(self):
        """Test valid tag value with forward slash."""
        tag = TagInput(key="team", value="platform/api")
        assert tag.value == "platform/api"

    def test_valid_tag_with_dash_in_value(self):
        """Test valid tag value with dash."""
        tag = TagInput(key="region", value="us-east-1")
        assert tag.value == "us-east-1"

    def test_valid_tag_with_numbers_in_value(self):
        """Test valid tag value with numbers."""
        tag = TagInput(key="version", value="v2")
        assert tag.value == "v2"

    def test_valid_tag_complex_value(self):
        """Test complex valid tag value."""
        tag = TagInput(key="team", value="platform/api-gateway-v2")
        assert tag.value == "platform/api-gateway-v2"

    def test_invalid_key_uppercase(self):
        """Test that uppercase letters in key are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TagInput(key="Team", value="platform")

        error_str = str(exc_info.value)
        assert "key" in error_str.lower()
        assert "pattern" in error_str.lower() or "match" in error_str.lower()

    def test_invalid_key_with_dash(self):
        """Test that dashes in key are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TagInput(key="team-name", value="platform")

        error_str = str(exc_info.value)
        assert "key" in error_str.lower()

    def test_invalid_key_with_number(self):
        """Test that numbers in key are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TagInput(key="team123", value="platform")

        error_str = str(exc_info.value)
        assert "key" in error_str.lower()

    def test_invalid_key_empty(self):
        """Test that empty key is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TagInput(key="", value="platform")

        error_str = str(exc_info.value)
        assert "key" in error_str.lower()

    def test_invalid_key_too_long(self):
        """Test that key longer than 32 chars is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TagInput(key="a" * 33, value="platform")

        error_str = str(exc_info.value)
        assert "key" in error_str.lower()
        assert "32" in error_str

    def test_invalid_value_uppercase(self):
        """Test that uppercase letters in value are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TagInput(key="team", value="Platform")

        error_str = str(exc_info.value)
        assert "value" in error_str.lower()

    def test_invalid_value_with_underscore(self):
        """Test that underscores in value are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TagInput(key="team", value="platform_api")

        error_str = str(exc_info.value)
        assert "value" in error_str.lower()

    def test_invalid_value_starting_with_number(self):
        """Test that values starting with number are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TagInput(key="team", value="1platform")

        error_str = str(exc_info.value)
        assert "value" in error_str.lower()

    def test_invalid_value_starting_with_dash(self):
        """Test that values starting with dash are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TagInput(key="team", value="-platform")

        error_str = str(exc_info.value)
        assert "value" in error_str.lower()

    def test_invalid_value_empty(self):
        """Test that empty value is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TagInput(key="team", value="")

        error_str = str(exc_info.value)
        assert "value" in error_str.lower()

    def test_invalid_value_too_long(self):
        """Test that value longer than 128 chars is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TagInput(key="team", value="a" * 129)

        error_str = str(exc_info.value)
        assert "value" in error_str.lower()
        assert "128" in error_str

    def test_max_key_length_valid(self):
        """Test that key with exactly 32 chars is valid."""
        key = "a" * 32
        tag = TagInput(key=key, value="platform")
        assert tag.key == key

    def test_max_value_length_valid(self):
        """Test that value with exactly 128 chars is valid."""
        value = "a" + "b" * 127  # Starts with 'a', total 128
        tag = TagInput(key="team", value=value)
        assert tag.value == value


class TestBoardTagsLimit:
    """Test BoardToolInput tag count validation."""

    def test_board_with_10_tags_valid(self):
        """Test that board with exactly 10 tags is valid."""
        # Use letters only in keys (no numbers or underscores allowed in tag keys)
        key_names = [
            "team",
            "environment",
            "region",
            "owner",
            "servicetype",
            "costcenter",
            "application",
            "tier",
            "criticality",
            "version",
        ]
        tags = [TagInput(key=key_names[i], value=f"value{i}") for i in range(10)]
        board = BoardToolInput(name="Test Board", tags=tags)
        assert len(board.tags) == 10

    def test_board_with_11_tags_rejected(self):
        """Test that board with 11 tags is rejected."""
        # Use letters only in keys (no numbers or underscores allowed in tag keys)
        key_names = [
            "team",
            "environment",
            "region",
            "owner",
            "servicetype",
            "costcenter",
            "application",
            "tier",
            "criticality",
            "version",
            "extra",
        ]
        tags = [TagInput(key=key_names[i], value=f"value{i}") for i in range(11)]

        with pytest.raises(ValidationError) as exc_info:
            BoardToolInput(name="Test Board", tags=tags)

        error_str = str(exc_info.value)
        assert "11" in error_str
        assert "10" in error_str
        assert "tag" in error_str.lower()

    def test_board_with_20_tags_rejected(self):
        """Test that board with 20 tags shows clear error."""
        # Use letters only to create 20 unique valid keys (lowercase letters only)
        tags = [TagInput(key=f"key{chr(97 + i)}", value=f"value{i}") for i in range(20)]

        with pytest.raises(ValidationError) as exc_info:
            BoardToolInput(name="Test Board", tags=tags)

        error_str = str(exc_info.value)
        assert "20" in error_str
        assert "maximum is 10" in error_str.lower()

    def test_board_with_no_tags_valid(self):
        """Test that board with no tags is valid."""
        board = BoardToolInput(name="Test Board")
        assert board.tags is None

    def test_board_with_empty_tags_list_valid(self):
        """Test that board with empty tags list is valid."""
        board = BoardToolInput(name="Test Board", tags=[])
        assert board.tags == []


class TestTagValidationErrorMessages:
    """Test that error messages are clear and actionable."""

    def test_invalid_key_message_clarity(self):
        """Test that invalid key error message is clear."""
        with pytest.raises(ValidationError) as exc_info:
            TagInput(key="Team-Name", value="platform")

        error_str = str(exc_info.value)
        # Should mention the pattern or constraint
        assert "lowercase" in error_str.lower() or "pattern" in error_str.lower()

    def test_invalid_value_message_clarity(self):
        """Test that invalid value error message is clear."""
        with pytest.raises(ValidationError) as exc_info:
            TagInput(key="team", value="Platform_API")

        error_str = str(exc_info.value)
        # Should mention the pattern or constraint
        assert "lowercase" in error_str.lower() or "pattern" in error_str.lower()

    def test_tag_limit_message_clarity(self):
        """Test that tag limit error message is clear."""
        # Use letters only to create 15 unique valid keys (lowercase letters only)
        tags = [TagInput(key=f"tag{chr(97 + i)}", value=f"value{i}") for i in range(15)]

        with pytest.raises(ValidationError) as exc_info:
            BoardToolInput(name="Test Board", tags=tags)

        error_str = str(exc_info.value)
        assert "Too many tags" in error_str
        assert "15" in error_str
        assert "maximum is 10" in error_str


class TestTagInputWithRealWorldExamples:
    """Test TagInput with real-world usage examples."""

    def test_common_valid_tags(self):
        """Test common valid tag patterns."""
        valid_examples = [
            {"key": "team", "value": "platform"},
            {"key": "environment", "value": "production"},
            {"key": "servicetype", "value": "api/backend"},
            {"key": "region", "value": "us-east-1"},
            {"key": "costcenter", "value": "engineering"},
            {"key": "owner", "value": "team-alpha"},
            {"key": "version", "value": "v2"},
        ]

        for example in valid_examples:
            tag = TagInput(**example)
            assert tag.key == example["key"]
            assert tag.value == example["value"]

    def test_common_invalid_tags(self):
        """Test common invalid tag patterns that users might try."""
        invalid_examples = [
            {"key": "Team", "value": "platform"},  # Uppercase key
            {"key": "team-name", "value": "platform"},  # Dash in key
            {"key": "team", "value": "Platform"},  # Uppercase value
            {"key": "team", "value": "platform_api"},  # Underscore in value
            {"key": "team", "value": "1platform"},  # Value starts with number
        ]

        for example in invalid_examples:
            with pytest.raises(ValidationError):
                TagInput(**example)
