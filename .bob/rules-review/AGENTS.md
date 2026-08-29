
# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Architectural Constraints (Non-Obvious)

- **Security scaffolding is locked** — `.bobignore` and `.gitignore` contain mandatory patterns that must not be changed. Any planned feature that requires files named with `credential`, `secret`, `password`, `token`, `config.json`, `config.yaml`, or `secrets.*` must use different filenames.
- **No build system exists yet** — planning must include setting up the build/test pipeline from scratch (no package.json, no requirements.txt, no pom.xml currently).
- The hackathon requires the `bob_sessions/` folder to be present in the repo with exported reports — factor this into any repo-restructuring plans.
- `dist/`, `build/`, and `target/` output directories are git-ignored — any CI/CD or artifact publication plan must account for this (artifacts cannot be committed to the repo).
- IBM Cloud account suspension is automatic on credential exposure — any architecture involving secrets must route through environment variables exclusively; no fallback to file-based config.
=======
# Project Rules for IBM Bob 2.0

## 1. Code Review & Quality Standards
* Evaluate all proposed changes against OWASP Top 10 security standards (e.g., injection risks, broken access control, insecure deserialization).
* Enforce explicit type annotations, robust error handling, and parameterized database queries.
* Prohibit raw logging of secrets, access tokens, or sensitive user data.
* Follow the Actor-Critic pattern: Generate the code, critique it against security rules, and refine before presenting the final diff.

## 2. Memory & Continuous Improvement
* Document all refactoring decisions and review findings in `.bob/audit_history.log`.
* When reviewing code, check previous findings in the workspace to ensure previously flagged anti-patterns are not repeated.
* Retain context across tasks by verifying workspace status before proposing destructive edits.

## 3. Conventional Commit Enforcement
* All commit messages generated must strictly follow the Conventional Commits specification: `<type>(<scope>): <short description>`
* Allowed types: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `sec`.
* Format:
    - Subject line: Imperative, lowercase, under 72 characters.
    - Body (optional): Explain *what* and *why*, not *how*.
    - Footer (optional): Issue references (e.g., `Closes #123`).

## 4. Automated Pull Request Descriptions
When generating PR descriptions (via `/review --pr-desc`), structure the output using this template:

### Summary of Changes
- Bullet point overview of changes.

### Security & Quality Audit (Actor-Critic)
- **OWASP Compliance:** [Pass / Flagged]
- **Identified Issues & Fixes Applied:** Detail any security/performance fixes.

### Testing & Validation
- Unit/integration test results and verification steps.

