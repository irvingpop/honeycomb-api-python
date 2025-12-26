---
description: Run specific tests by path or pattern
argument-hint: [test-path-or-pattern]
allowed-tools: Bash(poetry run pytest:*)
---

Running tests matching: $1

!`poetry run pytest $1 -v`
