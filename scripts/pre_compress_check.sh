#!/usr/bin/env bash
# pre_compress_check.sh — /compress 前に必須要素が保存されているか検証する
#
# 使い方:
#   bash scripts/pre_compress_check.sh [session_name]
#
# /compress する前にこのスクリプトを実行して、
# 重要情報がセーブファイルに書き込まれていることを確認する。
# 全チェックが通ったら /compress しても安全。

set -uo pipefail

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
CURRENT="${ROOT_DIR}/saves/${SESSION}/current"
INDEXES="${ROOT_DIR}/saves/${SESSION}/indexes"
DESIGN="${ROOT_DIR}/saves/${SESSION}/design"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

check() {
  local label="$1"
  local file="$2"
  local pattern="$3"

  if [[ ! -f "${file}" ]]; then
    echo -e "  ${RED}✗ ${label}: ファイルが見つかりません (${file})${NC}"
    ((FAIL++))
    return
  fi

  if grep -Eq "${pattern}" "${file}" 2>/dev/null; then
    echo -e "  ${GREEN}✓ ${label}${NC}"
    ((PASS++))
  else
    echo -e "  ${RED}✗ ${label}: 「${pattern}」が見つかりません${NC}"
    ((FAIL++))
  fi
}

warn_check() {
  local label="$1"
  local file="$2"
  local pattern="$3"

  if [[ ! -f "${file}" ]]; then
    echo -e "  ${YELLOW}△ ${label}: ファイルなし${NC}"
    ((WARN++))
    return
  fi

  if grep -Eq "${pattern}" "${file}" 2>/dev/null; then
    echo -e "  ${GREEN}✓ ${label}${NC}"
    ((PASS++))
  else
    echo -e "  ${YELLOW}△ ${label}: 推奨項目が未記載${NC}"
    ((WARN++))
  fi
}

echo ""
echo "========================================="
echo "  /compress 前の安全チェック"
echo "  セッション: ${SESSION}"
echo "========================================="
echo ""

# --- player.md ---
echo "■ player.md（プレイヤー状態）"
check "現在HP" "${CURRENT}/player.md" "現在HP"
check "能力使用残回数" "${CURRENT}/player.md" "能力使用残回数"
check "現在フェーズ" "${CURRENT}/player.md" "現在フェーズ"
check "コンディション" "${CURRENT}/player.md" "コンディション"
check "Appearance Profile" "${CURRENT}/player.md" "Appearance Profile"
check "Visual Character Sheet" "${CURRENT}/player.md" "Visual Character Sheet"
check "model sheet status" "${CURRENT}/player.md" "model sheet status"
warn_check "image prompt anchor" "${CURRENT}/player.md" "image prompt anchor"
check "Ability Constraint Profile" "${CURRENT}/player.md" "Ability Constraint Profile"
check "output scale" "${CURRENT}/player.md" "output scale"
check "uses / cooldown" "${CURRENT}/player.md" "uses.*cooldown"
check "trace" "${CURRENT}/player.md" "trace"
check "relationship risk" "${CURRENT}/player.md" "relationship risk"
check "Work Profile" "${CURRENT}/player.md" "Work Profile"
check "Life Base" "${CURRENT}/player.md" "Life Base"
warn_check "Equipment / Tools" "${CURRENT}/player.md" "Equipment"
echo ""

# --- gm.md ---
echo "■ gm.md（GM状態）"
check "現在のフック" "${CURRENT}/gm.md" "現在のフック"
check "脅威クロック" "${CURRENT}/gm.md" "脅威クロック"
check "勢力クロック" "${CURRENT}/gm.md" "勢力クロック"
warn_check "直近の後遺症" "${CURRENT}/gm.md" "直近の後遺症"
warn_check "知識スコープ" "${CURRENT}/gm.md" "知識スコープ"
warn_check "自動セーブ管理" "${CURRENT}/gm.md" "自動セーブ管理"
warn_check "Anti-Meta Dialogue" "${CURRENT}/gm.md" "Anti-Meta"
warn_check "Knowledge Boundary" "${CURRENT}/gm.md" "Knowledge Boundary"
warn_check "Anti-Leading" "${CURRENT}/gm.md" "Anti-Leading"
warn_check "Manga Export Candidates" "${CURRENT}/gm.md" "Manga Export Candidates"
echo ""

