#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR" || exit 2

usage() {
  cat <<'EOF'
Usage:
  bash scripts/check_session_integrity.sh [session_name]
  bash scripts/check_session_integrity.sh --repo-only

Checks are read-only.
EOF
}

repo_only=0
session_name=""

case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;
  --repo-only)
    repo_only=1
    ;;
  "")
    ;;
  *)
    session_name="$1"
    ;;
esac

errors=0
warnings=0

error() {
  errors=$((errors + 1))
  printf 'ERROR: %s\n' "$*"
}

warn() {
  warnings=$((warnings + 1))
  printf 'WARN: %s\n' "$*"
}

note() {
  printf 'NOTE: %s\n' "$*"
}

have_rg=0
if command -v rg >/dev/null 2>&1; then
  have_rg=1
else
  warn "rg is not installed; repository-wide text guardrails are skipped"
fi

latest_session() {
  find saves -mindepth 1 -maxdepth 1 -type d -name 'session_*' 2>/dev/null | sort | tail -n 1 | sed 's#^saves/##'
}

first_phase() {
  local file="$1"
  [[ -f "$file" ]] || return 0
  sed -nE 's/^[[:space:]-]*現在フェーズ[[:space:]]*[:：][[:space:]]*(.+)$/\1/p' "$file" | head -n 1
}

section_count() {
  local file="$1"
  local heading="$2"
  local pattern="$3"
  [[ -f "$file" ]] || {
    printf '0\n'
    return
  }
  awk -v heading="$heading" -v pattern="$pattern" '
    $0 ~ "^##[[:space:]]+" heading "([[:space:]]|$)" { in_section=1; next }
    in_section && $0 ~ "^##[[:space:]]+" { in_section=0 }
    in_section && $0 ~ pattern { count++ }
    END { print count + 0 }
  ' "$file"
}

