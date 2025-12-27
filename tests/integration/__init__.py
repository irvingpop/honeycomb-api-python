"""Integration tests for the Honeycomb Python SDK.

These tests run against the live Honeycomb API.

Setup:
    1. Configure management credentials in .envrc
    2. Run: direnv exec . poetry run python tests/integration/setup_test_session.py
    3. Run: direnv exec . poetry run pytest tests/integration/ -v
"""
