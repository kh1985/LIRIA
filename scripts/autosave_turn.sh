#!/usr/bin/env bash
# autosave_turn.sh — advance the scene counter and save a raw log at 10/10.
#
# Usage:
#   bash scripts/autosave_turn.sh <session_name> [--engine codex|claude|auto]
#
# This is intentionally a thin coordinator. The GM still owns the narrative
# state in current/*.md; this helper keeps the counter/raw-log path from
# splitting into multiple easy-to-forget commands.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/autosave_turn.sh <session_name> [--engine codex|claude|auto]

Advances current/gm.md autosave counter by one normal scene.
When the counter reaches 10/10, saves a raw log and resets the counter.
EOF
}

SESSION=""
ENGINE_OVERRIDE="${ENGINE:-auto}"

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    -h|--help|help)
      usage
      exit 0
      ;;
    --engine)
      shift
      if [[ "$#" -eq 0 ]]; then
        echo "--engine requires a value" >&2
        exit 1
      fi
      ENGINE_OVERRIDE="$1"
      ;;
    --engine=*)
      ENGINE_OVERRIDE="${1#*=}"
      ;;
    *)
      if [[ -z "${SESSION}" ]]; then
        SESSION="$1"
      else
        echo "unexpected argument: $1" >&2
        usage >&2
        exit 1
      fi
      ;;
  esac
  shift
done

if [[ -z "${SESSION}" ]]; then
  echo "session name is required" >&2
  usage >&2
  exit 1
fi

GM_FILE="${ROOT_DIR}/saves/${SESSION}/current/gm.md"
if [[ ! -f "${GM_FILE}" ]]; then
  echo "gm state not found: ${GM_FILE}" >&2
  exit 1
fi

case "${ENGINE_OVERRIDE}" in
  auto|codex|claude)
    ;;
  *)
    echo "unsupported engine: ${ENGINE_OVERRIDE}" >&2
    echo "use --engine auto, --engine codex, or --engine claude" >&2
    exit 1
    ;;
esac

tick_output="$(bash "${ROOT_DIR}/scripts/scene_tick.sh" "${SESSION}")"
printf '%s\n' "${tick_output}"

if [[ "${tick_output}" != *"AUTO_SAVE_REQUIRED=1"* ]]; then
  echo "AUTOSAVE_DONE=0"
  exit 0
fi

timestamp="$(date +%Y-%m-%d_%H:%M:%S)"
save_label="auto-rawlog-${timestamp}"

echo "NOTE: autosave threshold reached; saving raw log before next prompt."

if ENGINE="${ENGINE_OVERRIDE}" bash "${ROOT_DIR}/scripts/save_rawlog.sh" "${SESSION}"; then
  bash "${ROOT_DIR}/scripts/scene_tick.sh" --reset "${SESSION}" "${save_label}"
  echo "AUTOSAVE_DONE=1"
else
  echo "AUTOSAVE_DONE=0"
  echo "AUTOSAVE_ERROR=rawlog_failed"
  exit 1
fi
