#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/create_manga_export.sh <session_name> <type> <slug> [--one-pass-approved]

Types:
  model-sheet
  heroine-teaser
  scene-card
  one-page

Creates a manga export package scaffold under:
  exports/<session_name>/manga/<YYYYMMDD>/<HHMMSS>_<type>_<slug>/

Use --one-pass-approved only when the player explicitly asked to generate/output the image now.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || "$#" -lt 3 || "$#" -gt 4 ]]; then
  usage
  exit 0
fi

SESSION_NAME="$1"
EXPORT_TYPE="$2"
SLUG="$3"
MODE_FLAG="${4:-}"

GENERATION_MODE="consultation"
USER_APPROVAL="pending"
TASK_CONFIRMATION="yes"
JOB_STATUS="packaged"
DEFAULT_VISUAL_MODE="Japanese manga / anime-style illustration, not photorealistic"
DEFAULT_NEGATIVE_VISUALS="photorealistic, live-action, real photo, cinematic still, 3D render, uncanny realism, watermark, garbled text"

if [[ -n "${MODE_FLAG}" ]]; then
  case "${MODE_FLAG}" in
    --one-pass-approved|--auto-generate-approved)
      GENERATION_MODE="one-pass generation"
      USER_APPROVAL="granted by explicit generation request"
      TASK_CONFIRMATION="already granted by explicit generation request"
      JOB_STATUS="queued"
      ;;
    *)
      echo "invalid option: ${MODE_FLAG}" >&2
      usage
      exit 1
      ;;
  esac
fi

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

DATE_STAMP="$(date +"%Y%m%d")"
TIME_STAMP="$(date +"%H%M%S")"
TIMESTAMP="${DATE_STAMP}_${TIME_STAMP}"
PACKAGE_NAME="${TIME_STAMP}_${EXPORT_TYPE}_${SLUG}"
PACKAGE_DIR="${ROOT_DIR}/exports/${SESSION_NAME}/manga/${DATE_STAMP}/${PACKAGE_NAME}"

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
- package name: ${DATE_STAMP}/${PACKAGE_NAME}
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
- default visual mode: ${DEFAULT_VISUAL_MODE}
- visual style rule: use manga line art, illustrated faces, controlled screentone/shading, and readable comic composition unless the player explicitly requests live-action.
- must avoid visual style:
  - ${DEFAULT_NEGATIVE_VISUALS}

Generation status:
- current status: ${JOB_STATUS}
- player confirmation: ${USER_APPROVAL}
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
- global style notes: ${DEFAULT_VISUAL_MODE}. Use LIRIA style guidance without copying hidden notes into visible dialogue.
- global visual guardrails:
  - default to manga/comic illustration, not photorealistic output
  - no meta terms in dialogue or visible text
  - do not reveal unconfirmed secrets visually
  - keep adult or intimate content separated according to brief.md
- global negative prompt: ${DEFAULT_NEGATIVE_VISUALS}

## Panel 1

- panel intent: TODO
- composition: TODO
- characters in frame: TODO use character IDs from character_refs.md source of truth.
- expression / gesture: TODO
- background / prop: TODO
- dialogue text if any: TODO
- visual guardrails: TODO
- negative prompt: ${DEFAULT_NEGATIVE_VISUALS}
EOF

cat > "${PACKAGE_DIR}/lettering.md" <<EOF
# Lettering

> 正確な日本語は画像AIに直接任せず、ここを写植 / 後工程の正本にする。

- reading direction: Japanese right-to-left / top-to-bottom
- font mood: TODO handwritten / gothic / mincho / narration
- balloon style guide:
  - normal: TODO
  - whisper: TODO
  - inner thought: TODO
  - narration: TODO

## Panel 1

- text item:
  - speaker: TODO
  - exact text: TODO
  - placement hint: TODO
  - priority: must-have | optional | cut if crowded
  - notes: TODO

## Final Lettering Check

- no mojibake / garbled Japanese
- no meta terms in character dialogue
- no hidden proper nouns leaked
- no unreadable tiny text used for essential story information
- final output includes a lettered version, not only blank balloons
EOF

cat > "${PACKAGE_DIR}/image_gen_tasks.md" <<EOF
# Image Gen Tasks

This file is task planning. In consultation mode it does not authorize image generation.
In one-pass generation mode, user approval is already granted by the explicit request.

## Task 1: art-base

- task id: ${SLUG}-001
- dependency: none
- prompt source: panel_prompts.md#panel-1
- required Visual Character Sheet status: TODO prompt-ready before generation
- output kind: TODO model sheet / teaser image / scene card / one-page manga
- target file name: TODO ${SLUG}_art-base.png
- confirmation needed before generation: ${TASK_CONFIRMATION}
- visual mode: ${DEFAULT_VISUAL_MODE}
- negative visuals: ${DEFAULT_NEGATIVE_VISUALS}
- post-generation notes to record: generated asset references, seed, prompt version, continuity issues

## Task 2: lettering

- task id: ${SLUG}-lettering-001
- dependency: ${SLUG}-001
- prompt source: lettering.md
- required input: generated art-base image with blank balloons / caption areas
- output kind: lettered one-page manga
- target file name: TODO ${SLUG}_lettered.png
- confirmation needed before generation/editing: ${TASK_CONFIRMATION}
- post-generation notes to record: font/lettering method, text fit issues, corrections needed

Preflight:
- Confirm protagonist and heroine IDs from character_refs.md source-of-truth paths.
- Confirm generated asset references are supplemental, not identity source.
- Confirm adult content handling and spoiler boundaries.
- Confirm the player explicitly approved actual generation, or that this package was created with one-pass approval.
- Confirm final result is not blank-balloon-only; one-page manga needs lettering.
EOF

cat > "${PACKAGE_DIR}/job_status.md" <<EOF
# Job Status

- mode: ${GENERATION_MODE}
- user approval: ${USER_APPROVAL}
- story blocking: forbidden
- package status: packaged
- overall status: ${JOB_STATUS}
- art-base status: not started
- lettering status: not needed / not started
- output files:
  - TODO
- generated asset references:
  - TODO path / URL / seed / model / prompt version
- continuity issues:
  - TODO
- next user-facing update: short status only; do not paste command logs into GM narration

Notes:
- Keep long prompts and internal progress in this package.
- In one-pass generation mode, return to the story handoff immediately instead of waiting in GM narration.
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
- final generation status: ${JOB_STATUS}

Reminder:
- This package may guide later image generation, but no image has been generated by this scaffold.
EOF

echo "created manga export package: ${PACKAGE_DIR}"
