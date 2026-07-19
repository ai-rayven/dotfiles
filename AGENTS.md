# Agent Guidelines

## Writing 
- Never use the em dash "—". Use plain dash "-" instead

## Commits
- When writing commit messages, NEVER auto-add your agent name as co-author.
- Commit messages should be concise.
- Commits should be small, focused and individually testable.

## Decision Making
- When making technical decisions, do not give much weight to development cost. Instead, prefer quality, simplicity, robustness, scalability, and long term maintainability.
- Write zero speculative code (YAGNI).

## Workflow
- When doing bug fixes, always start with reproducing the bug in an E2E setting as closely aligned with how an end user would experience it as possible. This makes sure you find the real problem so your fix will actually solve it.
- Run the full automated gate (typing, linting, tests) via a single command. Do not run individual commands, instead use proper idiom for creating a reusable test command that runs everything at once.

# Coding Style
- All functions should have input validation with guards at the beginning.
- Resolve inputs and guard/assert them at the top of a function, then pass final values to the main logic 
- Favor early returns over deep nesting and chained `or` fall-throughs.
- Prefer a named class over multi-value tuples for functions returning several related values or with many parameters, so the contract is self-documenting and safe to extend.
- Co-locate data conversion and serialization logic exactly where the system crosses an external boundary.
