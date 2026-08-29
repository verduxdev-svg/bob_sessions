# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Architectural Constraints (Non-Obvious)

- **Security scaffolding is locked** — `.bobignore` and `.gitignore` contain mandatory patterns that must not be changed. Any planned feature that requires files named with `credential`, `secret`, `password`, `token`, `config.json`, `config.yaml`, or `secrets.*` must use different filenames.
- **No build system exists yet** — planning must include setting up the build/test pipeline from scratch (no package.json, no requirements.txt, no pom.xml currently).
- The hackathon requires the `bob_sessions/` folder to be present in the repo with exported reports — factor this into any repo-restructuring plans.
- `dist/`, `build/`, and `target/` output directories are git-ignored — any CI/CD or artifact publication plan must account for this (artifacts cannot be committed to the repo).
- IBM Cloud account suspension is automatic on credential exposure — any architecture involving secrets must route through environment variables exclusively; no fallback to file-based config.
