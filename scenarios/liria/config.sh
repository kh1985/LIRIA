#!/usr/bin/env bash

SCENARIO_ID="liria"
SCENARIO_NAME="LIRIA"
SCENARIO_ROOT="."
NEW_SYSTEM_PROMPT_FILES=(
  "GALGE.md"
  "prompt/core.md"
  "prompt/gm_policy.md"
  "prompt/visual_character_sheet.md"
  "prompt/manga_export.md"
  "prompt/core_newgame.md"
  "prompt/runtime.md"
  "prompt/combat.md"
  "prompt/villain_engine.md"
  "prompt/romance.md"
  "prompt/save_resume.md"
)

RESUME_SYSTEM_PROMPT_FILES=(
  "GALGE.md"
  "prompt/core.md"
  "prompt/gm_policy.md"
  "prompt/visual_character_sheet.md"
  "prompt/manga_export.md"
  "prompt/runtime.md"
  "prompt/combat.md"
  "prompt/villain_engine.md"
  "prompt/romance.md"
  "prompt/save_resume.md"
)

SYSTEM_PROMPT_FILES=("${RESUME_SYSTEM_PROMPT_FILES[@]}")

build_new_prompt() {
  local session_name="$1"
  local session_path="$2"

  cat <<EOF
GALGE.md のルールで LIRIA を開始して。新しいゲームを始めたい。

今回の session は ${session_name}。
launcher が ${session_path} を作成済みなので、この session 配下だけを新規ゲームの保存先として使うこと。

標準保存先:
- current: ${session_path}/current/player.md, ${session_path}/current/gm.md, ${session_path}/current/harem.md, ${session_path}/current/hotset.md
- cast: ${session_path}/cast/heroine/*.md, ${session_path}/cast/npc/*.md
- design: ${session_path}/design/villain_design.md, ${session_path}/design/visual_pipeline.md, ${session_path}/design/manga_pipeline.md
- indexes: ${session_path}/indexes/cast_index.md, ${session_path}/indexes/decision_index.md, ${session_path}/indexes/event_index.md
- archive: ${session_path}/archive/chapters/, ${session_path}/archive/events/, ${session_path}/archive/logs/

repo root の heroine/ や npc/ は live cast の保存先として使わないこと。
session 直下の player.md / gm.md / harem.md / villain_design.md mirror は新規作成しないこと。
EOF
}

build_resume_prompt() {
  local session_name="$1"
  local session_path="$2"

  cat <<EOF
GALGE.md のルールで LIRIA を再開して。

今回の session は ${session_name}。
読み込み対象は ${session_path}。

標準の正本:
- current: ${session_path}/current/player.md, ${session_path}/current/gm.md, ${session_path}/current/harem.md, ${session_path}/current/hotset.md
- cast: ${session_path}/cast/heroine/*.md, ${session_path}/cast/npc/*.md
- design: ${session_path}/design/villain_design.md, ${session_path}/design/visual_pipeline.md, ${session_path}/design/manga_pipeline.md
- indexes: ${session_path}/indexes/cast_index.md, ${session_path}/indexes/decision_index.md, ${session_path}/indexes/event_index.md

repo root の heroine/ や npc/ を live cast として読まないこと。
session 直下の legacy mirror は、current/ や design/ が欠けている旧 session を読む時だけ read-only fallback として扱うこと。
EOF
}
