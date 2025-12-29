"""Unit tests for Claude tool descriptions.

Tests that descriptions accurately reflect tool capabilities and don't mislead Claude.
"""

from honeycomb.tools.descriptions import get_description


class TestDescriptionAccuracy:
    """Test that descriptions accurately reflect tool capabilities."""

    def test_trigger_description_promotes_inline_recipients(self):
        """Trigger description should promote inline recipient creation."""
        desc = get_description("honeycomb_create_trigger")

        # Should mention inline recipients
        assert "inline" in desc.lower(), "Should mention inline recipient support"
        assert "recipients" in desc.lower(), "Should mention recipients"

        # Should NOT tell Claude to create them separately first
        misleading_phrases = [
            "create them first",
            "must already exist",
            "create separately",
        ]
        for phrase in misleading_phrases:
            assert phrase.lower() not in desc.lower(), (
                f"Description should not contain misleading phrase: '{phrase}'"
            )

        # Should indicate inline is preferred
        assert "PREFERRED" in desc or "preferred" in desc.lower(), (
            "Should indicate inline creation is preferred"
        )

    def test_slo_description_promotes_inline_derived_column(self):
        """SLO description should promote inline derived column creation."""
        desc = get_description("honeycomb_create_slo")

        assert "inline" in desc.lower(), "Should mention inline SLI expression support"
        assert "derived column" in desc.lower() or "SLI" in desc, (
            "Should mention derived column/SLI"
        )

    def test_board_description_promotes_inline_panels(self):
        """Board description should promote inline panel creation."""
        desc = get_description("honeycomb_create_board")

        assert "inline" in desc.lower(), "Should mention inline panel creation"
        assert "queries" in desc.lower() or "panels" in desc.lower(), (
            "Should mention queries/panels"
        )

    def test_batch_events_description_clarifies_structure(self):
        """Batch events description should clarify nested structure."""
        desc = get_description("honeycomb_send_batch_events")

        # Should mention structure requirements
        assert "STRUCTURE" in desc or "structure" in desc.lower(), (
            "Should clarify structure requirements"
        )

        # Should emphasize 'events' is required
        assert "events" in desc.lower(), "Should mention 'events' parameter"
        assert "REQUIRED" in desc or "CRITICAL" in desc or "required" in desc.lower(), (
            "Should emphasize 'events' parameter is required"
        )

        # Should mention nested data field
        assert "data" in desc.lower(), "Should mention 'data' field in each event"

    def test_single_event_description_clarifies_flat_structure(self):
        """Single event description should clarify flat structure."""
        desc = get_description("honeycomb_send_event")

        # Should mention it's for SINGLE events only
        assert "SINGLE" in desc or "single" in desc.lower(), (
            "Should clarify this is for single events"
        )

        # Should mention structure is flat
        assert "STRUCTURE" in desc or "flat" in desc.lower(), "Should clarify flat structure"

    def test_send_event_warns_against_multiple_events(self):
        """Single event tool should warn against using for multiple events."""
        desc = get_description("honeycomb_send_event")

        assert "batch" in desc.lower(), "Should mention batch alternative"
        assert "ONLY" in desc or "only" in desc.lower(), "Should emphasize ONLY for single events"


class TestDescriptionConsistency:
    """Test description consistency across related tools."""

    def test_create_vs_list_descriptions_are_complementary(self):
        """Create and list descriptions should complement each other."""
        # Example: list triggers mentions discovering existing, create mentions setting up new
        list_desc = get_description("honeycomb_list_triggers")
        create_desc = get_description("honeycomb_create_trigger")

        # List should mention discovery/inspection
        assert any(word in list_desc.lower() for word in ["discover", "existing", "retrieve"]), (
            "List description should mention discovery"
        )

        # Create should mention creation/setup
        assert any(word in create_desc.lower() for word in ["create", "new", "set up"]), (
            "Create description should mention creation"
        )

    def test_all_descriptions_follow_format(self):
        """All descriptions should follow the standard format."""
        from honeycomb.tools import list_tool_names

        for tool_name in list_tool_names():
            desc = get_description(tool_name)

            # Should be substantial (not just a sentence fragment)
            assert len(desc) >= 50, f"{tool_name}: description too short ({len(desc)} chars)"

            # Should start with present tense verb or noun
            first_word = desc.split()[0]
            assert first_word[0].isupper() or first_word.startswith("honeycomb"), (
                f"{tool_name}: description should start with capital letter"
            )

    def test_key_tools_explain_jargon(self):
        """Key tools should explain technical terms when used."""
        # Only check tools where jargon is central to the functionality
        key_tools_jargon = {
            "honeycomb_create_slo": ("SLI", ["derived column", "indicator"]),
            "honeycomb_create_burn_alert": ("burn alert", ["error budget", "SLO"]),
        }

        for tool_name, (term, explanations) in key_tools_jargon.items():
            desc = get_description(tool_name)

            if term.lower() in desc.lower():
                # If jargon is used, at least one explanation should be present
                has_explanation = any(exp.lower() in desc.lower() for exp in explanations)
                assert has_explanation, (
                    f"{tool_name}: uses '{term}' without explanation (should mention: {explanations})"
                )


class TestCriticalDescriptionIssues:
    """Test for specific misleading or incorrect descriptions."""

    def test_no_descriptions_say_opposite_of_capability(self):
        """No description should tell Claude NOT to use a capability the tool has."""
        problematic_patterns = [
            # Tool has capability X but description says "don't use X" or "create X first"
            ("honeycomb_create_trigger", ["create them first", "must already exist"], "recipients"),
            ("honeycomb_create_slo", ["create it first", "must already exist"], "derived column"),
            ("honeycomb_create_board", ["create them first", "must already exist"], "queries"),
        ]

        for tool_name, bad_phrases, feature in problematic_patterns:
            desc = get_description(tool_name)

            for phrase in bad_phrases:
                assert phrase.lower() not in desc.lower(), (
                    f"{tool_name} description says '{phrase}' about {feature}, "
                    f"but tool supports inline {feature} creation"
                )
