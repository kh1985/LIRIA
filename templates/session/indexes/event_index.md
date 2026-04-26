# event index

## Latest Anchors

| ID | When | Summary | Tags | Source |
|---|---|---|---|---|
| current_resume | current | Live resume state and immediate scene pressure | resume, live | `current/gm.md` |
| active_case | current | Active case goal, handles, ignored consequences, and next visible change | case, live | `current/case.md` |
| first_turn_hotset | current | First-turn temperature, pressure, and minimum cast/design context | hotset, cache | `current/hotset.md` |

## Archive Router

| ID | When | Summary | Tags | Archive |
|---|---|---|---|---|
| example_event_id | chapter/day/scene | One-line reason to open this archived event | tag1, tag2 | `archive/events/example_event_id.md` |
| example_checkpoint_id | checkpoint | Sidecar payload or checkpoint bundle that is no longer needed in live context | checkpoint, sidecar | `archive/checkpoints/example_checkpoint_id.md` |

## Checkpoint Sidecars

| ID | Status | Summary | Path |
|---|---|---|---|
| current_checkpoint_stub | active | Put temporary checkpoint payloads here while they are still in play | `current/checkpoints/` |
| archived_checkpoint_stub | archived | Move resolved checkpoint payloads here and add a concrete row above | `archive/checkpoints/` |

## Archive Migration Priority

1. Route any scene that is too large for `current/gm.md` into `archive/events/`.
2. Route resolved chapter summaries into `archive/chapters/`.
3. Route bulky run logs or transcript-like material into `archive/logs/`.
4. Route checkpoint sidecars into `current/checkpoints/` first, then `archive/checkpoints/` once resolved.

## Operating Notes

- Add an index row whenever narrative content moves out of `current/`.
- Keep summaries short enough that resume can scan this file before opening archive payloads.
- Use stable IDs that include chapter/day/scene or checkpoint purpose.
- Prefer opening only the archive files selected by this router.
