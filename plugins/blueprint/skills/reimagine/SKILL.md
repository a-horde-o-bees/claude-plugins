---
name: reimagine
description: |
  Abstract an existing capability into a generalized problem description for unbiased solution research. Reads target, extracts what problem it solves without implementation bias, and captures system constraints.
argument-hint: "--target <path | natural language description>"
allowed-tools:
  - Read
  - Write
  - AskUserQuestion
---

# /reimagine

Abstract an existing capability into a generalized problem description for unbiased solution research. Separates what a capability does (the problem it solves) from how it currently works (implementation details). System constraints (platform, runtime, invocation model) are preserved as research filters — they narrow results without shaping the search.

Produces an unbiased starting point so that research finds existing tools, proven approaches, and established patterns that fulfill the same purpose — including solutions that could be adopted directly rather than rebuilt.

## Trigger

User runs `/reimagine`

## Route

1. If not --target: Exit to user — respond with skill description and argument-hint
2. If {target} is a file path:
    1. {target-path} = {target}
    2. {target-type} = file
3. Else if {target} is a directory path:
    1. {target-directory} = {target}
    2. {target-type} = directory
4. Else:
    1. {target-description} = {target}
    2. {target-type} = description
5. Dispatch Workflow

## Workflow

1. Gather target content:
    1. If {target-type} is `directory`:
        1. Read SKILL.md in {target-directory} if present
        2. Read all `_*.md` component files in {target-directory}
        3. Read README.md in {target-directory} if present
    2. Else if {target-type} is `file`:
        1. Read {target-path}
    3. Else:
        1. Go to step 3. Present scope
2. Spawn agent with abstraction:
    1. Read `_abstraction-instructions.md`
    2. Analyze target content
    3. Return:
        - Generalized scope statement
        - System constraints list
3. Present scope — display generalized scope statement and system constraints; if {target-type} is `description`, present {target-description} as scope with empty constraints
4. User refines or approves scope via AskUserQuestion:
    1. If user approves: proceed
    2. Else: incorporate refinements, re-present scope; repeat until approved
5. Exit to user — present approved scope statement for user to provide as `/blueprint:research` target

### Report

- Generalized scope statement (approved version)
- System constraints
- Next step: `/blueprint:research [scope]`

## Rules

- Abstraction agent extracts what the target does (problem it solves), not how it currently works (implementation details)
- System constraints are literal facts about the deployment environment — they narrow research without biasing toward specific approaches
- Implementation details of the current solution are excluded from scope — they represent one approach, not the problem definition
- Generalized scope uses domain-neutral language — describe the problem category, not the existing tool
- User refinement is the final gate before initialization — agent produces initial abstraction, user adjusts
- Natural language targets skip abstraction — user already provided a generalized description; present for constraint addition and confirmation
- Reimagine does not manage blueprint infrastructure — initialization and state checking are research's responsibility
