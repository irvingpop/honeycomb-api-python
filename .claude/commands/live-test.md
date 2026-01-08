---
description: Run live API tests against real Honeycomb
argument-hint: [scope: all|crud|docs|<resource>]
allowed-tools: Bash(direnv exec:*)
---

Running live API tests with scope: ${1:-all}

Prerequisites:
- HONEYCOMB_API_KEY or HONEYCOMB_MANAGEMENT_KEY must be set in .envrc
- Run 'direnv allow' if you've updated .envrc

!`rm tests/integration/.tool_call_cache/*.json`
!`direnv exec . make test-eval`
!`direnv exec . make test-live`
