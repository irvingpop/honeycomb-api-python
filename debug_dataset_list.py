#!/usr/bin/env python3
"""Debug script to investigate dataset_list test failure."""

import json
import os
from anthropic import Anthropic
from honeycomb.tools import HONEYCOMB_TOOLS
from deepeval.test_case import LLMTestCase, ToolCall
from deepeval.metrics import ArgumentCorrectnessMetric
from deepeval.models import AnthropicModel

# Get the test case
from tests.integration.test_cases.datasets import TEST_CASES
test_case = [tc for tc in TEST_CASES if tc["id"] == "dataset_list"][0]

print("=" * 80)
print("TEST CASE")
print("=" * 80)
print(f"ID: {test_case['id']}")
print(f"Prompt: {test_case['prompt']}")
print(f"Expected tool: {test_case['expected_tool']}")
print(f"Expected params: {json.dumps(test_case['expected_params'], indent=2)}")
print()

# Get the tool definition (Claude-compatible, no input_examples)
list_datasets_tool = [t for t in HONEYCOMB_TOOLS if t["name"] == "honeycomb_list_datasets"][0]

print("=" * 80)
print("TOOL DEFINITION SENT TO CLAUDE")
print("=" * 80)
print(json.dumps(list_datasets_tool, indent=2))
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

print("=" * 80)
print("CLAUDE'S RESPONSE")
print("=" * 80)
print(f"Stop reason: {response.stop_reason}")
print(f"Content blocks: {len(response.content)}")
for i, block in enumerate(response.content):
    print(f"\nBlock {i}: {block.type}")
    if block.type == "tool_use":
        print(f"  Tool: {block.name}")
        print(f"  Input: {json.dumps(block.input, indent=4)}")
    else:
        print(f"  Text: {block.text}")
print()

# Extract tool call
tool_calls = [block for block in response.content if block.type == "tool_use"]
if tool_calls:
    tool_call = tool_calls[0]

    print("=" * 80)
    print("DEEPEVAL TEST CASE")
    print("=" * 80)
    test_case_obj = LLMTestCase(
        input=test_case["prompt"],
        actual_output="",
        tools_called=[
            ToolCall(name=tool_call.name, input_parameters=tool_call.input)
        ],
    )
    print(f"Input: {test_case_obj.input}")
    print(f"Tool called: {test_case_obj.tools_called[0].name}")
    print(f"Parameters: {json.dumps(test_case_obj.tools_called[0].input_parameters, indent=2)}")
    print()

    print("=" * 80)
    print("RUNNING DEEPEVAL METRIC")
    print("=" * 80)
    eval_model = AnthropicModel(model="claude-sonnet-4-5-20250929")
    metric = ArgumentCorrectnessMetric(threshold=0.7, model=eval_model)
    metric.measure(test_case_obj)

    print(f"Score: {metric.score}")
    print(f"Reason: {metric.reason}")
    print(f"Success: {metric.success}")
    print()
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print(f"Expected params: {json.dumps(test_case['expected_params'], indent=2)}")
    print(f"Actual params:   {json.dumps(tool_call.input, indent=2)}")
    print(f"Match: {tool_call.input == test_case['expected_params']}")
else:
    print("ERROR: No tool call found!")
