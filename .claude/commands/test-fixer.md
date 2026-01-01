---
description: Diagnose and fix failing tests. Use when CI fails or tests are broken.
allowed-tools: Bash(make:*), Bash(poetry run pytest:*), Read, Grep, Glob, Edit
---


# CI: Run Tests and Fix Failures

Run all test suites in the **test-fixer** sub agent and fix any failures iteratively.

## Step 1: Parallel Test Execution

Launch these test runner subagents **in parallel** (single Task tool call with multiple subagents):

### Format tests
- **subagent_type**: general-purpose
- **task**: Run `make format` - Check formatting

### Lint and type checks
- **subagent_type**: general-purpose
- **task**: Run `make check` - Run lint and typecheck

### Unit Tests
- **subagent_type**: general-purpose
- **task**: Run `make test-unit` - Run unit tests

### Docs Tests
- **subagent_type**: general-purpose
- **task**: Run `make validate-docs` - Validate documentation examples

### Claude tools eval tests
- **subagent_type**: general-purpose
- **task**: Run `rm tests/integration/.tool_call_cache/*.json && make test-eval` - Run DeepEval tests against claude tools

## Step 2: Aggregate Results

Collect distilled failures from all subagents. Present a summary table:

| Suite | Passed | Failed | Failures |
|-------|--------|--------|----------|
| frontend | X | Y | list |
| backend-unit | X | Y | list |
| backend-functional | X | Y | list |
| agentic | X | Y | list |

## Step 3: Fix Failures (if any)

For each failure, starting with the fastest suite:

1. Read the failing test and the code under test
2. Determine if the bug is in the test or the implementation
3. Make the minimal fix
4. Do NOT re-run the full suite yet—continue to next failure

## Step 4: Verify Fixes

After all fixes are applied, re-run only the previously failing tests.

If new failures appear, return to Step 3 for those specific failures.

## Step 5: Final Confirmation

Once all targeted tests pass, run the full suite one final time to catch any regressions.

Report final status and summarize all changes made.

## Notes

- If a test appears flaky (passes on retry with no code change), note it but do not modify
- If an agentic test fails due to external API issues, skip and report separately
- If fixes would require architectural changes, stop and report rather than making large modifications
