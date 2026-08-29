# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Documentation Context (Non-Obvious)

- **There is no application code** in this repo — it is a bare template. Do not reference src/, app/, or test directories; they do not exist yet.
- `SECURITY.MD` (uppercase .MD extension) is the security guide — not the conventional lowercase `.md`.
- The `bob_sessions/` folder appears in `.bobignore` (preventing Bob from logging it) but live session files within it are also git-ignored. However, **exported session reports from bob_sessions/ must be committed** for hackathon submission (per `.gitignore` line 10 comment).
- The `.env.example` file is the only committed credential-related file — it exists specifically because `.gitignore` has a `!.env.example` exception (line 23).
- This template supports Node.js, Python, or Java — there is no single "correct" language for the project.
