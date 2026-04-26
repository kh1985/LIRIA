#!/usr/bin/env python3
"""Run multiple AI Persona Playtests and collect a small Markdown report.

This is a thin harness over scripts/run_ai_persona_playtest.py. It does not
implement a fully autonomous GM/Player loop, and it does not ask AI to edit save
files directly. Each persona playtest remains responsible for read-only raw log
generation and optional analysis.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_DIR = ROOT / "saves" / "_harness_reports"
MAX_TURNS = 1000


@dataclass(frozen=True)
class PersonaRun:
    name: str
    path: Path
    turns: int


@dataclass
class RunResult:
    persona: PersonaRun
    session_name: str
    exit_status: int
    raw_log_path: str = ""
    analysis_path: str = ""
    dry_run_prompt_path: str = ""
    stdout: str = ""


def main() -> int:
    args = parse_args()
    started_at = datetime.now().astimezone()
    report_stamp = started_at.strftime("%Y%m%d_%H%M%S")
    personas = load_personas(args)
    results: list[RunResult] = []

    for index, persona in enumerate(personas, start=1):
        session_name = build_session_name(args.session_prefix, report_stamp, index, persona.name)
        result = run_persona(
            persona=persona,
            session_name=session_name,
            model=args.model,
            timeout_seconds=args.timeout_seconds,
            analyze=args.analyze,
            dry_run=args.dry_run,
        )
        results.append(result)
        print(
            f"[{index}/{len(personas)}] {persona.name}: "
            f"exit={result.exit_status} session={session_name}"
        )

    report_path = write_report(
        report_dir=args.report_dir,
        report_stamp=report_stamp,
        started_at=started_at,
        dry_run=args.dry_run,
        analyze=args.analyze,
        results=results,
    )
    print(f"AI player harness report: {display_path(report_path)}")

    failed = [result for result in results if result.exit_status != 0]
    return 1 if failed else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run multiple LIRIA AI persona playtests and summarize the outputs.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="YAML config with a personas list. Item fields: name, path, turns.",
    )
    parser.add_argument(
        "--persona",
        action="append",
        type=Path,
        default=[],
        help="Persona file path. Repeat to run multiple personas.",
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=8,
        help=f"Default turns per persona unless config item overrides it. 1-{MAX_TURNS}. Default: 8.",
    )
    parser.add_argument("--model", help="Optional Codex model override passed to each playtest.")
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        help="Optional timeout passed to each persona playtest.",
    )
    parser.add_argument(
        "--no-analyze",
        dest="analyze",
        action="store_false",
        help="Skip analyze_play_log for each persona playtest.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Create sessions/prompts and report only; pass --dry-run to each persona playtest.",
    )
    parser.add_argument(
        "--session-prefix",
        default="session_ai_harness",
        help="Prefix for auto-generated per-persona session names.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=DEFAULT_REPORT_DIR,
        help="Directory for ai_player_harness_*.md reports.",
    )
    parser.set_defaults(analyze=True)
    args = parser.parse_args()

    if args.turns < 1 or args.turns > MAX_TURNS:
        parser.error(f"--turns must be between 1 and {MAX_TURNS}")
    if args.timeout_seconds is not None and args.timeout_seconds < 60:
        parser.error("--timeout-seconds must be at least 60")
    if args.config is None and not args.persona:
        parser.error("provide --config or at least one --persona")
    args.report_dir = resolve_path(args.report_dir)
    return args


def load_personas(args: argparse.Namespace) -> list[PersonaRun]:
    personas: list[PersonaRun] = []
    if args.config is not None:
        personas.extend(load_config(args.config, default_turns=args.turns))
    for persona_path in args.persona:
        resolved = resolve_path(persona_path)
        personas.append(
            PersonaRun(
                name=slugify(resolved.stem),
                path=resolved,
                turns=args.turns,
            )
        )
    if not personas:
        raise SystemExit("no personas configured")

    for persona in personas:
        if persona.turns < 1 or persona.turns > MAX_TURNS:
            raise SystemExit(f"{persona.name}: turns must be between 1 and {MAX_TURNS}")
        if not persona.path.exists():
            raise SystemExit(f"{persona.name}: persona file not found: {display_path(persona.path)}")
    return personas


def load_config(config_path: Path, *, default_turns: int) -> list[PersonaRun]:
    path = resolve_path(config_path)
    if not path.exists():
        raise SystemExit(f"config not found: {display_path(path)}")

    raw_data = parse_config(path)
    if isinstance(raw_data, list):
        items = raw_data
    elif isinstance(raw_data, dict):
        items = raw_data.get("personas", [])
    else:
        raise SystemExit("config must be a mapping with personas or a list")

    personas: list[PersonaRun] = []
    for index, item in enumerate(items, start=1):
        if isinstance(item, str):
            item = {"path": item}
        if not isinstance(item, dict):
            raise SystemExit(f"config persona #{index} must be a string or mapping")
        path_value = item.get("path") or item.get("persona")
        if not path_value:
            raise SystemExit(f"config persona #{index} is missing path")
        path = resolve_path(Path(str(path_value)))
        name = str(item.get("name") or path.stem)
        turns = int(item.get("turns") or default_turns)
        personas.append(PersonaRun(name=slugify(name), path=path, turns=turns))
    return personas


def parse_config(path: Path) -> object:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        return parse_limited_yaml(text)
    loaded = yaml.safe_load(text)
    return {} if loaded is None else loaded


def parse_limited_yaml(text: str) -> dict[str, object]:
    """Parse the small harness sample format without requiring PyYAML."""

    personas: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    in_personas = False

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        stripped = raw_line.strip()
        if stripped == "personas:":
            in_personas = True
            continue
        if not in_personas:
            continue
        if stripped.startswith("- "):
            if current is not None:
                personas.append(current)
            current = {}
            rest = stripped[2:].strip()
            if rest:
                key, value = parse_key_value(rest)
                current[key] = parse_scalar(value)
            continue
        if current is not None and ":" in stripped:
            key, value = parse_key_value(stripped)
            current[key] = parse_scalar(value)

    if current is not None:
        personas.append(current)
    return {"personas": personas}


def parse_key_value(text: str) -> tuple[str, str]:
    if ":" not in text:
        raise SystemExit(f"invalid config line: {text}")
    key, value = text.split(":", 1)
    return key.strip(), value.strip()


def parse_scalar(value: str) -> object:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value


def run_persona(
    *,
    persona: PersonaRun,
    session_name: str,
    model: str | None,
    timeout_seconds: int | None,
    analyze: bool,
    dry_run: bool,
) -> RunResult:
    argv = [
        sys.executable,
        str(ROOT / "scripts/run_ai_persona_playtest.py"),
        session_name,
        "--turns",
        str(persona.turns),
        "--persona",
        str(persona.path),
    ]
    if model:
        argv.extend(["--model", model])
    if timeout_seconds is not None:
        argv.extend(["--timeout-seconds", str(timeout_seconds)])
    if not analyze:
        argv.append("--no-analyze")
    if dry_run:
        argv.append("--dry-run")

    completed = subprocess.run(
        argv,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return parse_run_result(
        persona=persona,
        session_name=session_name,
        exit_status=completed.returncode,
        stdout=completed.stdout,
    )


def parse_run_result(
    *,
    persona: PersonaRun,
    session_name: str,
    exit_status: int,
    stdout: str,
) -> RunResult:
    return RunResult(
        persona=persona,
        session_name=session_name,
        exit_status=exit_status,
        raw_log_path=match_output_path(stdout, r"^AI persona play log: (.+)$"),
        analysis_path=match_output_path(stdout, r"^analysis report: (.+)$"),
        dry_run_prompt_path=match_output_path(stdout, r"^dry-run prompt: (.+)$"),
        stdout=stdout,
    )


def match_output_path(output: str, pattern: str) -> str:
    match = re.search(pattern, output, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def write_report(
    *,
    report_dir: Path,
    report_stamp: str,
    started_at: datetime,
    dry_run: bool,
    analyze: bool,
    results: list[RunResult],
) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"ai_player_harness_{report_stamp}.md"
    failed = [result for result in results if result.exit_status != 0]
    lines = [
        f"# AI Player Harness Report: {report_stamp}",
        "",
        f"- 実行日時: {started_at.isoformat(timespec='seconds')}",
        f"- dry_run: {str(dry_run).lower()}",
        f"- analyze: {str(analyze).lower()}",
        f"- total_personas: {len(results)}",
        f"- failed_personas: {len(failed)}",
        "",
        "## Runs",
        "",
        "| status | persona | session | turns | raw log | analysis | prompt |",
        "|---|---|---|---:|---|---|---|",
    ]
    for result in results:
        status = "ok" if result.exit_status == 0 else f"failed({result.exit_status})"
        lines.append(
            "| "
            + " | ".join(
                [
                    status,
                    result.persona.name,
                    result.session_name,
                    str(result.persona.turns),
                    md_path(result.raw_log_path),
                    md_path(result.analysis_path),
                    md_path(result.dry_run_prompt_path),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Failed Personas", ""])
    if failed:
        for result in failed:
            lines.append(f"- {result.persona.name}: exit status {result.exit_status}")
    else:
        lines.append("- なし")

    lines.extend(["", "## Next Logs To Review", ""])
    review_targets = next_review_targets(results)
    if review_targets:
        for target in review_targets:
            lines.append(f"- {target}")
    else:
        lines.append("- dry-run のため raw log / analysis は未生成")

    lines.extend(["", "## Safety Notes", ""])
    lines.append("- このHarnessは `scripts/run_ai_persona_playtest.py` を順番に呼ぶだけで、完全自律GM/Playerループは実装しない。")
    lines.append("- AIにはsaveファイルを直接編集させない。raw log生成後の保存反映やsession更新は別処理。")

    lines.extend(["", "## Raw Runner Output", ""])
    for result in results:
        lines.extend(
            [
                f"### {result.persona.name}",
                "",
                "```text",
                result.stdout.strip() or "(no output)",
                "```",
                "",
            ]
        )

    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return report_path


def next_review_targets(results: list[RunResult]) -> list[str]:
    targets: list[str] = []
    for result in results:
        if result.exit_status != 0:
            targets.append(f"{result.persona.name}: report内の Raw Runner Output")
        elif result.analysis_path:
            targets.append(f"{result.persona.name}: {md_path(result.analysis_path)}")
        elif result.raw_log_path:
            targets.append(f"{result.persona.name}: {md_path(result.raw_log_path)}")
        elif result.dry_run_prompt_path:
            targets.append(f"{result.persona.name}: {md_path(result.dry_run_prompt_path)}")
    return targets


def md_path(path: str) -> str:
    return f"`{path}`" if path else "-"


def build_session_name(prefix: str, stamp: str, index: int, persona_name: str) -> str:
    safe_prefix = slugify(prefix)
    return f"{safe_prefix}_{stamp}_{index:02d}_{slugify(persona_name)}"


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug.lower() or "persona"


def resolve_path(path: Path) -> Path:
    expanded = path.expanduser()
    if expanded.is_absolute():
        return expanded
    return ROOT / expanded


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
