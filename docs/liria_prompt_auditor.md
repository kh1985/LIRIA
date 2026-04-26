# LIRIA Prompt Auditor

`scripts/liria_prompt_auditor.py` is a repo-local development auditor. It helps maintainers diagnose prompt bloat and session-memory hygiene without participating in the game runtime.

This document and the script are not game instructions. Do not include them from `prompt/`, `play.sh`, scenario prompt assembly, generated Claude/Codex prompts, or session templates.

## Scope

The auditor checks text files for review signals in these areas:

- Prompt bloat: large prompt files, repeated autosave language, and maintenance auditor text leaking into runtime prompt sources.
- Prompt assembly profiles: `scenarios/liria/config.sh` fast/full, new/resume file lists, total assembled character counts, missing files, and optional heavy prompt files accidentally included in the fast profile.
- Hard numbered choices: player-facing prompt files that appear to force numbered menus such as `1. ... 2. ... 3. ...`.
- Autosave contradictions: nearby wording that mixes incompatible save cadence, source-of-truth claims, or regresses to running autosave helpers every scene.
- Sidecar read policy: `event_index.md`, `mechanics_card.md`, checkpoint, and sidecar references that appear in mandatory-read wording instead of need-driven wording.
- Hotset hygiene: `hotset.md` growing beyond a compact resume cache or containing archive/source-of-truth language.
- Cast index hygiene: unresolved placeholders, missing read-priority guidance, or active NPC pressure without NPC cards.
- Event index hygiene: missing event index templates, very large event indexes, or entries that look like full prose dumps.

The checks are intentionally heuristic. A warning means "look here", not "the repo is wrong".
`INFO` lines report prompt profile sizes and do not affect the exit code.

## Usage

```bash
python scripts/liria_prompt_auditor.py
```

Optional session audit:

```bash
python scripts/liria_prompt_auditor.py --session saves/session_002
```

Optional stricter output:

```bash
python scripts/liria_prompt_auditor.py --fail-on-warning
```

Exit codes:

- `0`: no errors; warnings may exist unless `--fail-on-warning` was used.
- `1`: one or more errors, or warnings with `--fail-on-warning`.
- `2`: invalid arguments or missing paths.

The profile size report approximates the launcher assembly by reading each configured prompt file and joining files with blank lines. It is meant for quick comparison between `fast` and `full`, not byte-perfect reproduction of generated prompt artifacts.

## Expected Workflow

1. Run the auditor before or after prompt-maintenance changes.
2. Review findings manually.
3. If a finding is intentional, note it in the maintenance task evidence instead of weakening the heuristic immediately.
4. Keep fixes in runtime prompt/session files separate from changes to the auditor itself when possible.

## Design Notes

- The script is dependency-free Python and read-only.
- It does not inspect ignored personal logs unless a session path is explicitly provided.
- It should remain small and understandable; prefer adding a targeted rule with a clear message over building a framework.
- It complements, but does not replace, `scripts/pre_compress_check.sh` and `scripts/check_session_integrity.sh`.
