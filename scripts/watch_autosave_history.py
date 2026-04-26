#!/usr/bin/env python3
"""Watch Codex/Claude input history and tick LIRIA autosave outside the game UI.

The interactive engine does not return to play.sh between prompts, so launcher
hooks cannot run after each turn. This sidecar watches the engine's user-input
history for the active LIRIA session and runs autosave_turn.sh when normal
player inputs arrive. Output is written to a session log, not to the game UI.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLL_SECONDS = 2.0
BOOTSTRAP_WAIT_SECONDS = 20


@dataclass(frozen=True)
class HistoryRecord:
    source: str
    session_id: str
    timestamp: float
    text: str
    project: str = ""


def main() -> int:
    args = parse_args()
    session_dir = ROOT / "saves" / args.session
    log_dir = session_dir / "archive" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"autosave_watcher_{time.strftime('%Y%m%d_%H%M%S')}.log"

    with log_path.open("a", encoding="utf-8") as log:
        log_line(log, f"watcher start session={args.session} engine={args.engine} parent={args.parent_pid}")
        try:
            watch(args, log)
        except Exception as exc:  # noqa: BLE001 - keep sidecar failure out of game UI.
            log_line(log, f"watcher error: {type(exc).__name__}: {exc}")
            return 1
        finally:
            log_line(log, "watcher stop")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Watch LIRIA turn inputs and tick autosave.")
    parser.add_argument("--session", required=True, help="LIRIA session name, e.g. kaneko3")
    parser.add_argument("--engine", default="auto", choices=["auto", "codex", "claude"], help="Active CLI engine")
    parser.add_argument("--parent-pid", type=int, required=True, help="PID to watch; exits when it disappears")
    parser.add_argument("--threshold", type=int, default=10, help="Autosave threshold; autosave_turn.sh owns the actual reset")
    return parser.parse_args()


def watch(args: argparse.Namespace, log: Any) -> None:
    start_time = time.time() - 5
    active_source = ""
    active_session_id = ""
    seen: set[tuple[str, str, float, str]] = set()
    bootstrap_deadline = time.time() + BOOTSTRAP_WAIT_SECONDS

    while parent_alive(args.parent_pid):
        records = read_history_records(args.engine)
        for record in records:
            if record.timestamp < start_time:
                continue
            key = (record.source, record.session_id, record.timestamp, record.text)
            if key in seen:
                continue

            if not active_session_id:
                if is_bootstrap_record(record, args.session):
                    active_source = record.source
                    active_session_id = record.session_id
                    seen.add(key)
                    log_line(log, f"bound to {active_source} session_id={active_session_id}")
                elif time.time() > bootstrap_deadline and is_safe_fallback_record(record):
                    active_source = record.source
                    active_session_id = record.session_id
                    seen.add(key)
                    log_line(log, f"fallback-bound to {active_source} session_id={active_session_id}")
                    if is_countable_player_input(record.text):
                        result = run_autosave_turn(args.session, args.engine, active_session_id)
                        log_line(log, f"tick from fallback input: {shorten(record.text)}")
                        for line in result.splitlines():
                            log_line(log, f"  {line}")
                continue

            if record.source != active_source or record.session_id != active_session_id:
                continue

            seen.add(key)
            if not is_countable_player_input(record.text):
                log_line(log, f"skip meta/input: {shorten(record.text)}")
                continue

            result = run_autosave_turn(args.session, args.engine, active_session_id)
            log_line(log, f"tick from input: {shorten(record.text)}")
            for line in result.splitlines():
                log_line(log, f"  {line}")

        time.sleep(POLL_SECONDS)


def parent_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def read_history_records(engine: str) -> list[HistoryRecord]:
    records: list[HistoryRecord] = []
    if engine in {"auto", "codex"}:
        records.extend(read_codex_history())
    if engine in {"auto", "claude"}:
        records.extend(read_claude_history())
    records.sort(key=lambda record: record.timestamp)
    return records


def read_codex_history() -> list[HistoryRecord]:
    path = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "history.jsonl"
    records: list[HistoryRecord] = []
    for obj in read_jsonl(path):
        session_id = str(obj.get("session_id", ""))
        text = str(obj.get("text", ""))
        timestamp = float(obj.get("ts", 0) or 0)
        if session_id and text and timestamp:
            records.append(HistoryRecord(source="codex", session_id=session_id, timestamp=timestamp, text=text))
    return records


def read_claude_history() -> list[HistoryRecord]:
    path = Path(os.environ.get("CLAUDE_HOME", Path.home() / ".claude")) / "history.jsonl"
    records: list[HistoryRecord] = []
    for obj in read_jsonl(path):
        session_id = str(obj.get("sessionId", ""))
        text = str(obj.get("display", ""))
        raw_timestamp = float(obj.get("timestamp", 0) or 0)
        timestamp = raw_timestamp / 1000 if raw_timestamp > 10_000_000_000 else raw_timestamp
        project = str(obj.get("project", ""))
        if session_id and text and timestamp:
            records.append(
                HistoryRecord(
                    source="claude",
                    session_id=session_id,
                    timestamp=timestamp,
                    text=text,
                    project=project,
                )
            )
    return records


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    objects: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict):
                    objects.append(obj)
    except OSError:
        return []
    return objects


def is_bootstrap_record(record: HistoryRecord, session: str) -> bool:
    text = record.text
    return (
        "LIRIA.md のルール" in text
        and f"今回の session は {session}" in text
        and (f"読み込み対象は saves/{session}" in text or f"launcher が saves/{session}" in text)
    )


def is_safe_fallback_record(record: HistoryRecord) -> bool:
    if record.source == "codex":
        return True
    if record.source == "claude" and record.project:
        try:
            return Path(record.project).resolve() == ROOT.resolve()
        except OSError:
            return False
    return False


def is_countable_player_input(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    lowered = stripped.lower()
    if "LIRIA.md のルール" in stripped or "今回の session は" in stripped:
        return False
    if lowered in {"q", "quit", "exit"}:
        return False
    if re.match(r"^\(?\s*gm(?:\s|$)", lowered):
        return False
    meta_prefixes = (
        "セーブ",
        "保存",
        "今日はここまで",
        "続きはまた",
        "また今度",
        "ここで終わる",
        "やめる",
    )
    return not stripped.startswith(meta_prefixes)


def run_autosave_turn(session: str, engine: str, engine_session_id: str) -> str:
    command = ["bash", str(ROOT / "scripts" / "autosave_turn.sh"), session, "--engine", engine]
    env = os.environ.copy()
    env["LIRIA_ACTIVE_ENGINE_SESSION_ID"] = engine_session_id
    completed = subprocess.run(  # noqa: S603 - repo-local script with fixed path.
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = completed.stdout.strip()
    if completed.returncode != 0:
        return f"autosave_turn failed ({completed.returncode})\n{output}"
    return output


def log_line(log: Any, message: str) -> None:
    log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n")
    log.flush()


def shorten(text: str, limit: int = 90) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1] + "..."


if __name__ == "__main__":
    raise SystemExit(main())
