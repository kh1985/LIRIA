#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE_DIR="${ROOT_DIR}/templates/session"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/create_session.sh <scenario_id> <session_name> [scenario_workdir]

Creates a self-contained save scaffold under saves/<session_name>.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || "$#" -lt 2 ]]; then
  usage
  exit 0
fi

SCENARIO_ID="$1"
SESSION_NAME="$2"
SCENARIO_WORKDIR="${3:-${ROOT_DIR}}"
SAVE_ROOT="${SCENARIO_WORKDIR}/saves"
SESSION_DIR="${SAVE_ROOT}/${SESSION_NAME}"

if [[ ! "${SESSION_NAME}" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "invalid session name: ${SESSION_NAME}"
  echo "use only letters, numbers, dot, underscore, and hyphen; do not include slashes"
  exit 1
fi

if [[ ! -d "${TEMPLATE_DIR}" ]]; then
  echo "session template not found: ${TEMPLATE_DIR}"
  exit 1
fi

if [[ -e "${SESSION_DIR}" ]]; then
  echo "session already exists: ${SESSION_DIR}"
  exit 1
fi

mkdir -p "${SAVE_ROOT}"
mkdir -p "${SESSION_DIR}"
cp -R "${TEMPLATE_DIR}/." "${SESSION_DIR}/"

mkdir -p \
  "${SESSION_DIR}/current" \
  "${SESSION_DIR}/cast/heroine" \
  "${SESSION_DIR}/cast/npc" \
  "${SESSION_DIR}/design" \
  "${SESSION_DIR}/indexes" \
  "${SESSION_DIR}/archive/chapters" \
  "${SESSION_DIR}/archive/events" \
  "${SESSION_DIR}/archive/logs"

CREATED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
cat > "${SESSION_DIR}/session.json" <<EOF
{
  "session_name": "${SESSION_NAME}",
  "scenario_id": "${SCENARIO_ID}",
  "created_at": "${CREATED_AT}",
  "layout_version": 2,
  "source_of_truth": {
    "current": "current/",
    "cast": "cast/",
    "design": "design/",
    "indexes": "indexes/",
    "archive": "archive/"
  }
}
EOF

echo "created session: ${SESSION_NAME}"
echo "session path: ${SESSION_DIR}"
