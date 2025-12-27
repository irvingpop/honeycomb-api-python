#!/usr/bin/env python3
"""Set up a test session for integration testing.

This script uses the Management API to create a test environment and API key.
Credentials are saved to .claude/secrets/ for use by integration tests.

Usage:
    direnv exec . poetry run python tests/integration/setup_test_session.py

Prerequisites:
    - HONEYCOMB_MANAGEMENT_KEY and HONEYCOMB_MANAGEMENT_SECRET set in .envrc
"""

from __future__ import annotations

import asyncio
import json
import os
import secrets
import sys
from pathlib import Path

import httpx

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
SECRETS_DIR = PROJECT_ROOT / ".claude" / "secrets"


def get_management_credentials() -> tuple[str, str]:
    """Get management API credentials from environment."""
    mgmt_key = os.environ.get("HONEYCOMB_MANAGEMENT_KEY")
    mgmt_secret = os.environ.get("HONEYCOMB_MANAGEMENT_SECRET")

    if not mgmt_key or not mgmt_secret:
        print("ERROR: Management key not configured")
        print("Set HONEYCOMB_MANAGEMENT_KEY and HONEYCOMB_MANAGEMENT_SECRET in .envrc")
        sys.exit(1)

    return mgmt_key, mgmt_secret


async def get_team_slug(http: httpx.AsyncClient, headers: dict[str, str]) -> str:
    """Get the team slug from the auth endpoint."""
    resp = await http.get("https://api.honeycomb.io/2/auth", headers=headers)
    resp.raise_for_status()
    auth_data = resp.json()

    # Find team slug in included data
    for item in auth_data.get("included", []):
        if item.get("type") == "teams":
            return item["attributes"]["slug"]

    raise RuntimeError("Could not determine team slug from auth response")


async def find_or_create_test_environment(
    http: httpx.AsyncClient,
    headers: dict[str, str],
    team_slug: str,
) -> dict:
    """Find existing test environment or create a new one."""
    base_url = f"https://api.honeycomb.io/2/teams/{team_slug}/environments"

    resp = await http.get(base_url, headers=headers)
    resp.raise_for_status()
    envs = resp.json()
    print(f"Found {len(envs['data'])} environments")

    # Look for existing test environment
    for env in envs["data"]:
        if "sdk-test" in env["attributes"]["name"].lower():
            print(f"Using existing test environment: {env['attributes']['name']}")
            return env

    # Create new test environment
    print("Creating new test environment...")
    create_data = {
        "data": {
            "type": "environments",
            "attributes": {
                "name": f"python-sdk-test-{secrets.token_hex(4)}",
                "description": "Auto-created for Python SDK integration testing",
            },
        }
    }
    resp = await http.post(base_url, headers=headers, json=create_data)
    if resp.status_code != 201:
        print(f"Failed to create environment: {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    env = resp.json()["data"]
    print(f"Created environment: {env['attributes']['name']} ({env['id']})")
    return env


async def create_api_key(
    http: httpx.AsyncClient,
    headers: dict[str, str],
    team_slug: str,
    environment_id: str,
) -> tuple[str, str]:
    """Create a configuration API key for the test environment."""
    print("Creating configuration API key...")
    key_data = {
        "data": {
            "type": "api-keys",
            "attributes": {
                "key_type": "configuration",
                "name": f"sdk-test-key-{secrets.token_hex(4)}",
                "permissions": {
                    "create_datasets": True,
                    "manage_triggers": True,
                    "manage_boards": True,
                    "manage_slos": True,
                    "manage_markers": True,
                    "manage_recipients": True,
                    "manage_columns": True,
                    "manage_queries": True,
                    "send_events": True,
                    "run_queries": True,
                    "read_service_maps": True,
                },
            },
            "relationships": {
                "environment": {
                    "data": {
                        "id": environment_id,
                        "type": "environments",
                    }
                }
            },
        }
    }
    resp = await http.post(
        f"https://api.honeycomb.io/2/teams/{team_slug}/api-keys",
        headers=headers,
        json=key_data,
    )
    if resp.status_code != 201:
        print(f"Failed to create API key: {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    key_response = resp.json()
    # Configuration keys return key ID + secret separately
    key_id = key_response["data"]["id"]
    key_secret = key_response["data"]["attributes"]["secret"]
    # For configuration keys, use just the secret as the API key
    api_key = key_secret
    print(f"Created API key: {key_id}")
    return api_key, key_id


def save_session(
    env_id: str,
    env_name: str,
    env_slug: str,
    api_key: str,
    api_key_id: str,
) -> None:
    """Save session credentials to secrets directory."""
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)

    # Save session metadata (no secrets)
    session = {
        "environment_id": env_id,
        "environment_name": env_name,
        "environment_slug": env_slug,
        "api_key_id": api_key_id,
    }
    with open(SECRETS_DIR / "session.json", "w") as f:
        json.dump(session, f, indent=2)

    # Save API key for use by tests
    with open(SECRETS_DIR / "test.env", "w") as f:
        f.write(f'export HONEYCOMB_API_KEY="{api_key}"\n')
        f.write('export HONEYCOMB_TEST_DATASET="integration-test"\n')

    print(f"\nSession saved to {SECRETS_DIR}")


async def main() -> int:
    """Set up test session."""
    print("=" * 60)
    print("Setting up Integration Test Session")
    print("=" * 60)

    mgmt_key, mgmt_secret = get_management_credentials()
    headers = {
        "Authorization": f"Bearer {mgmt_key}:{mgmt_secret}",
        "Content-Type": "application/vnd.api+json",
    }

    async with httpx.AsyncClient() as http:
        # Verify management key and get team slug
        print("\nVerifying management key...")
        team_slug = await get_team_slug(http, headers)
        print(f"Authenticated to team: {team_slug}")

        # Find or create test environment
        env = await find_or_create_test_environment(http, headers, team_slug)

        # Create API key (needs environment ID, not slug)
        api_key, api_key_id = await create_api_key(http, headers, team_slug, env["id"])

        # Save session
        save_session(
            env_id=env["id"],
            env_name=env["attributes"]["name"],
            env_slug=env["attributes"]["slug"],
            api_key=api_key,
            api_key_id=api_key_id,
        )

    print("\n" + "=" * 60)
    print("Test session ready!")
    print(f"Environment: {env['attributes']['name']}")
    print("Run integration tests with:")
    print("  direnv exec . poetry run pytest tests/integration/ -v")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
