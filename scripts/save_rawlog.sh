#!/usr/bin/env bash
# save_rawlog.sh — セッション終了時に Claude Code / Codex CLI の会話ログを生ログとして保存する
#
# 使い方:
#   bash scripts/save_rawlog.sh [session_name]
#
# 例:
#   bash scripts/save_rawlog.sh <session_name>
#   ENGINE=codex bash scripts/save_rawlog.sh <session_name>
#   ENGINE=claude bash scripts/save_rawlog.sh <session_name>
#
# 注意: Claude / Codex の内部ログ形式は変更される可能性がある。
#       見つからない場合は手動保存テンプレートを作成する。

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

resolve_session() {
  if [[ -n "${1:-}" ]]; then
    echo "$1"
    return
  fi

  local latest
  latest="$(find "${ROOT_DIR}/saves" -mindepth 1 -maxdepth 1 -type d -name 'session_*' 2>/dev/null | sort | tail -n 1)"
  if [[ -z "${latest}" ]]; then
    echo "session name is required; no saves/session_* directory exists" >&2
    exit 1
  fi

  basename "${latest}"
}

SESSION="$(resolve_session "${1:-}")"
SAVE_DIR="${ROOT_DIR}/saves/${SESSION}/archive/logs"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTFILE="${SAVE_DIR}/raw_${TIMESTAMP}.md"
ENGINE_FILTER="${ENGINE:-auto}"

mkdir -p "${SAVE_DIR}"

CLAUDE_HOME="${CLAUDE_HOME:-${HOME}/.claude}"
CODEX_HOME="${CODEX_HOME:-${HOME}/.codex}"

LATEST_FILE=""
LATEST_SOURCE=""

consider_file() {
  local file="$1"
  local source="$2"

  [[ -f "${file}" ]] || return 0

  if [[ -z "${LATEST_FILE}" || "${file}" -nt "${LATEST_FILE}" ]]; then
    LATEST_FILE="${file}"
    LATEST_SOURCE="${source}"
  fi
}

consider_dir() {
  local dir="$1"
  local source="$2"
  local file

  [[ -d "${dir}" ]] || return 0

  while IFS= read -r -d '' file; do
    consider_file "${file}" "${source}"
  done < <(find "${dir}" -type f \( -name '*.jsonl' -o -name '*.json' \) -print0 2>/dev/null || true)
}

search_claude_logs() {
  consider_dir "${CLAUDE_HOME}/projects" "claude projects"
  consider_dir "${CLAUDE_HOME}/sessions" "claude sessions"
}

search_codex_logs() {
  consider_dir "${CODEX_HOME}/sessions" "codex sessions"
}

search_history_fallbacks() {
  case "${ENGINE_FILTER}" in
    claude)
      consider_file "${CLAUDE_HOME}/history.jsonl" "claude history"
      ;;
    codex)
      consider_file "${CODEX_HOME}/history.jsonl" "codex history"
      ;;
    *)
      consider_file "${CLAUDE_HOME}/history.jsonl" "claude history"
      consider_file "${CODEX_HOME}/history.jsonl" "codex history"
      ;;
  esac
}

case "${ENGINE_FILTER}" in
  claude)
    search_claude_logs
    ;;
  codex)
    search_codex_logs
    ;;
  auto|"")
    search_claude_logs
    search_codex_logs
    ;;
  *)
    echo "⚠ unknown ENGINE=${ENGINE_FILTER}; searching both Claude and Codex logs"
    search_claude_logs
    search_codex_logs
    ;;
esac

if [[ -z "${LATEST_FILE}" ]]; then
  search_history_fallbacks
fi

if [[ -n "${LATEST_FILE}" ]]; then
  ext="${LATEST_FILE##*.}"
  case "${ext}" in
    json|jsonl)
      ;;
    *)
      ext="log"
      ;;
  esac

  OUTLOG="${OUTFILE%.md}.${ext}"
  cp "${LATEST_FILE}" "${OUTLOG}"
  echo "✓ 生ログを保存しました: ${OUTLOG}"
  echo "  ソース: ${LATEST_SOURCE}"
  echo "  ファイル: ${LATEST_FILE}"
else
  cat <<EOF

========================================
  生ログの手動保存
========================================

Claude / Codex のセッションログの自動取得に失敗しました。
以下の方法で手動保存してください:

1. 現在の会話内容をコピー
2. 以下のファイルに貼り付け:
   ${OUTFILE}

または、セッション中に以下をGMに依頼:
  「(gm 今日の会話の要約を archive/logs/raw_${TIMESTAMP}.md に書いて)」

========================================
EOF

  cat > "${OUTFILE}" <<EOF
# 生ログ: ${TIMESTAMP}
# セッション: ${SESSION}
# ステータス: 手動保存待ち
#
# このファイルに会話ログを貼り付けてください。
EOF
  echo "✓ テンプレートを作成しました: ${OUTFILE}"
fi

echo ""
echo "保存先ディレクトリ: ${SAVE_DIR}"
ls -la "${SAVE_DIR}" | tail -5