check_current_specs() {
  local base="$1"
  local player="${base}/current/player.md"
  local gm="${base}/current/gm.md"
  local harem="${base}/current/harem.md"
  local case_file="${base}/current/case.md"
  local villain="${base}/design/villain_design.md"
  local hotset="${base}/current/hotset.md"
  local cast_index="${base}/indexes/cast_index.md"
  local npc_dir="${base}/cast/npc"

  if [[ -f "$player" ]]; then
    local required_player=(
      "Appearance Profile"
      "Visual Character Sheet"
      "Ability Constraint Profile"
    )
    local item
    for item in "${required_player[@]}"; do
      if ! grep -Eq "$item" "$player"; then
        error "player.md missing current spec section: ${item}"
      fi
    done

    # 攻撃力/防御力ゲームに寄っていないかを、Equipment / Tools の文脈だけで警告する。
    if grep -Eq 'Equipment / Tools|Equipment|Tools' "$player" &&
      grep -Eq '攻撃力|防御力|attack power|defense power|offense|defense' "$player" &&
      ! grep -Eq '行動選択肢|リスク|痕跡|関係リスク|action option|risk|trace|relationship risk' "$player"; then
      warn "player.md Equipment / Tools looks combat-stat-only; add action options, risk, trace, or relationship risk"
    fi
  fi

  if [[ -f "$gm" ]]; then
    if ! grep -Eq 'Anti-Meta' "$gm"; then
      warn "gm.md missing Anti-Meta guardrail"
    fi
    if ! grep -Eq 'Knowledge Boundary' "$gm"; then
      warn "gm.md missing Knowledge Boundary guardrail"
    fi
    if ! grep -Eq 'Base Area Dossier|初期生活圏台帳' "$gm"; then
      warn "gm.md missing Base Area Dossier / 初期生活圏台帳"
    fi

    local candidate_count
    candidate_count="$(section_count "$gm" "Manga Export Candidates" '^[[:space:]]*-[[:space:]]*candidate[[:space:]]*:')"
    if [[ "${candidate_count:-0}" -gt 3 ]]; then
      warn "gm.md has too many Manga Export Candidates (${candidate_count}); keep current to 2-3 candidates"
    fi

    local prompt_hint_count
    prompt_hint_count="$(grep -Eic 'image prompt anchor|long prompt|model sheet prompt|prompt package' "$gm" 2>/dev/null || true)"
    if [[ "${prompt_hint_count:-0}" -gt 3 ]]; then
      warn "gm.md appears to contain too much image prompt material in current (${prompt_hint_count} prompt hints)"
    fi
  fi

  if [[ -f "$harem" ]] && ! grep -Eq 'Heroine Crisis Role' "$harem"; then
    warn "harem.md missing Heroine Crisis Role"
  fi

  if [[ -f "$case_file" ]]; then
    if ! grep -Eq 'Active Case' "$case_file"; then
      warn "case.md missing Active Case section"
    fi
    if ! grep -Eq 'short goal|短期目標' "$case_file"; then
      warn "case.md missing short goal"
    fi
    if ! grep -Eq 'handles|手がかり|具体物' "$case_file"; then
      warn "case.md missing handles"
    fi
    if ! grep -Eq 'progress condition|進行条件' "$case_file"; then
      warn "case.md missing progress condition"
    fi
    if ! grep -Eq 'if ignored|放置' "$case_file"; then
      warn "case.md missing if ignored"
    fi
  else
    warn "missing case card: ${case_file}"
  fi

  if [[ -f "$cast_index" ]] && grep -Eq '未命名|gm current 参照|current 参照' "$cast_index"; then
    warn "cast_index has unresolved NPC reference; important or recurring NPCs should be promoted to cast/npc/*.md"
  fi

  local npc_sheet_count=0
  if [[ -d "$npc_dir" ]]; then
    npc_sheet_count="$(find "$npc_dir" -maxdepth 1 -type f -name '*.md' ! -name '.gitkeep' 2>/dev/null | wc -l | tr -d ' ')"
  fi

  local major_npc_pressure
  major_npc_pressure="$(grep -Eh '外部面談相手|配置確認の相手|敵幹部|主要人物|上位存在|scene lead|回収員|現場調整|社名空欄の外部面談' "$gm" "$case_file" "$hotset" 2>/dev/null || true)"
  if [[ -n "$major_npc_pressure" && "${npc_sheet_count:-0}" -eq 0 ]]; then
    warn "important NPC / organization contact appears active, but cast/npc/*.md has no NPC sheet"
  fi

  if [[ -f "$villain" ]]; then
    if ! grep -Eq 'Organization Doctrine' "$villain"; then
      warn "villain_design.md missing Organization Doctrine"
    fi
    if ! grep -Eq 'weak joint|弱い継ぎ目' "$villain"; then
      warn "villain_design.md missing weak joint / 弱い継ぎ目"
    fi
  fi
}

