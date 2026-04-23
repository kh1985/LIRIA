#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "${ROOT_DIR}"

echo "Available scenarios:"
bash "${ROOT_DIR}/play.sh" list
echo
read -r -p "Scenario name: " scenario
read -r -p "Mode (new/resume/list-sessions) [resume]: " mode
mode="${mode:-resume}"

if [[ "${mode}" == "list-sessions" ]]; then
  exec bash "${ROOT_DIR}/play.sh" list-sessions "${scenario}"
fi

if [[ "${mode}" == "resume" ]]; then
  echo
  echo "Available sessions:"
  bash "${ROOT_DIR}/play.sh" list-sessions "${scenario}"
  echo
  read -r -p "Session name [latest]: " session
  if [[ -n "${session}" ]]; then
    exec bash "${ROOT_DIR}/play.sh" "${scenario}" resume "${session}"
  fi
  exec bash "${ROOT_DIR}/play.sh" "${scenario}" resume
fi

read -r -p "New session name [auto]: " session
if [[ -n "${session}" ]]; then
  exec bash "${ROOT_DIR}/play.sh" "${scenario}" new "${session}"
fi

exec bash "${ROOT_DIR}/play.sh" "${scenario}" new
