#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/create_manga_export.sh <session_name> <type> <slug>

Types:
  model-sheet
  heroine-teaser
  scene-card
  one-page

Creates a manga export package scaffold under:
  exports/<session_name>/manga/<timestamp>_<type>_<slug>/
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || "$#" -ne 3 ]]; then
  usage
  exit 0
fi

SESSION_NAME="$1"
EXPORT_TYPE="$2"
SLUG="$3"

if [[ ! "${SESSION_NAME}" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "invalid session name: ${SESSION_NAME}" >&2
  echo "use only letters, numbers, dot, underscore, and hyphen; do not include slashes" >&2
  exit 1
fi

case "${EXPORT_TYPE}" in
  model-sheet|heroine-teaser|scene-card|one-page)
    ;;
  *)
    echo "invalid manga export type: ${EXPORT_TYPE}" >&2
    echo "expected one of: model-sheet, heroine-teaser, scene-card, one-page" >&2
    exit 1
    ;;
esac

if [[ ! "${SLUG}" =~ ^[A-Za-z0-9][A-Za-z0-9_-]*$ ]]; then
  echo "invalid slug: ${SLUG}" >&2
  echo "use only letters, numbers, underscore, and hyphen; do not include slashes" >&2
  exit 1
fi

SAVE_DIR="${ROOT_DIR}/saves/${SESSION_NAME}"
if [[ ! -d "${SAVE_DIR}" ]]; then
  echo "warning: save directory not found; creating export scaffold only: ${SAVE_DIR}" >&2
fi

TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"
PACKAGE_NAME="${TIMESTAMP}_${EXPORT_TYPE}_${SLUG}"
PACKAGE_DIR="${ROOT_DIR}/exports/${SESSION_NAME}/manga/${PACKAGE_NAME}"

if [[ -e "${PACKAGE_DIR}" ]]; then
  echo "manga export package already exists: ${PACKAGE_DIR}" >&2
  exit 1
fi

mkdir -p "${PACKAGE_DIR}"

cat > "${PACKAGE_DIR}/source.md" <<EOF
# Source

- session name: ${SESSION_NAME}
- export type: ${EXPORT_TYPE}
- slug: ${SLUG}
- package name: ${PACKAGE_NAME}
- created at: ${TIMESTAMP}
- source type: TODO current scene / heroine debut / relationship beat / crisis hint / model reference
- source files read:
  - TODO saves/${SESSION_NAME}/current/player.md
  - TODO saves/${SESSION_NAME}/current/gm.md
  - TODO saves/${SESSION_NAME}/current/harem.md
  - TODO saves/${SESSION_NAME}/cast/heroine/[name].md
  - TODO saves/${SESSION_NAME}/indexes/[index].md
- scene summary: TODO summarize only the needed scene facts. Do not paste full play logs.
- known boundary: TODO what may be stated plainly
- suspected boundary: TODO what may be implied only
- unknown boundary: TODO what must not be revealed
- secrets not to confirm visually: TODO

Notes:
- This is a prompt package scaffold, not an image generation result.
- Do not use this file as a substitute for the session save source of truth.
EOF

cat > "${PACKAGE_DIR}/brief.md" <<EOF
# Brief

- export type: ${EXPORT_TYPE}
- target audience: TODO private / public teaser / recap / model reference
- tone: TODO
- must include:
  - TODO
- must avoid:
  - TODO
- adult content handling: keep adult or intimate material separated and controlled for the intended audience; do not delete Style Layer guidance.
- relationship stage constraints: TODO preserve the current relationship stage and avoid over-intimacy.
- spoiler policy: TODO

Generation status:
- image generation has not been run.
- player confirmation is required before any image gen skill or tool call.
EOF

cat > "${PACKAGE_DIR}/character_refs.md" <<EOF
# Character References

## Source Of Truth

- protagonist character ID source: saves/${SESSION_NAME}/current/player.md
- heroine character ID source: saves/${SESSION_NAME}/cast/heroine/[name].md
- protagonist Visual Character Sheet: TODO copy or summarize only the needed prompt anchor fields.
- heroine Visual Character Sheet: TODO copy or summarize only the needed prompt anchor fields.
- model sheet status: TODO none / text-only / prompt-ready / image-generated

## Character ID Rules

- Character IDs, relationships, secrets, and inner state come from current/player.md and cast/heroine/[name].md.
- Images, standees, model sheets, URLs, seeds, and files are generated asset references only.
- Do not decide character ID, relationship status, secrets, or inner state from an image alone.
- If an image conflicts with the cast file, treat the cast file as the source of truth and record the image as a continuity issue.

## Prompt Anchors

- protagonist image prompt anchor: TODO
- heroine image prompt anchor: TODO
- continuity locks: TODO
- negative prompt / avoid: TODO
- generated asset references:
  - TODO none yet / path / URL / seed / note
- current appearance deltas for this scene: TODO clothes, injury, fatigue, hairstyle, props.

NPC handling:
- Do not create Visual Character Sheets for mobs, named NPCs, cast NPCs, or important NPCs.
- If an NPC appears, keep them as scene appearance notes only.
EOF

cat > "${PACKAGE_DIR}/name.md" <<EOF
# Name

- internal package name: ${PACKAGE_NAME}
- display title: TODO
- export type: ${EXPORT_TYPE}
- slug: ${SLUG}
- spoiler-safe title: TODO
- public caption draft: TODO

Rules:
- Do not expose unconfirmed secrets or hidden proper nouns in public-facing names.
- Keep private/internal labels separate from display titles.
EOF

cat > "${PACKAGE_DIR}/panel_prompts.md" <<EOF
# Panel Prompts

- page or panel count: TODO
- global style notes: TODO use LIRIA style guidance without copying hidden notes into visible dialogue.
- global visual guardrails:
  - no meta terms in dialogue or visible text
  - do not reveal unconfirmed secrets visually
  - keep adult or intimate content separated according to brief.md
- global negative prompt: TODO

## Panel 1

- panel intent: TODO
- composition: TODO
- characters in frame: TODO use character IDs from character_refs.md source of truth.
- expression / gesture: TODO
- background / prop: TODO
- dialogue text if any: TODO
- visual guardrails: TODO
- negative prompt: TODO
EOF

cat > "${PACKAGE_DIR}/image_gen_tasks.md" <<EOF
# Image Gen Tasks

This file is task planning only. It does not authorize image generation.

## Task 1

- task id: ${SLUG}-001
- dependency: none
- prompt source: panel_prompts.md#panel-1
- required Visual Character Sheet status: TODO prompt-ready before generation
- output kind: TODO model sheet / teaser image / scene card / one-page manga
- target file name: TODO ${SLUG}_001.png
- confirmation needed before generation: yes
- post-generation notes to record: generated asset references, seed, prompt version, continuity issues

Preflight:
- Confirm protagonist and heroine IDs from character_refs.md source-of-truth paths.
- Confirm generated asset references are supplemental, not identity source.
- Confirm adult content handling and spoiler boundaries.
- Confirm the player explicitly approved actual generation.
EOF

cat > "${PACKAGE_DIR}/publish_notes.md" <<EOF
# Publish Notes

- visibility: TODO private / public teaser / recap / internal-only
- spoiler policy: TODO
- adult content separation: TODO keep private/adult material out of public teaser prompts unless explicitly approved.
- credit / internal-only note: TODO
- what not to publish:
  - TODO hidden proper nouns
  - TODO unresolved secrets
  - TODO raw play log excerpts
- final generation status: not generated

Reminder:
- This package may guide later image generation, but no image has been generated by this scaffold.
EOF

echo "created manga export package: ${PACKAGE_DIR}"
