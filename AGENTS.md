# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Context

This is an **IBM Watsonx Hackathon project template** — a starter repo with no application code yet. The tech stack (Node.js, Python, or Java) is chosen by the team building on top of it.

## Critical Security Constraints

- **Never read, log, or display `.env` files** — `.bobignore` is configured to block this, but enforce it yourself too.
- **Never hardcode credentials** in any file. All secrets must use environment variables.
- **Never modify or remove patterns** from `.bobignore` or `.gitignore` — these are security-mandated.
- The `bob_sessions/` folder is excluded from Bob's logging (`.bobignore` line 96) and git-ignored — but **exported session reports must be committed** (see `.gitignore` line 10).
- Files named with `credential`, `secret`, `password`, or `token` anywhere in the name are git-ignored by wildcard patterns — don't create project files with these words in the filename.
- `config.json`, `config.yaml`, `secrets.json`, `secrets.yaml` are also git-ignored — avoid these as filenames for non-sensitive config too.

## Environment Variables

Primary credential variable names for this project:
- `IBM_CLOUD_API_KEY` — main IBM Cloud credential
- `WATSON_*_API_KEY` / `WATSON_*_URL` — Watson service credentials
- `ASSISTANT_API_KEY`, `DISCOVERY_API_KEY` — specific Watson services

Use `.env.example` as the template; copy to `.env` (never committed).

## Build / Test / Lint Commands

No build system is configured yet — commands depend on the stack the team adds. Once code is added, follow the stack-specific conventions below.

## No Application Code Yet

There are no `src/`, `app/`, `lib/`, or test directories. The only project files are:
- `README.md` — quick start guide
- `SECURITY.MD` — credential management guidelines
- `.env.example` — environment variable template
- `.bobignore` / `.gitignore` — security ignore rules
