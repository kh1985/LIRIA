#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "${ROOT_DIR}"

# No session argument means play.sh resumes the latest available session.
exec bash "${ROOT_DIR}/play.sh" liria resume
