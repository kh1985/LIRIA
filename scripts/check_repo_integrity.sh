#!/usr/bin/env bash
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}" || exit 2

ok_count=0
warn_count=0
fail_count=0
skip_count=0

ok() {
  ok_count=$((ok_count + 1))
  printf '[OK] %s\n' "$*"
}

warn() {
  warn_count=$((warn_count + 1))
  printf '[WARN] %s\n' "$*"
}

fail() {
  fail_count=$((fail_count + 1))
  printf '[FAIL] %s\n' "$*"
}

skip() {
  skip_count=$((skip_count + 1))
  printf '[SKIP] %s\n' "$*"
}

indent_file() {
  sed 's/^/    /' "$1"
}

run_capture() {
  local label="$1"
  shift
  local tmp
  tmp="$(mktemp)"
  if "$@" >"${tmp}" 2>&1; then
    ok "${label}"
  else
    fail "${label}"
    indent_file "${tmp}"
  fi
  rm -f "${tmp}"
}

check_file_exists() {
  local file="$1"
  if [[ -e "${file}" ]]; then
    ok "exists: ${file}"
  else
    fail "missing: ${file}"
  fi
}

check_git_diff() {
  run_capture "git diff --check" git diff --check

  if git diff --cached --quiet --exit-code --; then
    skip "git diff --cached --check (no staged diff)"
  else
    run_capture "git diff --cached --check" git diff --cached --check
  fi
}

check_python_syntax() {
  local py_files=()
  local file

  while IFS= read -r file; do
    py_files+=("${file}")
  done < <(find scripts -maxdepth 1 -type f -name '*.py' | sort)

  if [[ "${#py_files[@]}" -eq 0 ]]; then
    skip "python syntax (no scripts/*.py)"
    return
  fi

  if ! command -v python3 >/dev/null 2>&1; then
    fail "python syntax (python3 not found)"
    return
  fi

  local pycache_dir
  local tmp
  pycache_dir="$(mktemp -d)"
  tmp="$(mktemp)"
  if PYTHONPYCACHEPREFIX="${pycache_dir}" python3 -m py_compile "${py_files[@]}" >"${tmp}" 2>&1; then
    ok "python syntax (${#py_files[@]} files)"
  else
    fail "python syntax (${#py_files[@]} files)"
    indent_file "${tmp}"
  fi
  rm -rf "${pycache_dir}"
  rm -f "${tmp}"
}

check_shell_syntax() {
  local shell_files=()
  local file

  while IFS= read -r file; do
    shell_files+=("${file}")
  done < <(find scripts -maxdepth 1 -type f -name '*.sh' | sort)

  for file in play.sh liria; do
    if [[ -f "${file}" ]]; then
      shell_files+=("${file}")
    fi
  done

  if [[ "${#shell_files[@]}" -eq 0 ]]; then
    skip "shell syntax (no shell files)"
    return
  fi

  for file in "${shell_files[@]}"; do
    run_capture "shell syntax: ${file}" bash -n "${file}"
    if [[ ! -x "${file}" ]]; then
      warn "shell executable bit missing: ${file}"
    fi
  done
}

check_required_files() {
  local files=(
    "README.md"
    "CONCEPT.md"
    "ARCHITECTURE.md"
    "REQUIREMENTS.md"
    "TODO.md"
    "LIRIA.md"
    "play.sh"
    "liria"
    "scenarios/liria/config.sh"
    "templates/session/session.json"
    "templates/session/current/player.md"
    "templates/session/current/gm.md"
    "templates/session/current/harem.md"
    "templates/session/current/case.md"
    "templates/session/current/hotset.md"
    "templates/session/current/mechanics_card.md"
  )
  local file

  for file in "${files[@]}"; do
    check_file_exists "${file}"
  done
}

check_prompt_files() {
  local files=(
    "prompt/core.md"
    "prompt/gm_policy.md"
    "prompt/core_newgame.md"
    "prompt/case_engine.md"
    "prompt/runtime.md"
    "prompt/combat.md"
    "prompt/villain_engine.md"
    "prompt/romance.md"
    "prompt/save_resume.md"
    "prompt/pi_player.md"
  )
  local file

  for file in "${files[@]}"; do
    check_file_exists "${file}"
  done
}

