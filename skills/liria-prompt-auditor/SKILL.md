---
name: liria-prompt-auditor
description: Use when maintaining the LIRIA repo's prompt/session hygiene, auditing prompt bloat, autosave or runtime-rule contradictions, numbered choice leaks, hotset/index growth, or deciding whether to run scripts/liria_prompt_auditor.py before changing prompt or session templates.
---

# LIRIA Prompt Auditor

Use this skill for LIRIA maintenance that touches prompt files, session templates, save/resume behavior, or game-runtime rules. Keep maintenance tooling out of in-game prompt text and preserve the play experience first.

## Workflow

1. Inspect the worktree first. Other workers may have prompt, template, script, or docs edits in flight; do not revert them.
2. Run the read-only auditor when the task involves prompt/session hygiene, save/resume rules, runtime rules, or before accepting broad prompt/template edits:

```bash
python scripts/liria_prompt_auditor.py --root .
```

For a concrete save/session directory:

```bash
python scripts/liria_prompt_auditor.py --root . --session saves/session_name
```

Use `--fail-on-warning` for CI-style gating or when the user asks for strict validation.

3. Treat auditor output as triage, not an automatic rewrite request. Read the reported file and nearby context before editing.
4. Keep edits scoped to the user's request. Avoid touching prompt, script, docs, README, or template files unless the user explicitly asked for those changes.
5. Re-run the auditor after relevant edits and report remaining warnings/errors with rationale if any are intentionally left.

## What To Look For

- Prompt bloat: oversized prompt files, repeated policy blocks, duplicated save/compress guidance, or maintenance instructions leaking into runtime prompt sources.
- Session bloat: `hotset.md` becoming a log/archive instead of a compact resume cache, long event-index prose, missing resume anchors, or missing read-priority guidance in indexes.
- Runtime safety: contradictory autosave cadence, `hotset` described as source of truth, hard numbered player choices in prose-facing prompt files, or rules that would slow play by requiring extra maintenance commands every scene.

## Safe Runtime Rules

- `hotset` is a compact resume cache, not the canonical archive or full log.
- Autosave policy should be lightweight and consistent; avoid adding multiple competing mechanisms or per-scene command burdens.
- Game-facing prompts should stay diegetic and flexible. Avoid hardcoded numbered player choices unless the context is tooling, setup, or a checklist.
- Maintenance/audit instructions belong in skills, scripts, docs, or operator workflows, not in prompts the game runtime consumes.
