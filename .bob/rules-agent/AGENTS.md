# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Coding Rules (Non-Obvious)

- **Do not create files named** `config.json`, `config.yaml`, `secrets.json`, `secrets.yaml`, or any filename containing `credential`, `secret`, `password`, or `token` — they are git-ignored by wildcard and will silently disappear from version control.
- All credentials must come from environment variables. Node.js: `require('dotenv').config()` + `process.env.VAR`; Python: `load_dotenv()` + `os.getenv('VAR')`; Java: `System.getenv("VAR")`.
- **Do not read or output `.env` file contents** — `.bobignore` blocks it, but this must also be respected in generated code (e.g., no `console.log(process.env)` dumps).
- `.bobignore` patterns are glob-based and case-sensitive per-pattern; both `*API_KEY*` and `*api_key*` are listed separately.
- When adding project source code, avoid placing it in `dist/`, `build/`, or `target/` — these are git-ignored.
- `.vscode/` and `.idea/` directories are git-ignored; do not create IDE config files in the repo.
