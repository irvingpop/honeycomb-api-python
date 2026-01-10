"""Tests for TagsMixin."""

import pytest

from honeycomb import TagsMixin


class TestTagsMixin:
    """Tests for the TagsMixin tag management methods."""

    def test_initialization(self):
        """Test TagsMixin initialization."""
        mixin = TagsMixin()
        assert mixin._tags == []

    def test_single_tag(self):
        """Test adding a single tag."""
        mixin = TagsMixin()
        result = mixin.tag("team", "backend")
        assert result is mixin  # Method chaining
        assert len(mixin._tags) == 1
        assert mixin._tags[0] == {"key": "team", "value": "backend"}

    def test_multiple_tags_via_tag_method(self):
        """Test adding multiple tags via tag() method."""
        mixin = TagsMixin()
        mixin.tag("team", "backend")
        mixin.tag("env", "production")
        mixin.tag("service", "api")
        assert len(mixin._tags) == 3

    def test_tags_via_dict(self):
        """Test adding tags via tags() method with dictionary."""
        mixin = TagsMixin()
        mixin.tags({"team": "backend", "env": "production"})
        assert len(mixin._tags) == 2

    def test_tags_with_underscore_in_key_rejected(self):
        """Test that underscores in tag key are rejected (API requires lowercase letters only)."""
        mixin = TagsMixin()
        with pytest.raises(ValueError, match="must contain only lowercase letters"):
            mixin.tag("service_type", "api")

    def test_tags_with_slash_in_value(self):
        """Test tag value with forward slash."""
        mixin = TagsMixin()
        mixin.tag("owner", "team/platform")
        assert mixin._tags[0]["value"] == "team/platform"

    def test_tags_with_dash_in_value(self):
        """Test tag value with dash."""
        mixin = TagsMixin()
        mixin.tag("env", "staging-east")
        assert mixin._tags[0]["value"] == "staging-east"

    def test_get_all_tags_empty(self):
        """Test getting tags when none added."""
        mixin = TagsMixin()
        tags = mixin._get_all_tags()
        assert tags is None

    def test_get_all_tags_returns_list(self):
        """Test that _get_all_tags returns list when tags exist."""
        mixin = TagsMixin()
        mixin.tag("team", "backend")
        tags = mixin._get_all_tags()
        assert tags == [{"key": "team", "value": "backend"}]

    def test_method_chaining(self):
        """Test that tag methods support chaining."""
        mixin = TagsMixin()
        result = mixin.tag("team", "backend").tag("env", "prod").tags({"service": "api"})
        assert result is mixin
        assert len(mixin._tags) == 3

    def test_tag_order_preserved(self):
        """Test that tag order is preserved."""
        mixin = TagsMixin()
        mixin.tag("first", "a")
        mixin.tag("second", "b")
        mixin.tag("third", "c")

        tags = mixin._get_all_tags()
        assert tags[0]["key"] == "first"
        assert tags[1]["key"] == "second"
        assert tags[2]["key"] == "third"