check_readme_command_targets() {
  local files=(
    "scripts/run_pi_player_smoke.sh"
    "scripts/run_ai_persona_playtest.sh"
    "scripts/run_ai_player_harness.sh"
    "scripts/analyze_play_log.sh"
    "scripts/check_session_integrity.sh"
    "scripts/pre_compress_check.sh"
    "scripts/create_manga_export.sh"
    "scripts/liria_prompt_auditor.py"
  )
  local file

  for file in "${files[@]}"; do
    check_file_exists "${file}"
  done
}

check_markdown_links() {
  if ! command -v python3 >/dev/null 2>&1; then
    fail "markdown md links (python3 not found)"
    return
  fi

  local tmp
  tmp="$(mktemp)"
  if python3 - "${ROOT_DIR}" >"${tmp}" 2>&1 <<'PY'
import os
import re
import sys

root = sys.argv[1]
sources = ["README.md", "ARCHITECTURE.md", "TODO.md"]
link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
missing = []

for source in sources:
    source_path = os.path.join(root, source)
    if not os.path.exists(source_path):
        missing.append(f"{source}: source file missing")
        continue

    with open(source_path, encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, 1):
            for match in link_re.finditer(line):
                raw_target = match.group(1).strip()
                target = raw_target.split()[0].strip("<>")
                if not target or target.startswith("#"):
                    continue
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                    continue

                path_only = target.split("#", 1)[0]
                path_only = path_only.split("?", 1)[0]
                if not path_only.endswith(".md"):
                    continue

                if os.path.isabs(path_only):
                    check_path = os.path.join(root, path_only.lstrip("/"))
                else:
                    check_path = os.path.normpath(
                        os.path.join(root, os.path.dirname(source), path_only)
                    )

                if not os.path.exists(check_path):
                    missing.append(f"{source}:{lineno}: missing link target: {raw_target}")

if missing:
    print("\n".join(missing))
    sys.exit(1)
PY
  then
    ok "markdown md links in README/ARCHITECTURE/TODO"
  else
    fail "markdown md links in README/ARCHITECTURE/TODO"
    indent_file "${tmp}"
  fi
  rm -f "${tmp}"
}

check_tracked_generated_files() {
  local violations=()
  local path

  while IFS= read -r -d '' path; do
    case "${path}" in
      saves/.gitkeep)
        ;;
      saves/*|exports/*|logs/*|rawlogs/*|tmp/*|.codex/generated/*|*.DS_Store|*.pyc|*.local.md)
        violations+=("${path}")
        ;;
      */__pycache__/*|__pycache__/*)
        violations+=("${path}")
        ;;
    esac
  done < <(git ls-files -z)

  if [[ "${#violations[@]}" -eq 0 ]]; then
    ok "tracked generated files guard"
  else
    fail "tracked generated files guard"
    printf '    %s\n' "${violations[@]}"
  fi
}

check_prompt_auditor() {
  if [[ ! -f "scripts/liria_prompt_auditor.py" ]]; then
    fail "prompt auditor (scripts/liria_prompt_auditor.py missing)"
    return
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    fail "prompt auditor (python3 not found)"
    return
  fi

  local tmp
  tmp="$(mktemp)"
  if python3 scripts/liria_prompt_auditor.py --root . >"${tmp}" 2>&1; then
    if grep -Eq '^\[WARN\]|^WARN:|warnings?:[[:space:]]*[1-9]' "${tmp}"; then
      warn "prompt auditor (warnings reported)"
      indent_file "${tmp}"
    else
      ok "prompt auditor"
    fi
  else
    fail "prompt auditor"
    indent_file "${tmp}"
  fi
  rm -f "${tmp}"
}

printf 'Repo technical integrity check\n'
printf 'Root: %s\n\n' "${ROOT_DIR}"

check_git_diff
check_python_syntax
check_shell_syntax
check_required_files
check_prompt_files
check_readme_command_targets
check_markdown_links
check_tracked_generated_files
check_prompt_auditor

printf '\nSummary: %d ok, %d warn, %d skip, %d fail\n' \
  "${ok_count}" "${warn_count}" "${skip_count}" "${fail_count}"

if [[ "${fail_count}" -eq 0 ]]; then
  printf 'Repo integrity check: OK\n'
  exit 0
fi

printf 'Repo integrity check: FAILED\n'
exit 1
