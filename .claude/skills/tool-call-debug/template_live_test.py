#!/usr/bin/env python3
"""Template for live API testing of tool calls.

Usage:
    1. Copy this file to /tmp/test_tool_call.py
    2. Edit the tool_input variable with your test data
    3. Run: direnv exec . poetry run python /tmp/test_tool_call.py
"""
import asyncio
import json
import os
from honeycomb import HoneycombClient
from honeycomb.tools import execute_tool


async def main():
    api_key = os.environ.get("HONEYCOMB_API_KEY")
    if not api_key:
        print("ERROR: HONEYCOMB_API_KEY not set")
        return

    async with HoneycombClient(api_key=api_key) as client:
        dataset = "test-dataset"  # TODO: Change to your dataset

        print("=" * 80)
        print("Live Tool Call Test")
        print("=" * 80)

        # Step 1: Send events to create dataset and columns
        print("\n1. Creating dataset with sample events...")
        events = [
            # TODO: Add events with all columns needed by your queries
            {
                "column1": "value1",
                "column2": 123,
                "column3": "test",
            },
            {
                "column1": "value2",
                "column2": 456,
                "column3": "test2",
            },
        ]

        for event in events:
            await client.events.send_async(dataset, data=event)

        print(f"  ✓ Sent {len(events)} events")
        print("  Waiting 3 seconds for dataset creation...")
        await asyncio.sleep(3)

        # Step 2: Validate tool input client-side
        print("\n2. Validating tool input...")

        # TODO: Replace with your tool input
        tool_input = {
            "name": "Test Board",
            "inline_query_panels": [
                {
                    "name": "Panel 1",
                    "dataset": dataset,
                    "time_range": 3600,
                    "calculations": [{"op": "COUNT"}],
                }
            ],
        }

        # Validate before executing
        from honeycomb.models.tool_inputs import BoardToolInput  # or TriggerToolInput, SLOToolInput
        from pydantic import ValidationError

        try:
            validated = BoardToolInput.model_validate(tool_input)
            print(f"  ✓ Validation passed ({len(validated.inline_query_panels)} panels)")
        except ValidationError as e:
            print("  ✗ Validation FAILED:")
            print(f"    {e.errors()[0]['msg'][:300]}...")
            return

        # Step 3: Execute tool
        print("\n3. Executing tool...")

        tool_name = "honeycomb_create_board"  # TODO: Change to your tool

        try:
            result_json = await execute_tool(client, tool_name, tool_input)
            result = json.loads(result_json)

            print(f"  ✅ SUCCESS")
            print(f"     Result: {json.dumps(result, indent=2)[:500]}...")

            # Cleanup
            resource_id = result.get("id")
            if resource_id and tool_name == "honeycomb_create_board":
                await client.boards.delete_async(resource_id)
                print(f"     Cleaned up resource {resource_id}")

        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            print(f"     Error type: {type(e).__name__}")

            error_str = str(e)

            # Analyze error type
            if "same QueryID" in error_str:
                print("\n  → Duplicate QueryID detected by API")
                print("  → Validator should have caught this!")

                # Show which panels are duplicates
                from honeycomb.validation.boards import generate_query_signature

                signatures = {}
                for i, panel in enumerate(validated.inline_query_panels, 1):
                    sig = generate_query_signature(panel)
                    if sig in signatures:
                        print(f"     Panel {i} duplicates Panel {signatures[sig]}")
                    else:
                        signatures[sig] = i

            elif "Duplicate query" in error_str:
                print("\n  → Validator caught the duplicate ✓")

            elif "400" in error_str or "422" in error_str:
                print("\n  → Validation error from API")
                print(f"     {error_str[:200]}")

            print(f"\n  Full error:\n  {error_str}")


if __name__ == "__main__":
    asyncio.run(main())
