#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCENARIOS_DIR="${ROOT_DIR}/scenarios"
ENGINE="${ENGINE:-auto}"
CLAUDE_BARE="${CLAUDE_BARE:-0}"
PROMPT_ONLY=0
CLEANUP_SESSIONS_DRY_RUN=0
CODEX_INSTRUCTIONS_FILE=""
CLAUDE_SYSTEM_PROMPT_FILE=""
GENERATED_PROMPT_FILES=()
RUNTIME_PACKET_TEXT=""
AUTOSAVE_WATCHER_PID=""
TRANSCRIPT_PATH=""

usage() {
  cat <<'EOF'
Usage:
  bash play.sh
  bash play.sh menu
  bash play.sh list
  bash play.sh list-sessions [scenario]
  bash play.sh cleanup-sessions [--dry-run]
  bash play.sh new [scenario] [session_name]
  bash play.sh resume [scenario] [session_name]
  bash play.sh <scenario> new [session_name]
  bash play.sh <scenario> resume [session_name]
  bash play.sh [--prompt-only] ...
  bash play.sh [--claude|--codex|--engine ENGINE] ...

Examples:
  bash play.sh
  bash play.sh menu
  bash play.sh list
  bash play.sh list-sessions
  bash play.sh cleanup-sessions --dry-run
  bash play.sh new
  bash play.sh new liria session_002
  bash play.sh resume
  bash play.sh resume liria session_002
  bash play.sh resume -codex
  bash play.sh --codex resume
  bash play.sh liria new
  bash play.sh liria new session_002
  bash play.sh liria resume session_002
  bash play.sh liria new session_002 --prompt-only
  bash play.sh new --prompt-only

Notes:
  - Running without arguments opens a Japanese start menu when stdin is a terminal.
  - `new` / `resume` without scenario use `liria`.
  - `new` without session_name creates the next session_NNN automatically.
  - Auto numbering starts at session_002 to avoid the legacy first slot.
  - `resume` without session_name selects the latest numbered session and prints it.
  - `cleanup-sessions --dry-run` lists removable local sessions without prompting.
  - This launcher supports Claude CLI and Codex CLI.
  - `ENGINE=auto` prefers Codex when available, then falls back to Claude.
  - Force an engine with `ENGINE=claude` or `ENGINE=codex`.
  - Claude bare mode is opt-in. Set `CLAUDE_BARE=1` to enable `--bare`.
  - `--prompt-only` creates the session and generated prompt files, then exits before launching Claude/Codex.
EOF
}

trim_spaces() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  echo "${value}"
}

