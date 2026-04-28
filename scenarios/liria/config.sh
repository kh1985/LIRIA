#!/usr/bin/env bash

SCENARIO_ID="liria"
SCENARIO_NAME="LIRIA"
SCENARIO_ROOT="."

LIRIA_PROMPT_PROFILE="${LIRIA_PROMPT_PROFILE:-fast}"
LIRIA_RUNTIME_PACKET_ENABLED=0
LIRIA_AUTOSAVE_WATCH_ENABLED="${LIRIA_AUTOSAVE_WATCH_ENABLED:-1}"
LIRIA_TRANSCRIPT_ENABLED="${LIRIA_TRANSCRIPT_ENABLED:-1}"

LIRIA_HEROINE_INCIDENT_GATE_PROMPT_FILES=(
  "prompt/heroine_incident_gate.md"
)

LIRIA_BASE_NEW_SYSTEM_PROMPT_FILES=(
  "LIRIA.md"
  "prompt/core.md"
  "prompt/gm_policy.md"
  "prompt/core_newgame.md"
  "prompt/case_engine.md"
  "${LIRIA_HEROINE_INCIDENT_GATE_PROMPT_FILES[@]}"
  "prompt/runtime.md"
  "prompt/combat.md"
  "prompt/villain_engine.md"
  "prompt/romance.md"
  "prompt/save_resume.md"
)

LIRIA_BASE_RESUME_SYSTEM_PROMPT_FILES=(
  "LIRIA.md"
  "prompt/core.md"
  "prompt/gm_policy.md"
  "prompt/case_engine.md"
  "${LIRIA_HEROINE_INCIDENT_GATE_PROMPT_FILES[@]}"
  "prompt/runtime.md"
  "prompt/combat.md"
  "prompt/villain_engine.md"
  "prompt/romance.md"
  "prompt/save_resume.md"
)

LIRIA_HEAVY_SURFACE_PROMPT_FILES=(
  "prompt/visual_character_sheet.md"
  "prompt/manga_export.md"
  "prompt/story_reference.md"
)

LIRIA_FAST_NEW_SYSTEM_PROMPT_FILES=(
  "${LIRIA_BASE_NEW_SYSTEM_PROMPT_FILES[@]}"
)

LIRIA_FAST_RESUME_SYSTEM_PROMPT_FILES=(
  "${LIRIA_BASE_RESUME_SYSTEM_PROMPT_FILES[@]}"
)

LIRIA_LITE_NEW_SYSTEM_PROMPT_FILES=(
  "prompt/lite_core.md"
  "prompt/lite_case_engine.md"
  "${LIRIA_HEROINE_INCIDENT_GATE_PROMPT_FILES[@]}"
  "prompt/lite_runtime.md"
  "prompt/lite_save_resume.md"
  "prompt/core_newgame.md"
)

LIRIA_LITE_RESUME_SYSTEM_PROMPT_FILES=(
  "prompt/lite_core.md"
  "prompt/lite_case_engine.md"
  "${LIRIA_HEROINE_INCIDENT_GATE_PROMPT_FILES[@]}"
  "prompt/lite_runtime.md"
  "prompt/lite_save_resume.md"
)

LIRIA_FULL_NEW_SYSTEM_PROMPT_FILES=(
  "${LIRIA_BASE_NEW_SYSTEM_PROMPT_FILES[@]}"
  "${LIRIA_HEAVY_SURFACE_PROMPT_FILES[@]}"
)

LIRIA_FULL_RESUME_SYSTEM_PROMPT_FILES=(
  "${LIRIA_BASE_RESUME_SYSTEM_PROMPT_FILES[@]}"
  "${LIRIA_HEAVY_SURFACE_PROMPT_FILES[@]}"
)

case "${LIRIA_PROMPT_PROFILE}" in
  full)
    NEW_SYSTEM_PROMPT_FILES=("${LIRIA_FULL_NEW_SYSTEM_PROMPT_FILES[@]}")
    RESUME_SYSTEM_PROMPT_FILES=("${LIRIA_FULL_RESUME_SYSTEM_PROMPT_FILES[@]}")
    ;;
  lite|resume-min|min)
    LIRIA_RUNTIME_PACKET_ENABLED=1
    NEW_SYSTEM_PROMPT_FILES=("${LIRIA_LITE_NEW_SYSTEM_PROMPT_FILES[@]}")
    RESUME_SYSTEM_PROMPT_FILES=("${LIRIA_LITE_RESUME_SYSTEM_PROMPT_FILES[@]}")
    ;;
  fast|default|"")
    NEW_SYSTEM_PROMPT_FILES=("${LIRIA_FAST_NEW_SYSTEM_PROMPT_FILES[@]}")
    RESUME_SYSTEM_PROMPT_FILES=("${LIRIA_FAST_RESUME_SYSTEM_PROMPT_FILES[@]}")
    ;;
  *)
    NEW_SYSTEM_PROMPT_FILES=("${LIRIA_FAST_NEW_SYSTEM_PROMPT_FILES[@]}")
    RESUME_SYSTEM_PROMPT_FILES=("${LIRIA_FAST_RESUME_SYSTEM_PROMPT_FILES[@]}")
    ;;