class TestTagsMixinValidation:
    """Tests for tag validation."""

    def test_key_too_long(self):
        """Test that key > 32 chars raises error."""
        mixin = TagsMixin()
        with pytest.raises(ValueError, match="must be 1-32 characters"):
            mixin.tag("a" * 33, "value")

    def test_key_empty(self):
        """Test that empty key raises error."""
        mixin = TagsMixin()
        with pytest.raises(ValueError, match="must be 1-32 characters"):
            mixin.tag("", "value")

    def test_key_uppercase(self):
        """Test that uppercase key raises error."""
        mixin = TagsMixin()
        with pytest.raises(ValueError, match="must contain only lowercase"):
            mixin.tag("Team", "value")

    def test_key_with_numbers_rejected(self):
        """Test that numbers in key are rejected."""
        mixin = TagsMixin()
        with pytest.raises(ValueError, match="must contain only lowercase"):
            mixin.tag("team123", "value")

    def test_key_with_special_chars_rejected(self):
        """Test that special chars in key (except underscore) are rejected."""
        mixin = TagsMixin()
        with pytest.raises(ValueError, match="must contain only lowercase"):
            mixin.tag("team-name", "value")

    def test_value_too_long(self):
        """Test that value > 128 chars raises error."""
        mixin = TagsMixin()
        with pytest.raises(ValueError, match="must be 1-128 characters"):
            mixin.tag("team", "a" * 129)

    def test_value_empty(self):
        """Test that empty value raises error."""
        mixin = TagsMixin()
        with pytest.raises(ValueError, match="must be 1-128 characters"):
            mixin.tag("team", "")

    def test_value_uppercase_start(self):
        """Test that value starting with uppercase raises error."""
        mixin = TagsMixin()
        with pytest.raises(ValueError, match="must start with a lowercase letter"):
            mixin.tag("team", "Backend")

    def test_value_number_start(self):
        """Test that value starting with number raises error."""
        mixin = TagsMixin()
        with pytest.raises(ValueError, match="must start with a lowercase letter"):
            mixin.tag("team", "1backend")

    def test_value_with_invalid_chars(self):
        """Test that value with invalid chars raises error."""
        mixin = TagsMixin()
        with pytest.raises(ValueError, match="can only contain lowercase letters"):
            mixin.tag("team", "back_end")  # Underscore not allowed in value

    def test_value_with_uppercase_rejected(self):
        """Test that uppercase in value is rejected."""
        mixin = TagsMixin()
        with pytest.raises(ValueError, match="can only contain lowercase letters"):
            mixin.tag("team", "backEnd")

    def test_max_tags_limit(self):
        """Test that max 10 tags are allowed."""
        mixin = TagsMixin()
        for i in range(10):
            mixin.tag(f"key{chr(97 + i)}", f"value{i}")

        with pytest.raises(ValueError, match="Maximum of 10 tags allowed"):
            mixin.tag("keyk", "value10")

    def test_tags_dict_validates_each_tag(self):
        """Test that tags() dict method validates each tag."""
        mixin = TagsMixin()
        with pytest.raises(ValueError, match="must contain only lowercase"):
            mixin.tags({"Team": "backend"})


class TestTagsMixinEdgeCases:
    """Tests for edge cases in tag handling."""

    def test_valid_minimal_tag(self):
        """Test minimal valid tag."""
        mixin = TagsMixin()
        mixin.tag("a", "b")
        assert mixin._tags[0] == {"key": "a", "value": "b"}

    def test_valid_maximal_key(self):
        """Test maximum length key."""
        mixin = TagsMixin()
        key = "a" * 32
        mixin.tag(key, "value")
        assert mixin._tags[0]["key"] == key

    def test_valid_maximal_value(self):
        """Test maximum length value."""
        mixin = TagsMixin()
        value = "a" * 128
        mixin.tag("team", value)
        assert mixin._tags[0]["value"] == value

    def test_value_all_numbers_after_first_char(self):
        """Test value with all numbers after first char."""
        mixin = TagsMixin()
        mixin.tag("team", "a123456789")
        assert mixin._tags[0]["value"] == "a123456789"

    def test_value_with_multiple_slashes(self):
        """Test value with multiple slashes."""
        mixin = TagsMixin()
        mixin.tag("path", "team/platform/api")
        assert mixin._tags[0]["value"] == "team/platform/api"

    def test_value_with_multiple_dashes(self):
        """Test value with multiple dashes."""
        mixin = TagsMixin()
        mixin.tag("env", "staging-us-east-1")
        assert mixin._tags[0]["value"] == "staging-us-east-1"

    def test_value_mixed_special_chars(self):
        """Test value with mixed special characters."""
        mixin = TagsMixin()
        mixin.tag("identifier", "team-123/service-456")
        assert mixin._tags[0]["value"] == "team-123/service-456"
