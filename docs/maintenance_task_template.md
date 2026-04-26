# LIRIA Maintenance Task Template

Use this template for repo-local maintenance work that improves prompt/session hygiene without changing game runtime behavior.

## Task

- Goal:
- Files owned by this task:
- Files explicitly out of scope:
- Runtime impact expected: none / explain if any
- Reviewer:

## Guardrails

- Do not edit unrelated files or revert concurrent work.
- Do not add this maintenance document, `docs/liria_prompt_auditor.md`, or `scripts/liria_prompt_auditor.py` to game prompt assembly.
- Keep tools read-only unless the task explicitly says otherwise.
- Prefer small, inspectable heuristics over broad rewrites.
- Treat findings as review prompts, not automatic truth.

## Audit Checklist

- Prompt bloat: repeated policy blocks, oversized generated prompts, or maintenance text leaking into runtime prompts.
- Hard numbered choices: player-facing output should avoid fixed `1. 2. 3.` menus unless intentionally out-of-character tooling.
- Autosave contradictions: save timing, scene counts, `/compress`, raw logs, and current/session file responsibilities should not conflict.
- Hotset hygiene: `hotset.md` should be a compact resume cache, not a source of truth or long archive.
- Cast index hygiene: recurring/important NPCs should graduate from inline mentions to cast sheets and index rows.
- Event index hygiene: event entries should remain concise, dated/anchored where possible, and avoid duplicating full prose.

## Evidence

- Command run:
- Files inspected:
- Key findings:
- False positives or intentional exceptions:

## Outcome

- Changes made:
- Tests/checks run:
- Remaining risks:
- Follow-up task, if needed:
