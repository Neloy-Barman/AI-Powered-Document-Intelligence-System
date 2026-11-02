# Developer Instructions

These instructions apply to any project unless the user explicitly says otherwise.

## Scope

- Do exactly what is asked. Nothing more.
- Do not add extra features, files, refactors, comments, or output that were not requested.
- If a requirement is ambiguous, ask before implementing.
- Get the user's approval before starting any new task or change.

## Code Style

- Write clean, readable, production-quality code.
- Follow the standard naming conventions of the language (PEP 8 for Python, camelCase/PascalCase for JavaScript/TypeScript, etc.).
- Use descriptive, meaningful names for variables, functions, classes, and files.
- Add a short, plain-language comment on each line of React/frontend component code so the user (learning React) can follow what it does.
- Do not add unnecessary comments elsewhere; comment only when the logic is genuinely non-obvious.
- Keep functions and methods small and focused on a single responsibility.
- Match the existing structure, patterns, and style of the surrounding codebase.

## Typing

- Add type hints to every function and method argument.
- Add a return type hint to every function and method.
- Prefer precise types over `Any`.
- Use the modern syntax supported by the project's language version (for example, `str | Path` and `dict[str, str | int | list[str]]` in Python 3.10+).

## Error Handling

- Handle expected failures explicitly with specific exception types.
- Catch the narrowest exception first and the generic `Exception` last.
- Never let a known failure crash the flow; return a structured error response instead.
- Include the exception type name in printed or logged error messages, for example `f"{type(error).__name__}: {error}"`.
- Error responses must include a `status` key, the resource or file name, and an `error_message` key.
- Use `"status": "success"` for successful responses and `"status": "failed"` for error responses.

## Response Structure

- Order dictionary keys by priority: `status` first, then the identifying field (such as `file_name`), then the remaining details.
- Keep response schemas consistent across success and failure paths.
- Return only the data that was requested.

## Verification

- Do not claim something works without verifying it.
- Test changes against real inputs whenever possible.

## Communication

- Report only what was done.
- Keep responses concise and avoid unnecessary explanations unless asked.

## Progress Tracking

- Maintain `docs/progress-tracker.md`.
- Update it whenever a new module, component, function, import set, or behavior is implemented.
- Record what was added, where it lives, and what it returns or handles.
- Keep it short, factual, and free of filler or buzzwords.
- Include a brief project overview, implemented work, pending work, and known gaps so another agent can continue from the file alone.
- Maintain `docs/frontend-development-plan.md` for frontend work: check off build-order items, log progress, and revise the requirements table, API contract, or data shapes whenever they change.

## Maintaining This File

- When the user gives an instruction that is general and not project-specific, append it to this file so it does not need to be repeated.

## Dependencies
- When a new dependency is added to `requirements.txt` (or any dependency manifest), install it immediately in the project environment (e.g. `pip install -r requirements.txt` or `pip install <package>`).
- Do not only edit the manifest; keep the environment in sync with it.
- Report the install result so it is clear the dependency is actually available.