menu_session_names() {
  local save_root="${ROOT_DIR}/saves"
  local dir

  [[ -d "${save_root}" ]] || return 0

  for dir in "${save_root}"/*; do
    [[ -d "${dir}" ]] || continue
    basename "${dir}"
  done | sort
}

menu_latest_session_name() {
  local latest=""
  while IFS= read -r latest; do
    :
  done < <(menu_session_names)

  [[ -n "${latest}" ]] || return 1
  echo "${latest}"
}

interactive_menu() {
  SCENARIO_ID="liria"
  MODE=""
  SESSION_NAME=""

  echo
  echo "LIRIA をどう始めますか？"
  echo "  1. 新規スタート"
  echo "  2. 続きから"
  echo "  3. セッション一覧"
  echo "  4. 不要なセッションを削除する"
  echo "  q. やめる"
  echo

  local answer
  while true; do
    printf "入力してください（新規 / 続きから / 一覧 / 削除）: "
    if ! IFS= read -r answer; then
      echo
      exit 0
    fi
    answer="$(trim_spaces "${answer}")"

    case "${answer}" in
      1|n|new|New|NEW|新規|新規スタート|はじめる|始める|スタート)
        MODE="new"
        printf "セッション名を入れてください（空Enterで自動採番）: "
        IFS= read -r SESSION_NAME || SESSION_NAME=""
        SESSION_NAME="$(trim_spaces "${SESSION_NAME}")"
        return
        ;;
      2|r|resume|Resume|RESUME|続き|続きから|再開)
        MODE="resume"
        choose_resume_session_interactive
        return
        ;;
      3|l|list|List|LIST|一覧|セッション一覧)
        echo
        echo "保存済みセッション:"
        if ! menu_session_names; then
          echo "まだありません"
        fi
        echo
        ;;
      4|cleanup|cleanup-sessions|削除|セッション削除|不要なセッションを削除する)
        MODE="cleanup-sessions"
        return
        ;;
      q|Q|quit|exit|やめる|終了)
        exit 0
        ;;
      "")
        ;;
      *)
        echo "分からなかったので、'新規' か '続きから' で答えてください。"
        ;;
    esac
  done
}

choose_resume_session_interactive() {
  local -a sessions=()
  local session
  while IFS= read -r session; do
    [[ -n "${session}" ]] || continue
    sessions+=("${session}")
  done < <(menu_session_names)

  if [[ "${#sessions[@]}" -eq 0 ]]; then
    echo "まだ保存済みセッションがありません。新規スタートにします。"
    MODE="new"
    printf "セッション名を入れてください（空Enterで自動採番）: "
    IFS= read -r SESSION_NAME || SESSION_NAME=""
    SESSION_NAME="$(trim_spaces "${SESSION_NAME}")"
    return
  fi

  local latest
  latest="$(menu_latest_session_name || true)"

  echo
  echo "どの続きから始めますか？"
  echo "空Enterなら最新っぽいものを使います: ${latest}"
  echo

  local start=0
  if (( ${#sessions[@]} > 20 )); then
    start=$((${#sessions[@]} - 20))
    echo "最近の候補（多いので末尾20件だけ表示）:"
  else
    echo "候補:"
  fi

  local i display_index
  for (( i=start; i<${#sessions[@]}; i++ )); do
    display_index=$((i - start + 1))
    printf "  %2d. %s\n" "${display_index}" "${sessions[i]}"
  done
  echo

  local pick
  while true; do
    printf "番号かセッション名を入力: "
    if ! IFS= read -r pick; then
      echo
      exit 0
    fi
    pick="$(trim_spaces "${pick}")"

    if [[ -z "${pick}" ]]; then
      SESSION_NAME="${latest}"
      return
    fi

    if [[ "${pick}" =~ ^[0-9]+$ ]]; then
      local selected_index=$((start + pick - 1))
      if (( pick >= 1 && selected_index < ${#sessions[@]} )); then
        SESSION_NAME="${sessions[selected_index]}"
        return
      fi
      echo "その番号は候補にありません。"
      continue
    fi

    SESSION_NAME="${pick}"
    return
  done
}

list_scenarios() {
  local found=0
  local dir
  for dir in "${SCENARIOS_DIR}"/*; do
    [[ -d "${dir}" ]] || continue
    [[ -f "${dir}/config.sh" ]] || continue
    found=1
    local scenario_id
    scenario_id="$(basename "${dir}")"
    echo "${scenario_id}"
  done

  if [[ "${found}" -eq 0 ]]; then
    echo "no scenarios found"
    exit 1
  fi
}

is_existing_scenario() {
  local scenario_id="$1"
  [[ -f "${SCENARIOS_DIR}/${scenario_id}/config.sh" ]]
}

validate_mode() {
  case "${MODE}" in
    new|resume|list|list-sessions|cleanup-sessions)
      ;;
    *)
      echo "unsupported mode: ${MODE}"
      usage
      exit 1
      ;;
  esac
}

resolve_action_first_args() {
  local action="$1"
  local second="${2:-}"
  local third="${3:-}"

  MODE="${action}"

  if [[ -n "${third}" ]]; then
    SCENARIO_ID="${second:-liria}"
    SESSION_NAME="${third}"
    return
  fi

  if [[ -z "${second}" ]]; then
    SCENARIO_ID="liria"
    SESSION_NAME=""
    return
  fi

  if is_existing_scenario "${second}"; then
    SCENARIO_ID="${second}"
    SESSION_NAME=""
    return
  fi

  SCENARIO_ID="liria"
  SESSION_NAME="${second}"
}

resolve_args() {
  local requested_engine=""
  local -a positional=()

  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      -h|--help|help)
        usage
        exit 0
        ;;
      -claude|--claude)
        requested_engine="claude"
        ;;
      -codex|--codex)
        requested_engine="codex"
        ;;
      --engine)
        shift
        if [[ "$#" -eq 0 ]]; then
          echo "--engine requires a value"
          exit 1
        fi
        requested_engine="$1"
        ;;
      --engine=*)
        requested_engine="${1#*=}"
        ;;
      --prompt-only)
        PROMPT_ONLY=1
        ;;
      --dry-run)
        CLEANUP_SESSIONS_DRY_RUN=1
        ;;
      --)
        shift
        while [[ "$#" -gt 0 ]]; do
          positional+=("$1")
          shift
        done
        break
        ;;
      *)
        positional+=("$1")
        ;;
    esac
    shift
  done

  if [[ -n "${requested_engine}" ]]; then
    ENGINE="${requested_engine}"
  fi

  local arg1="${positional[0]:-}"
  local arg2="${positional[1]:-}"
  local arg3="${positional[2]:-}"

  SCENARIO_ID=""
  MODE=""
  SESSION_NAME=""

  case "${arg1}" in
    "")
      if [[ -t 0 ]]; then
        interactive_menu
      else
        usage
        exit 0
      fi
      ;;
    menu|start|スタート|起動)
      interactive_menu
      ;;
    list)
      MODE="list"
      SCENARIO_ID=""
      SESSION_NAME=""
      ;;
    list-sessions)
      MODE="list-sessions"
      SCENARIO_ID="${arg2:-liria}"
      SESSION_NAME=""
      ;;
    cleanup-sessions|cleanup)
      MODE="cleanup-sessions"
      SCENARIO_ID=""
      SESSION_NAME=""
      ;;
    new|resume|新規|新規スタート|はじめる|始める|続き|続きから|再開)
      case "${arg1}" in
        新規|新規スタート|はじめる|始める)
          arg1="new"
          ;;
        続き|続きから|再開)
          arg1="resume"
          ;;
      esac
      resolve_action_first_args "${arg1}" "${arg2}" "${arg3}"
      ;;
    *)
      SCENARIO_ID="${arg1}"
      MODE="${arg2:-resume}"
      if [[ "${MODE}" == "list-sessions" ]]; then
        SESSION_NAME=""
      else
        SESSION_NAME="${arg3:-}"
      fi
      ;;
  esac

  validate_mode
}

load_scenario() {
  local config_path="${SCENARIOS_DIR}/${SCENARIO_ID}/config.sh"
  if [[ ! -f "${config_path}" ]]; then
    echo "scenario not found: ${SCENARIO_ID}"
    echo
    echo "available scenarios:"
    list_scenarios
    exit 1
  fi

  # shellcheck source=/dev/null
  source "${config_path}"

  if [[ "${SCENARIO_ROOT}" = /* ]]; then
    SCENARIO_WORKDIR="${SCENARIO_ROOT}"
  else
    SCENARIO_WORKDIR="${ROOT_DIR}/${SCENARIO_ROOT}"
  fi
  SYSTEM_PROMPT_PATHS=()

  local -a selected_prompt_files=()
  if [[ "${MODE}" == "new" ]] && declare -p NEW_SYSTEM_PROMPT_FILES >/dev/null 2>&1; then
    selected_prompt_files=("${NEW_SYSTEM_PROMPT_FILES[@]}")
  elif [[ "${MODE}" == "resume" ]] && declare -p RESUME_SYSTEM_PROMPT_FILES >/dev/null 2>&1; then
    selected_prompt_files=("${RESUME_SYSTEM_PROMPT_FILES[@]}")
  elif declare -p SYSTEM_PROMPT_FILES >/dev/null 2>&1; then
    selected_prompt_files=("${SYSTEM_PROMPT_FILES[@]}")
  else
    local prompt_path="${SCENARIO_WORKDIR}/${SYSTEM_PROMPT_FILE}"
    if [[ ! -f "${prompt_path}" ]]; then
      echo "system prompt file not found: ${prompt_path}"
      exit 1
    fi
    SYSTEM_PROMPT_PATHS+=("${prompt_path}")
    return
  fi

  local prompt_rel
  for prompt_rel in "${selected_prompt_files[@]}"; do
    local prompt_path="${SCENARIO_WORKDIR}/${prompt_rel}"
    if [[ ! -f "${prompt_path}" ]]; then
      echo "system prompt file not found: ${prompt_path}"
      exit 1
    fi
    SYSTEM_PROMPT_PATHS+=("${prompt_path}")
  done
}

list_sessions() {
  local save_root="${SCENARIO_WORKDIR}/saves"
  local -a sessions=()
  local dir

  if [[ -d "${save_root}" ]]; then
    for dir in "${save_root}"/*; do
      [[ -d "${dir}" ]] || continue
      sessions+=("$(basename "${dir}")")
    done
  fi

  if [[ "${#sessions[@]}" -eq 0 ]]; then
    echo "no sessions found for scenario: ${SCENARIO_ID}"
    return 0
  fi

  printf "%s\n" "${sessions[@]}" | sort
}

CLEANUP_CANDIDATE_NAMES=()
CLEANUP_PROTECTED_NAMES=()
CLEANUP_PROTECTED_REASONS=()
CLEANUP_UNKNOWN_NAMES=()
CLEANUP_UNKNOWN_REASONS=()
CLEANUP_BLOCKED_NAMES=()
CLEANUP_BLOCKED_REASONS=()
CLEANUP_SELECTION=()

cleanup_is_protected_session() {
  case "$1" in
    kaneko1|kaneko2|kaneko3)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

cleanup_is_candidate_name() {
  case "$1" in
    session_*|skill_probe)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

cleanup_name_is_unsafe() {
  local name="$1"

  [[ -z "${name}" || "${name}" == *"/"* || "${name}" == *".."* ]]
}

cleanup_tracked_files_for() {
  local rel_path="$1"

  git -C "${ROOT_DIR}" ls-files -- "${rel_path}"
}

cleanup_collect_sessions() {
  CLEANUP_CANDIDATE_NAMES=()
  CLEANUP_PROTECTED_NAMES=()
  CLEANUP_PROTECTED_REASONS=()
  CLEANUP_UNKNOWN_NAMES=()
  CLEANUP_UNKNOWN_REASONS=()
  CLEANUP_BLOCKED_NAMES=()
  CLEANUP_BLOCKED_REASONS=()

  local save_root="${ROOT_DIR}/saves"
  local dir name rel_path tracked_files

  [[ -d "${save_root}" ]] || return 0

  for dir in "${save_root}"/*; do
    [[ -d "${dir}" ]] || continue
    name="$(basename "${dir}")"
    rel_path="saves/${name}"

    if cleanup_name_is_unsafe "${name}"; then
      CLEANUP_BLOCKED_NAMES+=("${name:-<empty>}")
      CLEANUP_BLOCKED_REASONS+=("unsafe name")
      continue
    fi

    if cleanup_is_protected_session "${name}"; then
      CLEANUP_PROTECTED_NAMES+=("${name}")
      CLEANUP_PROTECTED_REASONS+=("protected")
      continue
    fi

    tracked_files="$(cleanup_tracked_files_for "${rel_path}")"
    if [[ -n "${tracked_files}" ]]; then
      CLEANUP_BLOCKED_NAMES+=("${name}")
      CLEANUP_BLOCKED_REASONS+=("contains tracked file")
      continue
    fi

    if [[ ! -f "${dir}/session.json" ]]; then
      CLEANUP_UNKNOWN_NAMES+=("${name}")
      CLEANUP_UNKNOWN_REASONS+=("missing session.json")
      continue
    fi

    if ! cleanup_is_candidate_name "${name}"; then
      CLEANUP_UNKNOWN_NAMES+=("${name}")
      CLEANUP_UNKNOWN_REASONS+=("not a cleanup candidate")
      continue
    fi

    CLEANUP_CANDIDATE_NAMES+=("${name}")
  done
}

cleanup_print_category() {
  local header="$1"
  local count="$2"
  echo "${header}"
  if [[ "${count}" -eq 0 ]]; then
    echo "  (なし)"
    echo
    return
  fi
}

cleanup_print_protected_sessions() {
  cleanup_print_category "保護中:" "${#CLEANUP_PROTECTED_NAMES[@]}"
  [[ "${#CLEANUP_PROTECTED_NAMES[@]}" -eq 0 ]] && return
  local i
  for (( i=0; i<${#CLEANUP_PROTECTED_NAMES[@]}; i++ )); do
    echo "  - saves/${CLEANUP_PROTECTED_NAMES[i]}  reason: ${CLEANUP_PROTECTED_REASONS[i]}"
  done
  echo
}

cleanup_print_unknown_sessions() {
  cleanup_print_category "要確認:" "${#CLEANUP_UNKNOWN_NAMES[@]}"
  [[ "${#CLEANUP_UNKNOWN_NAMES[@]}" -eq 0 ]] && return
  local i
  for (( i=0; i<${#CLEANUP_UNKNOWN_NAMES[@]}; i++ )); do
    echo "  - saves/${CLEANUP_UNKNOWN_NAMES[i]}  reason: ${CLEANUP_UNKNOWN_REASONS[i]}"
  done
  echo
}

cleanup_print_blocked_sessions() {
  cleanup_print_category "削除不可:" "${#CLEANUP_BLOCKED_NAMES[@]}"
  [[ "${#CLEANUP_BLOCKED_NAMES[@]}" -eq 0 ]] && return
  local i
  for (( i=0; i<${#CLEANUP_BLOCKED_NAMES[@]}; i++ )); do
    echo "  - saves/${CLEANUP_BLOCKED_NAMES[i]}  reason: ${CLEANUP_BLOCKED_REASONS[i]}"
  done
  echo
}

cleanup_print_sessions() {
  echo "削除候補:"
  if [[ "${#CLEANUP_CANDIDATE_NAMES[@]}" -eq 0 ]]; then
    echo "  (なし)"
  else
    local i
    for (( i=0; i<${#CLEANUP_CANDIDATE_NAMES[@]}; i++ )); do
      printf "  %d. saves/%s\n" "$((i + 1))" "${CLEANUP_CANDIDATE_NAMES[i]}"
    done
  fi
  echo

  cleanup_print_protected_sessions
  cleanup_print_unknown_sessions
  cleanup_print_blocked_sessions
}

cleanup_add_selected_index() {
  local selected="$1"
  local existing

  if [[ "${#CLEANUP_SELECTION[@]}" -gt 0 ]]; then
    for existing in "${CLEANUP_SELECTION[@]}"; do
      [[ "${existing}" == "${selected}" ]] && return
    done
  fi

  CLEANUP_SELECTION+=("${selected}")
}

cleanup_parse_selection() {
  local raw="$1"
  local max="$2"
  local compact token start end start_num end_num token_num current
  local -a tokens=()

  CLEANUP_SELECTION=()
  compact="${raw//[[:space:]]/}"

  if [[ -z "${compact}" ]]; then
    echo "番号、範囲、all、q のいずれかを入力してください。"
    return 1
  fi

  case "${compact}" in
    q|Q|quit|exit|やめる|キャンセル)
      return 2
      ;;
    all|ALL|All)
      for (( current=1; current<=max; current++ )); do
        cleanup_add_selected_index "${current}"
      done
      return 0
      ;;
  esac

  IFS=',' read -r -a tokens <<< "${compact}"
  for token in "${tokens[@]}"; do
    if [[ "${token}" =~ ^([0-9]+)-([0-9]+)$ ]]; then
      start="${BASH_REMATCH[1]}"
      end="${BASH_REMATCH[2]}"
      start_num=$((10#${start}))
      end_num=$((10#${end}))
      if (( start_num < 1 || end_num < start_num || end_num > max )); then
        echo "範囲が候補外です: ${token}"
        return 1
      fi
      for (( current=start_num; current<=end_num; current++ )); do
        cleanup_add_selected_index "${current}"
      done
    elif [[ "${token}" =~ ^[0-9]+$ ]]; then
      token_num=$((10#${token}))
      if (( token_num < 1 || token_num > max )); then
        echo "番号が候補外です: ${token}"
        return 1
      fi
      cleanup_add_selected_index "${token_num}"
    else
      echo "入力を解釈できません: ${token}"
      return 1
    fi
  done

  [[ "${#CLEANUP_SELECTION[@]}" -gt 0 ]]
}

cleanup_delete_block_reason() {
  local name="$1"
  local rel_path path tracked_files

  if cleanup_name_is_unsafe "${name}"; then
    echo "unsafe name"
    return 0
  fi

  if cleanup_is_protected_session "${name}"; then
    echo "protected"
    return 0
  fi

  rel_path="saves/${name}"
  path="${ROOT_DIR}/${rel_path}"

  if [[ "${rel_path}" == "saves/.gitkeep" ]]; then
    echo "protected"
    return 0
  fi

  if [[ ! -d "${path}" ]]; then
    echo "not a directory"
    return 0
  fi

  case "${path}" in
    "${ROOT_DIR}/saves/"*)
      ;;
    *)
      echo "outside saves"
      return 0
      ;;
  esac

  tracked_files="$(cleanup_tracked_files_for "${rel_path}")"
  if [[ -n "${tracked_files}" ]]; then
    echo "contains tracked file"
    return 0
  fi

  if [[ ! -f "${path}/session.json" ]]; then
    echo "missing session.json"
    return 0
  fi

  if ! cleanup_is_candidate_name "${name}"; then
    echo "not a cleanup candidate"
    return 0
  fi

  echo ""
}

cleanup_print_git_status() {
  local status

  status="$(git -C "${ROOT_DIR}" status --short)"
  echo "git status --short:"
  if [[ -z "${status}" ]]; then
    echo "(no tracked changes)"
  else
    echo "${status}"
  fi
}

cleanup_sessions() {
  local dry_run="$1"

  cleanup_collect_sessions
  cleanup_print_sessions

  if [[ "${dry_run}" == "1" ]]; then
    echo "--dry-run: 削除は行いません。"
    return 0
  fi

  if [[ "${#CLEANUP_CANDIDATE_NAMES[@]}" -eq 0 ]]; then
    echo "削除候補がありません。"
    return 0
  fi

  local answer parse_status
  while true; do
    echo "削除する番号を入力してください（例: 1 / 1,3,5 / 2-4 / all / q）:"
    printf "> "
    if ! IFS= read -r answer; then
      echo
      echo "キャンセルしました。"
      return 0
    fi

    set +e
    cleanup_parse_selection "${answer}" "${#CLEANUP_CANDIDATE_NAMES[@]}"
    parse_status="$?"
    set -e

    if [[ "${parse_status}" == "0" ]]; then
      break
    fi
    if [[ "${parse_status}" == "2" ]]; then
      echo "キャンセルしました。"
      return 0
    fi
  done

  local index name
  echo
  echo "以下のセッションを削除します:"
  for index in "${CLEANUP_SELECTION[@]}"; do
    name="${CLEANUP_CANDIDATE_NAMES[$((index - 1))]}"
    echo "- saves/${name}"
  done
  echo
  echo "本当に削除しますか？"
  printf "削除する場合は yes と入力してください: "

  if ! IFS= read -r answer; then
    echo
    echo "キャンセルしました。"
    return 0
  fi

  if [[ "${answer}" != "yes" ]]; then
    echo "キャンセルしました。"
    return 0
  fi

  local -a deleted=()
  local -a skipped=()
  local -a skipped_reasons=()
  local reason rel_path path

  for index in "${CLEANUP_SELECTION[@]}"; do
    name="${CLEANUP_CANDIDATE_NAMES[$((index - 1))]}"
    reason="$(cleanup_delete_block_reason "${name}")"
    if [[ -n "${reason}" ]]; then
      skipped+=("saves/${name}")
      skipped_reasons+=("${reason}")
      continue
    fi

    rel_path="saves/${name}"
    path="${ROOT_DIR}/${rel_path}"
    rm -rf -- "${path}"
    deleted+=("${rel_path}")
  done

  echo
  echo "削除済み:"
  if [[ "${#deleted[@]}" -eq 0 ]]; then
    echo "- (なし)"
  else
    for rel_path in "${deleted[@]}"; do
      echo "- ${rel_path}"
    done
  fi

  echo
  echo "スキップ:"
  if [[ "${#skipped[@]}" -eq 0 ]]; then
    echo "- (なし)"
  else
    local i
    for (( i=0; i<${#skipped[@]}; i++ )); do
      echo "- ${skipped[i]} reason: ${skipped_reasons[i]}"
    done
  fi

  echo
  cleanup_print_git_status
}

latest_session_name() {
  local save_root="${SCENARIO_WORKDIR}/saves"
  local latest=""
  local latest_num=-1
  local -a fallback=()
  local dir name raw_num num

  [[ -d "${save_root}" ]] || return 1

  for dir in "${save_root}"/*; do
    [[ -d "${dir}" ]] || continue
    name="$(basename "${dir}")"
    fallback+=("${name}")
    if [[ "${name}" =~ ^session_([0-9]+)$ ]]; then
      raw_num="${BASH_REMATCH[1]}"
      num=$((10#${raw_num}))
      if (( num > latest_num )); then
        latest_num="${num}"
        latest="${name}"
      fi
    fi
  done

  if [[ -n "${latest}" ]]; then
    echo "${latest}"
    return 0
  fi

  if [[ "${#fallback[@]}" -gt 0 ]]; then
    printf "%s\n" "${fallback[@]}" | sort | tail -n 1
    return 0
  fi

  return 1
}

next_session_name() {
  local save_root="${SCENARIO_WORKDIR}/saves"
  # The first numbered slot is legacy; automatic new sessions start at session_002
  # even when saves/ is empty, while existing numbered sessions still use max+1.
  local max_num=1
  local dir name raw_num num

  if [[ -d "${save_root}" ]]; then
    for dir in "${save_root}"/session_*; do
      [[ -d "${dir}" ]] || continue
      name="$(basename "${dir}")"
      if [[ "${name}" =~ ^session_([0-9]+)$ ]]; then
        raw_num="${BASH_REMATCH[1]}"
        num=$((10#${raw_num}))
        if (( num > max_num )); then
          max_num="${num}"
        fi
      fi
    done
  fi

  printf "session_%03d\n" "$((max_num + 1))"
}

validate_session_name() {
  if [[ ! "${SESSION_NAME}" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
    echo "invalid session name: ${SESSION_NAME}"
    echo "use only letters, numbers, dot, underscore, and hyphen; do not include slashes"
    exit 1
  fi
}

create_new_session() {
  if [[ -z "${SESSION_NAME}" ]]; then
    SESSION_NAME="$(next_session_name)"
    echo "auto-generated session: ${SESSION_NAME}"
  fi

  validate_session_name

  if [[ -e "${SCENARIO_WORKDIR}/saves/${SESSION_NAME}" ]]; then
    echo "session already exists: ${SCENARIO_WORKDIR}/saves/${SESSION_NAME}"
    exit 1
  fi

  bash "${ROOT_DIR}/scripts/create_session.sh" "${SCENARIO_ID}" "${SESSION_NAME}" "${SCENARIO_WORKDIR}"
}

resolve_resume_session() {
  if [[ -z "${SESSION_NAME}" ]]; then
    if ! SESSION_NAME="$(latest_session_name)"; then
      echo "no sessions found for scenario: ${SCENARIO_ID}"
      echo "start one with: bash play.sh new ${SCENARIO_ID}"
      exit 1
    fi
    echo "no session specified; using latest session: ${SESSION_NAME}"
  fi

  validate_session_name

  if [[ ! -d "${SCENARIO_WORKDIR}/saves/${SESSION_NAME}" ]]; then
    echo "save not found: ${SCENARIO_WORKDIR}/saves/${SESSION_NAME}"
    exit 1
  fi
}

build_system_prompt() {
  local prompt_path
  SYSTEM_PROMPT=""

  for prompt_path in "${SYSTEM_PROMPT_PATHS[@]}"; do
    if [[ -n "${SYSTEM_PROMPT}" ]]; then
      SYSTEM_PROMPT+=$'\n\n'
    fi
    SYSTEM_PROMPT+="$(cat "${prompt_path}")"
  done
}

append_runtime_packet_to_user_prompt() {
  if [[ "${MODE}" != "resume" ]]; then
    return
  fi
  if [[ "${LIRIA_RUNTIME_PACKET_ENABLED:-0}" != "1" ]]; then
    return
  fi

  local builder="${SCENARIO_WORKDIR}/scripts/build_runtime_packet.py"
  local session_dir="${SCENARIO_WORKDIR}/saves/${SESSION_NAME}"

  if [[ ! -f "${builder}" ]]; then
    echo "runtime packet builder not found: ${builder}"
    exit 1
  fi

  if ! RUNTIME_PACKET_TEXT="$(python "${builder}" --session "${session_dir}")"; then
    echo "failed to build runtime packet for ${session_dir}"
    exit 1
  fi

  USER_PROMPT+=$'\n\n'
  USER_PROMPT+="${RUNTIME_PACKET_TEXT}"
}

start_autosave_watcher() {
  if [[ "${MODE}" != "new" && "${MODE}" != "resume" ]]; then
    return
  fi
  if [[ "${LIRIA_AUTOSAVE_WATCH_ENABLED:-0}" != "1" ]]; then
    return
  fi
  if [[ -z "${SESSION_NAME}" || -z "${ENGINE_COMMAND:-}" ]]; then
    return
  fi

  local watcher="${SCENARIO_WORKDIR}/scripts/watch_autosave_history.py"
  if [[ ! -f "${watcher}" ]]; then
    return
  fi

  python "${watcher}" \
    --session "${SESSION_NAME}" \
    --engine "${ENGINE_COMMAND}" \
    --parent-pid "$$" \
    >/dev/null 2>&1 &
  AUTOSAVE_WATCHER_PID="$!"
}

transcript_path_for_launch() {
  if [[ "${MODE}" != "new" && "${MODE}" != "resume" ]]; then
    return
  fi
  if [[ "${LIRIA_TRANSCRIPT_ENABLED:-0}" != "1" ]]; then
    return
  fi
  if [[ -z "${SESSION_NAME}" ]]; then
    return
  fi
  if ! command -v script >/dev/null 2>&1; then
    return
  fi

  local logs_dir="${SCENARIO_WORKDIR}/saves/${SESSION_NAME}/archive/logs"
  local timestamp
  timestamp="$(date +%Y%m%d_%H%M%S)"
  mkdir -p "${logs_dir}"
  TRANSCRIPT_PATH="${logs_dir}/live_${timestamp}_${ENGINE_COMMAND}.log"
}

write_codex_instructions_file() {
  local codex_dir="${SCENARIO_WORKDIR}/.codex/generated"
  CODEX_INSTRUCTIONS_FILE="${codex_dir}/${SCENARIO_ID}-${MODE}.instructions.md"

  mkdir -p "${codex_dir}"
  cat > "${CODEX_INSTRUCTIONS_FILE}" <<EOF
# Generated by play.sh
# Do not edit by hand.

${SYSTEM_PROMPT}
EOF
}

write_claude_system_prompt_file() {
  local claude_dir="${SCENARIO_WORKDIR}/.claude/generated"
  CLAUDE_SYSTEM_PROMPT_FILE="${claude_dir}/${SCENARIO_ID}-${MODE}.system-prompt.md"

  mkdir -p "${claude_dir}"
  cat > "${CLAUDE_SYSTEM_PROMPT_FILE}" <<EOF
# Generated by play.sh
# Do not edit by hand.

${SYSTEM_PROMPT}
EOF
}

write_generated_prompt_artifacts() {
  GENERATED_PROMPT_FILES=()
  write_codex_instructions_file
  GENERATED_PROMPT_FILES+=("${CODEX_INSTRUCTIONS_FILE}")
  write_claude_system_prompt_file
  GENERATED_PROMPT_FILES+=("${CLAUDE_SYSTEM_PROMPT_FILE}")
}

display_path() {
  local path="$1"

  if [[ "${path}" == "${SCENARIO_WORKDIR}/"* ]]; then
    echo "${path#${SCENARIO_WORKDIR}/}"
    return
  fi

  if [[ "${path}" == "${ROOT_DIR}/"* ]]; then
    echo "${path#${ROOT_DIR}/}"
    return
  fi

  echo "${path}"
}

print_prompt_only_summary() {
  local path

  echo "prompt-only: yes"
  echo "scenario: ${SCENARIO_ID}"
  echo "mode: ${MODE}"
  echo "session: ${SESSION_NAME}"
  if [[ "${LIRIA_RUNTIME_PACKET_ENABLED:-0}" == "1" ]]; then
    echo "runtime packet: enabled"
  else
    echo "runtime packet: disabled"
  fi
  echo "generated prompt/instructions files:"
  for path in "${GENERATED_PROMPT_FILES[@]}"; do
    echo "- $(display_path "${path}")"
  done
  echo "loaded prompt files:"
  for path in "${SYSTEM_PROMPT_PATHS[@]}"; do
    echo "- $(display_path "${path}")"
  done
}

resolve_engine_command() {
  case "${ENGINE}" in
    auto)
      if command -v codex >/dev/null 2>&1; then
        ENGINE_COMMAND="codex"
      elif command -v claude >/dev/null 2>&1; then
        ENGINE_COMMAND="claude"
      else
        echo "neither claude nor codex command was found"
        exit 1
      fi
      ;;
    claude|codex)
      if ! command -v "${ENGINE}" >/dev/null 2>&1; then
        echo "${ENGINE} command not found"
        exit 1
      fi
      ENGINE_COMMAND="${ENGINE}"
      ;;
    *)
      echo "unsupported ENGINE=${ENGINE}"
      echo "use ENGINE=auto, ENGINE=claude, or ENGINE=codex"
      exit 1
      ;;
  esac
}

launch_claude() {
  local -a claude_cmd=(claude)
  if [[ "${CLAUDE_BARE}" == "1" ]]; then
    claude_cmd+=(--bare)
  fi
  claude_cmd+=(--append-system-prompt "${SYSTEM_PROMPT}" "${USER_PROMPT}")

  transcript_path_for_launch
  if [[ -n "${TRANSCRIPT_PATH}" ]]; then
    exec script -q "${TRANSCRIPT_PATH}" "${claude_cmd[@]}"
  fi

  exec "${claude_cmd[@]}"
}

launch_codex() {
  local -a codex_cmd=(codex)

  write_codex_instructions_file
  codex_cmd+=(-c "model_instructions_file=\"${CODEX_INSTRUCTIONS_FILE}\"" "${USER_PROMPT}")

  transcript_path_for_launch
  if [[ -n "${TRANSCRIPT_PATH}" ]]; then
    exec script -q "${TRANSCRIPT_PATH}" "${codex_cmd[@]}"
  fi

  exec "${codex_cmd[@]}"
}

main() {
  resolve_args "$@"

  if [[ "${MODE}" == "list" ]]; then
    list_scenarios
    exit 0
  fi

  if [[ "${MODE}" == "cleanup-sessions" ]]; then
    cleanup_sessions "${CLEANUP_SESSIONS_DRY_RUN}"
    exit 0
  fi

  load_scenario

  if [[ "${MODE}" == "list-sessions" ]]; then
    list_sessions
    exit 0
  fi

  case "${MODE}" in
    new)
      create_new_session
      USER_PROMPT="$(build_new_prompt "${SESSION_NAME}" "saves/${SESSION_NAME}")"
      ;;
    resume)
      resolve_resume_session
      USER_PROMPT="$(build_resume_prompt "${SESSION_NAME}" "saves/${SESSION_NAME}")"
      ;;
    *)
      usage
      exit 1
      ;;
  esac

  build_system_prompt
  append_runtime_packet_to_user_prompt

  cd "${SCENARIO_WORKDIR}"

  if [[ "${PROMPT_ONLY}" == "1" ]]; then
    write_generated_prompt_artifacts
    print_prompt_only_summary
    exit 0
  fi

  resolve_engine_command
  start_autosave_watcher

  case "${ENGINE_COMMAND}" in
    claude)
      launch_claude
      ;;
    codex)
      launch_codex
      ;;
  esac
}

main "${@}"
