# Agent Guidelines

- Never use the em dash "—". Use plain dash "-" instead
- When writing commit messages, NEVER auto-add your agent name as co-author
- When making technical decisions, do not give much weight to development cost. Instead, prefer quality, simplicity, robustness, scalability, and long term maintainability.
- When doing bug fixes, always start with reproducing the bug in an E2E setting as closely aligned with how an end user would experience it as possible. This makes sure you find the real problem so your fix will actually solve it.
- When end-to-end testing a product, be picky about the UI you see and be obsessed with pixel perfection. If something clearly looks off, even if it is not directly related to what you are doing, try to get it fixed along the way.
- Apply that same high standard to engineering excellence: lint, test failures, and test flakiness. If you see one, even if it is not caused by what you are working on right now, still get it fixed.
- All functions should have input validation with guards at the beginning. This not only prevents excessive fall-through but also makes functions easier to test and maintain.
- Prefer a named class over multi-value tuples for functions returning several related values, so the contract is self-documenting and safe to extend.
- Resolve inputs and guard/assert them at the top of a function, then pass final values to the main logic — favor early returns over deep nesting and chained `or` fall-throughs.