check_session_scaffold() {
  local session="$1"
  local base="saves/${session}"

  note "checking session scaffold: ${session}"

  [[ -d "$base" ]] || {
    error "missing session directory: ${base}"
    return
  }

  local required_dirs=(
    "current"
    "cast"
    "cast/heroine"
    "cast/npc"
    "design"
    "indexes"
    "archive"
    "archive/chapters"
    "archive/events"
    "archive/logs"
  )

  local dir
  for dir in "${required_dirs[@]}"; do
    [[ -d "${base}/${dir}" ]] || error "missing directory: ${base}/${dir}"
  done

  [[ -f "${base}/session.json" ]] || warn "missing session metadata: ${base}/session.json"
  [[ -f "${base}/design/initial_answers.md" ]] || error "missing initial answers source of truth: ${base}/design/initial_answers.md"

  local player_phase gm_phase hotset_phase
  player_phase="$(first_phase "${base}/current/player.md")"
  gm_phase="$(first_phase "${base}/current/gm.md")"
  hotset_phase="$(first_phase "${base}/current/hotset.md")"

  if [[ -n "$player_phase" && -n "$gm_phase" && "$player_phase" != "$gm_phase" ]]; then
    error "current phase mismatch: player.md='${player_phase}' gm.md='${gm_phase}'"
  fi

  if [[ -n "$hotset_phase" && -n "$gm_phase" && "$hotset_phase" != "$gm_phase" ]]; then
    error "current phase mismatch: hotset.md='${hotset_phase}' gm.md='${gm_phase}'"
  fi

  if [[ -f "${base}/current/hotset.md" ]]; then
    local anchor_count
    anchor_count="$(grep -E '再開アンカー[[:space:]]*[:：]' "${base}/current/hotset.md" | wc -l | tr -d ' ')"
    if [[ "${anchor_count:-0}" -gt 1 ]]; then
      error "hotset has multiple resume anchors: ${base}/current/hotset.md (${anchor_count})"
    fi
  else
    warn "missing hotset cache: ${base}/current/hotset.md"
  fi

  check_current_specs "$base"

  if [[ "$have_rg" -eq 1 ]]; then
    local explicit_other_sessions
    explicit_other_sessions="$(rg -n 'saves/session_[A-Za-z0-9_-]+' "$base/current" "$base/cast" "$base/design" "$base/indexes" "$base/archive" 2>/dev/null | grep -v "saves/${session}" || true)"
    if [[ -n "$explicit_other_sessions" ]]; then
      warn "explicit references to other session paths found:"
      printf '%s\n' "$explicit_other_sessions"
    fi
  fi
}

check_repo_guardrails() {
  note "checking repository guardrails"

  [[ "$have_rg" -eq 1 ]] || return

  local legacy_suffix="001"
  local legacy_pattern="session_${legacy_suffix}"

  local live_hits
  live_hits="$(rg -n "$legacy_pattern" play.sh scenarios prompt scripts --glob '!scripts/check_session_integrity.sh' 2>/dev/null || true)"
  if [[ -n "$live_hits" ]]; then
    warn "possible fixed legacy session reference in live logic/prompt:"
    printf '%s\n' "$live_hits"
  fi

  local doc_hits
  doc_hits="$(rg -n "$legacy_pattern" README.md ARCHITECTURE.md MEMORY_MODEL.md INTEGRITY_CHECK.md VALIDATION.md TODO.md 2>/dev/null || true)"
  if [[ -n "$doc_hits" ]]; then
    note "legacy session references in docs; these should be migration/example only:"
    printf '%s\n' "$doc_hits"
  fi

  local root_cast_hits
  root_cast_hits="$(rg -n '(^|[[:space:]`"'"'"'(:])((heroine|npc)/\*\.md|(heroine|npc)/\[[^]]+\]\.md)' prompt README.md ARCHITECTURE.md MEMORY_MODEL.md INTEGRITY_CHECK.md VALIDATION.md TODO.md 2>/dev/null || true)"
  if [[ -n "$root_cast_hits" ]]; then
    warn "possible repo-root cast path reference:"
    printf '%s\n' "$root_cast_hits"
  fi

  if find heroine npc -maxdepth 1 -type f 2>/dev/null | grep -q .; then
    warn "repo-root cast files still exist; they must be legacy/import-only, not live data"
    find heroine npc -maxdepth 1 -type f 2>/dev/null | sort
  fi
}

check_repo_guardrails

if [[ "$repo_only" -eq 0 ]]; then
  if [[ -z "$session_name" ]]; then
    session_name="$(latest_session)"
    if [[ -z "$session_name" ]]; then
      warn "no saves/session_* directory found; skipping session checks"
    else
      note "no session specified; using latest session: ${session_name}"
    fi
  fi

  if [[ -n "$session_name" ]]; then
    check_session_scaffold "$session_name"
  fi
fi

printf 'Done: %d error(s), %d warning(s)\n' "$errors" "$warnings"

if [[ "$errors" -gt 0 ]]; then
  exit 1
fi

exit 0
