# Code Review Skill — Plan

## Overview

Create a Bob skill (`SKILL.md`) named `review` that teaches Bob how to perform structured,
on-demand code reviews. When activated (via `/review` or natural language like "review this
code"), Bob follows a step-by-step procedure and outputs a structured markdown report with a
section per concern area: **Security**, **Logic**, **Style**, **Architecture**, and
**Dependencies**.

The skill lives at `.bob/skills/review/SKILL.md` (workspace scope).

---

## Sub-Tasks

### Sub-Task 1 — Create the skill directory and SKILL.md file

**Intent**
Author the `review` skill file with correct frontmatter (name, description) and a clear
procedural body that instructs Bob to gather context, analyse the code, and produce the
structured report.

**Expected Outcomes**
- File `.bob/skills/review/SKILL.md` exists with valid frontmatter.
- Skill name `review` matches the directory name (satisfies the `^[a-z0-9]+(-[a-z0-9]+)*$` rule).
- The body defines numbered steps Bob follows during a review session.
- Activating `/review` (or saying "review this code") loads the skill and begins the workflow.

**Todo List**
1. Create directory `.bob/skills/review/`.
2. Write `.bob/skills/review/SKILL.md` with:
   - Frontmatter: `name: review`, `description:` trigger phrase covering `/review` and
     "review this code" intent.
   - **Step 1 — Gather scope**: ask which file(s), PR diff, or code snippet to review if not
     already provided; ask whether any concern areas should be skipped.
   - **Step 2 — Read the code**: use `read_file` (or accept pasted code) to load the target.
   - **Step 3 — Analyse per concern area** (in order):
     - **Security**: credential exposure, injection risks, unsafe deserialization, missing
       input validation, insecure dependencies.
     - **Logic**: off-by-one errors, unhandled edge cases, incorrect branching, missing
       null/error handling.
     - **Style**: naming conventions, dead code, overly complex expressions, inconsistency
       with surrounding code.
     - **Architecture**: coupling, separation of concerns, violation of existing patterns,
       scalability concerns.
     - **Dependencies**: unnecessary additions, pinned vs. floating versions, known-vulnerable
       packages, licence conflicts.
   - **Step 4 — Produce the report**: output a markdown report with one `##` section per
     concern area; each finding is a bullet with severity tag (`🔴 High`, `🟡 Medium`,
     `🟢 Low`) and a short recommendation. Include a **Summary** section at the top.
   - **Step 5 — Offer follow-up**: ask whether the user wants a deep-dive on any finding or
     wants a corrected code snippet generated.

**Relevant Context**
- Skill file location: `.bob/skills/review/SKILL.md`
- Name validation regex: `^[a-z0-9]+(-[a-z0-9]+)*$`
- Security constraints from `AGENTS.md` and `SECURITY.MD` must inform the Security step
  (IBM Cloud credential exposure, `.env` file checks, no hardcoded secrets).
- No supporting script needed — the analysis is open-ended and tool-call based.

**Status**: `[x] done`

---

### Sub-Task 2 — Validate the skill is discoverable

**Intent**
Confirm the skill file is correctly structured so Bob will auto-discover and auto-invoke it.

**Expected Outcomes**
- `SKILL.md` frontmatter is valid YAML with `name` and `description` fields.
- Directory name matches `name` field exactly.
- The skill appears available in the next Bob session.

**Todo List**
1. Re-read `.bob/skills/review/SKILL.md` and verify frontmatter parses cleanly.
2. Check directory name matches the `name` field (`review` == `review`).
3. Confirm no invalid characters in name (uppercase, underscores, spaces, double dashes).
4. Confirm `description` field contains concrete trigger phrases.

**Relevant Context**
- From `create-skill` skill guide: "An invalid name causes the skill to be skipped with no
  error."
- The skill takes effect in the **next** Bob task/conversation after file creation.

**Status**: `[x] done`

---

## Non-Goals

- No supporting shell script — free-form model analysis is appropriate here.
- No separate skills per concern area — one `review` skill covers all areas.
- No modification of `.bobignore` or `.gitignore`.
- No changes to existing mode rules or `AGENTS.md` files.
