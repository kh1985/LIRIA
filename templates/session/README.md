# session template

## Layout

- `current/` is the resume/save source of truth for live state.
- `cast/heroine/` and `cast/npc/` hold session-local live cast files.
- `design/` holds long-range design references and setup answers.
- `indexes/` routes readers to current/archive material before opening large files.
- `archive/` holds event, chapter, log, and checkpoint sidecars after they leave the hot path.

## Read Priority

1. `current/hotset.md`
2. `current/case.md`
3. Focused excerpts from `current/gm.md`, `current/player.md`, and `current/relationships.md`
4. `indexes/cast_index.md` to narrow cast reads
5. Relevant `cast/heroine/*.md` and `cast/npc/*.md`
6. `indexes/decision_index.md` for resolved decisions
7. `current/mechanics_card.md` only when ability, combat, tools, consent, or risk rules matter
8. `indexes/event_index.md` only when continuity or archived detail is needed
9. Relevant `design/*.md`
10. Only the files selected from `archive/*`

## Operating Notes

- Treat `current/` as the canonical live snapshot. Do not recreate legacy session-root mirrors for normal saves.
- Treat `hotset.md` as a first-turn resume cache, not a second `gm.md`.
- Route archived details through `indexes/event_index.md` before opening archive files.
- Put volatile or one-off checkpoint sidecars under `current/checkpoints/`; move durable resolved checkpoint notes to `archive/checkpoints/`.

## Legacy Mirror Policy

- Canonical files live under `current/*`, `cast/*`, `design/*`, `indexes/*`, and `archive/*`.
- Do not create session-root `player.md`, `gm.md`, `harem.md`, or similar mirrors.
- If an older backup contains legacy mirrors, treat them as read-only fallback input.
- Move any needed fallback information into the session-local canonical files before saving.
