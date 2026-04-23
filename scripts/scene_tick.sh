#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MODE="tick"

usage() {
  cat <<'USAGE'
Usage:
  bash scripts/scene_tick.sh <session_name>
  bash scripts/scene_tick.sh --reset <session_name> [save_label]

Increments or resets the 10-scene autosave counter in:
  saves/<session_name>/current/gm.md
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "${1:-}" == "--reset" ]]; then
  MODE="reset"
  shift
fi

SESSION_NAME="${1:-}"
if [[ -z "$SESSION_NAME" ]]; then
  echo "error: session_name is required" >&2
  usage >&2
  exit 2
fi

GM_FILE="${ROOT_DIR}/saves/${SESSION_NAME}/current/gm.md"
if [[ ! -f "$GM_FILE" ]]; then
  echo "error: gm file not found: ${GM_FILE}" >&2
  exit 1
fi

if [[ "$MODE" == "reset" ]]; then
  SAVE_LABEL="${2:-manual save}"
  COUNT="0" \
  HOLD="なし" \
  SAVE_LABEL="$SAVE_LABEL" \
  perl -0pi -e '
    s/(- 前回保存からのシーン数:\s*)\d+\/10/${1}$ENV{COUNT}\/10/;
    s/(- 最終保存:\s*).*/${1}$ENV{SAVE_LABEL}/;
    s/(- 次回自動保存:\s*).*/${1}通常シーン10回後/;
    s/(- 自動セーブ保留:\s*).*/${1}$ENV{HOLD}/;
  ' "$GM_FILE"

  echo "SESSION=${SESSION_NAME}"
  echo "SCENE_COUNTER=0/10"
  echo "AUTO_SAVE_REQUIRED=0"
  echo "ACTION=reset"
  exit 0
fi

CURRENT_COUNT="$(
  sed -nE 's/^- 前回保存からのシーン数:[[:space:]]*([0-9]+)\/10.*/\1/p' "$GM_FILE" | head -n 1
)"

if [[ -z "$CURRENT_COUNT" ]]; then
  echo "error: autosave counter not found in ${GM_FILE}" >&2
  exit 1
fi

NEXT_COUNT=$((CURRENT_COUNT + 1))
if (( NEXT_COUNT >= 10 )); then
  NEXT_COUNT=10
  HOLD="あり（10/10到達。次の「どうする？」前に自動セーブ）"
  AUTO_SAVE_REQUIRED=1
else
  HOLD="なし"
  AUTO_SAVE_REQUIRED=0
fi

COUNT="$NEXT_COUNT" \
HOLD="$HOLD" \
perl -0pi -e '
  s/(- 前回保存からのシーン数:\s*)\d+\/10/${1}$ENV{COUNT}\/10/;
  s/(- 自動セーブ保留:\s*).*/${1}$ENV{HOLD}/;
' "$GM_FILE"

echo "SESSION=${SESSION_NAME}"
echo "SCENE_COUNTER=${NEXT_COUNT}/10"
echo "AUTO_SAVE_REQUIRED=${AUTO_SAVE_REQUIRED}"
if (( AUTO_SAVE_REQUIRED == 1 )); then
  echo "ACTION=save_before_next_prompt"
else
  echo "ACTION=continue"
fi
