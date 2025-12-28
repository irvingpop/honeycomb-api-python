#!/usr/bin/env python3
"""Debug query_run_or_filter_combination test failure."""

import json
import os
from anthropic import Anthropic
from honeycomb.tools import HONEYCOMB_TOOLS
from tests.integration.test_cases.queries import TEST_CASES

# Get the failing test case
test_case = [tc for tc in TEST_CASES if tc["id"] == "query_run_or_filter_combination"][0]

print("=" * 80)
print("TEST CASE")
print("=" * 80)
print(f"Prompt: {test_case['prompt']}")
print(f"\nExpected params: {json.dumps(test_case['expected_params'], indent=2)}")
print(f"\nAssertion checks:")
for assertion in test_case["assertion_checks"]:
    print(f"  - {assertion}")
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
    max_tokens=1024,
    tools=HONEYCOMB_TOOLS,
    system=system_prompt,
    messages=[{"role": "user", "content": test_case["prompt"]}],
)

tool_calls = [b for b in response.content if b.type == "tool_use"]
if tool_calls:
    tool_call = tool_calls[0]
    params = tool_call.input

    print("=" * 80)
    print("CLAUDE'S TOOL CALL")
    print("=" * 80)
    print(f"Tool: {tool_call.name}")
    print(f"\nFull parameters:\n{json.dumps(params, indent=2)}")
    print()

    print("=" * 80)
    print("FILTERS ANALYSIS")
    print("=" * 80)
    if "filters" in params:
        for i, f in enumerate(params["filters"]):
            print(f"Filter {i}: column={f.get('column')}, op={f.get('op')}, value={f.get('value')} (type: {type(f.get('value'))})")
    print()

    print("=" * 80)
    print("ASSERTION CHECK RESULTS")
    print("=" * 80)
    for assertion in test_case["assertion_checks"]:
        try:
            result = eval(assertion)
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {assertion}")
        except Exception as e:
            print(f"❌ ERROR: {assertion}")
            print(f"   {e}")
else:
    print("ERROR: No tool call found!")