esac

SYSTEM_PROMPT_FILES=("${RESUME_SYSTEM_PROMPT_FILES[@]}")

build_new_prompt() {
  local session_name="$1"
  local session_path="$2"

  cat <<EOF
LIRIA.md のルールで LIRIA を開始して。新しいゲームを始めたい。

今回の session は ${session_name}。
launcher が ${session_path} を作成済みなので、この session 配下だけを新規ゲームの保存先として使うこと。

標準保存先:
- session guide: ${session_path}/README.md
- current: ${session_path}/current/player.md, ${session_path}/current/gm.md, ${session_path}/current/relationships.md, ${session_path}/current/case.md, ${session_path}/current/hotset.md, ${session_path}/current/mechanics_card.md
- active checkpoints: ${session_path}/current/checkpoints/
- cast: ${session_path}/cast/heroine/*.md, ${session_path}/cast/npc/*.md
- design: ${session_path}/design/initial_answers.md, ${session_path}/design/story_reference.md, ${session_path}/design/story_spine.md, ${session_path}/design/organization_cast.md, ${session_path}/design/villain_design.md, ${session_path}/design/visual_pipeline.md, ${session_path}/design/manga_pipeline.md
- indexes: ${session_path}/indexes/cast_index.md, ${session_path}/indexes/decision_index.md, ${session_path}/indexes/event_index.md
- archive: ${session_path}/archive/chapters/, ${session_path}/archive/events/, ${session_path}/archive/checkpoints/, ${session_path}/archive/logs/

軽量起動では story_reference / story_spine / organization_cast / visual_pipeline / manga_pipeline などの重い sidecar は正本として維持しつつ、必要になった時だけ読む・更新すること。
通常進行は current/hotset.md, current/case.md, cast/*, indexes/cast_index.md, indexes/decision_index.md を優先し、indexes/event_index.md, current/mechanics_card.md, checkpoints は continuity 照合・能力処理・圧縮前点検など必要な場面だけ軽く開くこと。
画像生成・漫画化・物語参照の専門運用が必要な場面だけ該当 sidecar を開くこと。

repo root の heroine/ や npc/ は live cast の保存先として使わないこと。
session 直下の player.md / gm.md / harem.md / villain_design.md mirror は新規作成しないこと。
EOF
}

build_resume_prompt() {
  local session_name="$1"
  local session_path="$2"

  cat <<EOF
LIRIA.md のルールで LIRIA を再開して。

今回の session は ${session_name}。
読み込み対象は ${session_path}。

標準の正本（軽量再開で先に読む）:
- session guide: ${session_path}/README.md
- current: ${session_path}/current/player.md, ${session_path}/current/gm.md, ${session_path}/current/relationships.md, ${session_path}/current/case.md, ${session_path}/current/hotset.md
- cast: ${session_path}/cast/heroine/*.md, ${session_path}/cast/npc/*.md
- indexes: ${session_path}/indexes/cast_index.md, ${session_path}/indexes/decision_index.md

必要時だけ開く sidecar 正本:
- mechanics: ${session_path}/current/mechanics_card.md
- active checkpoints: ${session_path}/current/checkpoints/
- design: ${session_path}/design/initial_answers.md, ${session_path}/design/story_reference.md, ${session_path}/design/story_spine.md, ${session_path}/design/organization_cast.md, ${session_path}/design/villain_design.md, ${session_path}/design/visual_pipeline.md, ${session_path}/design/manga_pipeline.md
- event index: ${session_path}/indexes/event_index.md
- archive checkpoints: ${session_path}/archive/checkpoints/

軽量再開では current/hotset.md, current/case.md, indexes/cast_index.md, indexes/decision_index.md を先に使い、indexes/event_index.md, current/mechanics_card.md, checkpoints, story_reference / story_spine / organization_cast / visual_pipeline / manga_pipeline などの sidecar は必要になった時だけ読む・更新すること。
画像生成・漫画化・物語参照の専門運用が必要な場面では、該当 sidecar を正本として扱うこと。

repo root の heroine/ や npc/ を live cast として読まないこと。
session 直下の legacy mirror は、current/ や design/ が欠けている旧 session を読む時だけ read-only fallback として扱うこと。
EOF
}