# --- harem.md ---
echo "■ harem.md（Relationship / Heroine Network）"
check "AFFINITY" "${CURRENT}/harem.md" "AFFINITY"
check "bond" "${CURRENT}/harem.md" "bond"
warn_check "hidden 深化ベクトル" "${CURRENT}/harem.md" "hidden 深化ベクトル"
warn_check "約束体系" "${CURRENT}/harem.md" "約束体系"
warn_check "Heroine Crisis Role" "${CURRENT}/harem.md" "Heroine Crisis Role"
echo ""

# --- hotset.md ---
echo "■ hotset.md（再開キャッシュ）"
check "現在フェーズ" "${CURRENT}/hotset.md" "現在フェーズ"
check "再開アンカー" "${CURRENT}/hotset.md" "再開アンカー"
check "能力" "${CURRENT}/hotset.md" "能力"
warn_check "Appearance Profile 抜粋" "${CURRENT}/hotset.md" "Appearance Profile"
warn_check "Visual Character Sheet 抜粋" "${CURRENT}/hotset.md" "Visual Character Sheet"
warn_check "Organization Doctrine 抜粋" "${CURRENT}/hotset.md" "Organization Doctrine"
echo ""

# --- design ---
echo "■ design（長期設計）"
warn_check "Organization Doctrine" "${DESIGN}/villain_design.md" "Organization Doctrine"
warn_check "visual_pipeline 存在" "${DESIGN}/visual_pipeline.md" "Visual Character Sheet"
warn_check "manga_pipeline 存在" "${DESIGN}/manga_pipeline.md" "Manga Pipeline"
warn_check "contact surface" "${DESIGN}/villain_design.md" "contact surface"
warn_check "weak joint / 弱い継ぎ目" "${DESIGN}/villain_design.md" "weak joint|弱い継ぎ目"
echo ""

# --- indexes ---
echo "■ indexes（索引）"
check "event_index 存在" "${INDEXES}/event_index.md" "event"
check "decision_index 存在" "${INDEXES}/decision_index.md" "決定"
warn_check "cast_index 存在" "${INDEXES}/cast_index.md" "cast|キャスト|ヒロイン"
echo ""

# --- 生ログ ---
echo "■ 生ログ"
LOGS_DIR="${ROOT_DIR}/saves/${SESSION}/archive/logs"
TODAY="$(date +%Y%m%d)"
if ls "${LOGS_DIR}/raw_${TODAY}"* &>/dev/null 2>&1; then
  echo -e "  ${GREEN}✓ 本日の生ログあり${NC}"
  ((PASS++))
else
  echo -e "  ${YELLOW}△ 本日の生ログなし（bash scripts/save_rawlog.sh で保存推奨）${NC}"
  ((WARN++))
fi
echo ""

# --- 結果 ---
echo "========================================="
echo -e "  結果: ${GREEN}${PASS} 通過${NC} / ${RED}${FAIL} 失敗${NC} / ${YELLOW}${WARN} 警告${NC}"
echo "========================================="
echo ""

if [[ "${FAIL}" -gt 0 ]]; then
  echo -e "${RED}✗ /compress は安全ではありません。失敗項目をセーブしてから実行してください。${NC}"
  exit 1
elif [[ "${WARN}" -gt 0 ]]; then
  echo -e "${YELLOW}△ 警告項目があります。可能なら対処してから /compress してください。${NC}"
  exit 0
else
  echo -e "${GREEN}✓ 全チェック通過。/compress しても安全です。${NC}"
  exit 0
fi
