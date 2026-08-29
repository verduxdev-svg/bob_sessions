---
name: review
description: Use when the user wants to review code, a file, or a PR — performs a structured code review covering security, logic, style, architecture, and dependencies, then outputs a markdown report with severity-tagged findings.
---

# Code Review

Follow these steps in order whenever the user asks for a code review, types `/review`, or says something like "review this code", "can you review my changes", or "check this file".

## Step 1 — Gather Scope

Use `ask_followup_question` if the target is not already clear:
- Which file(s), diff, or code snippet should be reviewed?
- Are any concern areas out of scope for this review (e.g. skip style)?

If the user has already provided code or a filename, proceed directly to Step 2.

## Step 2 — Read the Code

- If a filename was given, use `read_file` to load it. For large files, read the relevant range first.
- If a diff or snippet was pasted inline, use that directly — no tool call needed.
- If multiple files are involved, read each one before starting the analysis.

## Step 3 — Analyse Per Concern Area

Work through each area below in order. For each finding, note the file and line number (if known), a brief description, and a severity:
- 🔴 **High** — must fix before shipping (security holes, data loss, crashes)
- 🟡 **Medium** — should fix (correctness issues, fragile logic, noisy warnings)
- 🟢 **Low** — consider fixing (style, minor inconsistency, nice-to-have)

### Security
- Hardcoded credentials, API keys, tokens, or passwords in source (check for patterns like `API_KEY =`, `password =`, string literals that look like keys)
- Environment variable usage — are secrets coming from `process.env` / `os.getenv` / `System.getenv`, not from files?
- Input validation and sanitisation — SQL injection, command injection, XSS, path traversal
- Unsafe deserialization or eval-like constructs
- Overly permissive file/network access

### Logic
- Off-by-one errors in loops or array access
- Unhandled edge cases (empty input, null/undefined, zero, negative numbers)
- Incorrect branching or inverted conditions
- Missing error handling or swallowed exceptions
- Race conditions or incorrect async/await usage

### Style
- Naming that is unclear, inconsistent with the surrounding code, or misleading
- Dead code — unreachable branches, unused variables/imports
- Overly complex expressions that should be broken up
- Inconsistent formatting or indentation relative to the rest of the file

### Architecture
- Tight coupling between components that should be independent
- Violations of the existing separation-of-concerns pattern in the codebase
- Logic placed in the wrong layer (e.g. business logic in a route handler)
- Scalability concerns — O(n²) loops over large collections, unbounded growth
- Duplication of logic that already exists elsewhere

### Dependencies
- New packages added without clear justification
- Floating version ranges (`*`, `latest`, `^`) on packages where stability matters
- Known-vulnerable packages (flag if the package is old or well-known to have CVEs)
- Licence conflicts with the project's licence
## Step 3.1 — Actor-Critic Validation
Before generating the final report, act as the Critic. Review the initial findings against strict OWASP ASVS standards. Discard any false positives. For every 🔴 High severity issue, internally draft a remediation code patch, critique your own patch for secondary vulnerabilities or performance regressions, and refine the patch before presenting it in Step 4.
## Step 4 — Output the Report

Produce a markdown report using this exact structure:

```
## Code Review: <filename or description>

### Summary
<2–4 sentence overview of the overall quality and the most important findings>

### 🔐 Security
<findings as bullets, or "No findings." if clean>

### 🧠 Logic
<findings as bullets, or "No findings." if clean>

### 🎨 Style
<findings as bullets, or "No findings." if clean>

### 🏗️ Architecture
<findings as bullets, or "No findings." if clean>

### 📦 Dependencies
<findings as bullets, or "No findings." if clean>
```

Each finding bullet follows this format:
- `[SEVERITY EMOJI] **Short title** (line N)` — explanation + recommended fix
After the markdown report, append a valid SARIF v2.1.0 JSON snippet containing all 🔴 High and 🟡 Medium severity findings inside a JSON code block. This ensures the output is immediately actionable for CI/CD pipelines and external AI agents.

Example:
- `🔴 **Hardcoded API key** (line 12)` — `API_KEY = "sk-abc123"` must be moved to an environment variable. Use `process.env.API_KEY` instead.

## Step 5 — Offer Follow-Up

After delivering the report, ask:
> Would you like me to deep-dive on any finding, or generate a corrected version of the affected code?

Use `ask_followup_question` to present options if there are multiple high-severity findings worth addressing first.
