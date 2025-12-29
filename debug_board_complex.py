#!/usr/bin/env python3
"""Debug complex board creation test failures."""

import json
import os
from anthropic import Anthropic
from honeycomb.tools import HONEYCOMB_TOOLS
from tests.integration.test_cases.boards import TEST_CASES

# Test both failing cases
test_ids = ["board_create_environment_wide_query", "board_create_inline_slo"]

for test_id in test_ids:
    test_case = [tc for tc in TEST_CASES if tc["id"] == test_id][0]

    print("=" * 80)
    print(f"TEST CASE: {test_id}")
    print("=" * 80)
    print(f"Prompt: {test_case['prompt']}")
    print(f"\nExpected params: {json.dumps(test_case['expected_params'], indent=2)}")
    print()

    # Call Claude
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    system_prompt = (
        "You are a Honeycomb API automation assistant. "
        "When the user asks you to perform operations on Honeycomb resources, "
        "you MUST use the available tools rather than providing conversational responses. "
        "Always call the appropriate tool, even if some parameters are not explicitly specified - "
        "use reasonable defaults. "
        "Only respond conversationally if no appropriate tool is available."
    )
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        tools=HONEYCOMB_TOOLS,
        system=system_prompt,
        messages=[{"role": "user", "content": test_case["prompt"]}],
    )

    tool_calls = [b for b in response.content if b.type == "tool_use"]
    if tool_calls:
        tool_call = tool_calls[0]
        params = tool_call.input

        print("CLAUDE'S TOOL CALL:")
        print(f"Tool: {tool_call.name}")
        print(f"\nFull parameters:\n{json.dumps(params, indent=2)}")
        print()

        print("ASSERTION CHECK RESULTS:")
        for assertion in test_case["assertion_checks"]:
            try:
                result = eval(assertion)
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status}: {assertion}")
                if not result and "inline" in assertion:
                    # Show what we got
                    if "inline_query_panels" in params:
                        print(f"   → Got: {params.get('inline_query_panels', [])}")
                    if "inline_slo_panels" in params:
                        print(f"   → Got: {params.get('inline_slo_panels', [])}")
            except Exception as e:
                print(f"❌ ERROR: {assertion}")
                print(f"   {e}")
        print()
