#!/usr/bin/env python3
"""Read-only maintenance auditor for LIRIA prompt/session hygiene."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


MAX_PROMPT_CHARS = 45_000
MAX_GENERATED_PROMPT_CHARS = 80_000
MAX_LITE_PROMPT_CHARS = 28_000
MAX_FAST_PROMPT_CHARS = 55_000
MAX_HOTSET_CHARS = 12_000
MAX_INDEX_CHARS = 28_000
OPTIONAL_HEAVY_PROMPT_FILES = {
    "prompt/manga_export.md",
    "prompt/story_reference.md",
    "prompt/visual_character_sheet.md",
}


@dataclass
class Finding:
    level: str
    path: Path
    message: str
    line: int | None = None

    def format(self, root: Path) -> str:
        rel = self.path.relative_to(root) if self.path.is_relative_to(root) else self.path
        where = f"{rel}:{self.line}" if self.line else str(rel)
        return f"{self.level}: {where}: {self.message}"


@dataclass
class PromptArray:
    name: str
    files: list[str]
    line: int


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def add(finding_list: list[Finding], level: str, path: Path, message: str, line: int | None = None) -> None:
    finding_list.append(Finding(level=level, path=path, message=message, line=line))


def markdown_files(base: Path) -> list[Path]:
    if not base.exists():
        return []
    if base.is_file():
        return [base] if base.suffix == ".md" else []
    return sorted(path for path in base.rglob("*.md") if path.is_file())


def parse_bash_prompt_arrays(config: Path) -> dict[str, PromptArray]:
    if not config.exists():
        return {}

    arrays: dict[str, PromptArray] = {}
    current_name: str | None = None
    current_line = 0
    current_files: list[str] = []
    assignment = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)=\(\s*(?:#.*)?$")

    for line_no, raw_line in enumerate(read_text(config).splitlines(), start=1):
        if current_name is None:
            match = assignment.match(raw_line)
            if not match:
                continue
            current_name = match.group(1)
            current_line = line_no
            current_files = []
            continue

        stripped = raw_line.strip()
        if stripped == ")" or stripped.startswith(")"):
            arrays[current_name] = PromptArray(name=current_name, files=current_files, line=current_line)
            current_name = None
            continue

        for double_quoted, single_quoted in re.findall(r'"([^"]+)"|'"'"'([^'"'"']+)'"'"'', raw_line):
            token = double_quoted or single_quoted
            expansion = re.fullmatch(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\[@\]\}", token)
            if expansion and expansion.group(1) in arrays:
                current_files.extend(arrays[expansion.group(1)].files)
            else:
                current_files.append(token)

    return arrays


def prompt_assembly_chars(root: Path, files: list[str]) -> tuple[int, list[str]]:
    total = 0
    missing: list[str] = []
    existing = 0
    for rel in files:
        path = root / rel
        if not path.exists():
            missing.append(rel)
            continue
        if existing:
            total += 2
        total += len(read_text(path).rstrip("\n"))
        existing += 1
    return total, missing


def scan_prompt_profiles(root: Path, findings: list[Finding]) -> None:
    config = root / "scenarios" / "liria" / "config.sh"
    arrays = parse_bash_prompt_arrays(config)
    profile_arrays = {
        "fast/new": arrays.get("LIRIA_FAST_NEW_SYSTEM_PROMPT_FILES"),
        "fast/resume": arrays.get("LIRIA_FAST_RESUME_SYSTEM_PROMPT_FILES"),
        "full/new": arrays.get("LIRIA_FULL_NEW_SYSTEM_PROMPT_FILES"),
        "full/resume": arrays.get("LIRIA_FULL_RESUME_SYSTEM_PROMPT_FILES"),
    }
    lite_arrays = {
        "lite/new": arrays.get("LIRIA_LITE_NEW_SYSTEM_PROMPT_FILES"),
        "lite/resume": arrays.get("LIRIA_LITE_RESUME_SYSTEM_PROMPT_FILES"),
    }
    if any(lite_arrays.values()):
        profile_arrays = {**lite_arrays, **profile_arrays}

    for profile, prompt_array in profile_arrays.items():
        if prompt_array is None:
            add(findings, "WARN", config, f"missing prompt array for {profile}")
            continue

        total_chars, missing = prompt_assembly_chars(root, prompt_array.files)
        heavy = sorted(set(prompt_array.files) & OPTIONAL_HEAVY_PROMPT_FILES)
        heavy_note = f"; optional heavy: {', '.join(heavy)}" if heavy else "; optional heavy: none"
        add(findings, "INFO", config, f"{profile} prompt assembly: {len(prompt_array.files)} file(s), {total_chars} chars{heavy_note}", prompt_array.line)

        for rel in missing:
            add(findings, "ERROR", config, f"{profile} prompt file is missing: {rel}", prompt_array.line)

        if (profile.startswith("fast/") or profile.startswith("lite/")) and heavy:
            add(
                findings,
                "ERROR",
                config,
                f"{profile} includes optional heavy prompt file(s): {', '.join(heavy)}; keep these out of lightweight profiles",
                prompt_array.line,
            )
        if profile.startswith("lite/") and total_chars > MAX_LITE_PROMPT_CHARS:
            add(findings, "WARN", config, f"{profile} is large for a lite prompt ({total_chars} chars > {MAX_LITE_PROMPT_CHARS})", prompt_array.line)
        elif profile.startswith("fast/") and total_chars > MAX_FAST_PROMPT_CHARS:
            add(findings, "WARN", config, f"{profile} generated prompt may be large ({total_chars} chars > {MAX_FAST_PROMPT_CHARS})", prompt_array.line)

    fast_resume = profile_arrays.get("fast/resume")
    full_resume = profile_arrays.get("full/resume")
    if fast_resume and full_resume:
        fast_chars, _ = prompt_assembly_chars(root, fast_resume.files)
        full_chars, _ = prompt_assembly_chars(root, full_resume.files)
        delta = full_chars - fast_chars
        add(findings, "INFO", config, f"resume profile delta: full is {delta} chars larger than fast")


def scan_generated_prompt_artifacts(root: Path, findings: list[Finding]) -> None:
    generated_files = [
        root / ".codex" / "generated" / "liria-new.instructions.md",
        root / ".codex" / "generated" / "liria-resume.instructions.md",
        root / ".claude" / "generated" / "liria-new.system-prompt.md",
        root / ".claude" / "generated" / "liria-resume.system-prompt.md",
    ]

    for path in generated_files:
        if not path.exists():
            continue
        text = read_text(path)
        size = len(text)
        add(findings, "INFO", path, f"generated prompt artifact size: {size} chars")
        if size > MAX_GENERATED_PROMPT_CHARS:
            add(findings, "WARN", path, f"generated prompt artifact is large ({size} chars > {MAX_GENERATED_PROMPT_CHARS})")
        lower = text.lower()
        if "liria prompt auditor" in lower or "liria_prompt_auditor" in lower:
            add(findings, "ERROR", path, "maintenance auditor text appears in generated prompt artifact")
        if re.search(r"\b(docs/maintenance_task_template\.md|docs/liria_prompt_auditor\.md|scripts/liria_prompt_auditor\.py)\b", text):
            add(findings, "ERROR", path, "maintenance-only file reference appears in generated prompt artifact")


def scan_prompt_bloat(root: Path, findings: list[Finding]) -> None:
    prompt_dir = root / "prompt"
    for path in markdown_files(prompt_dir):
        text = read_text(path)
        if len(text) > MAX_PROMPT_CHARS:
            add(findings, "WARN", path, f"large prompt file ({len(text)} chars); consider splitting or trimming repeated policy text")

        lower = text.lower()
        if "liria prompt auditor" in lower or "liria_prompt_auditor" in lower:
            add(findings, "ERROR", path, "maintenance auditor text appears in runtime prompt source")

        autosave_mentions = len(re.findall(r"auto\s*save|autosave|自動セーブ|生ログ|/compress", text, flags=re.I))
        if autosave_mentions > 18:
            add(findings, "WARN", path, f"many save/compress mentions ({autosave_mentions}); check for duplicated or conflicting save policy")


def scan_hard_numbered_choices(root: Path, findings: list[Finding]) -> None:
    numbered_choice = re.compile(
        r"(?ms)^[ \t]*1[.)、][^\n]{1,120}\n[ \t]*2[.)、][^\n]{1,120}\n[ \t]*3[.)、]"
    )
    allowed_context = re.compile(r"起動コマンド|Usage:|使い方|チェックリスト|手順|セットアップ|template", re.I)

    for path in markdown_files(root / "prompt"):
        text = read_text(path)
        for match in numbered_choice.finditer(text):
            window_start = max(0, match.start() - 240)
            window = text[window_start : match.end() + 240]
            if allowed_context.search(window):
                continue
            add(
                findings,
                "WARN",
                path,
                "possible hard numbered player choices; prefer natural options or diegetic prompts unless this is tooling",
                line_number(text, match.start()),
            )


def scan_autosave_contradictions(root: Path, findings: list[Finding]) -> None:
    candidates = markdown_files(root / "prompt") + markdown_files(root / "templates/session")
    cadence_pattern = re.compile(r"(10\s*シーン|十\s*シーン|毎ターン|毎回|after every turn|every turn|scene_tick|autosave_turn)", re.I)
    source_pattern = re.compile(
        r"(hotset[^\n]{0,80}(正本として扱|を正本|source of truth)|source of truth[^\n]{0,80}hotset)",
        re.I,
    )
    every_scene_command = re.compile(
        r"(毎\s*シーン|通常シーン終了時|scene\s*end|every\s+(?:normal\s+)?scene|after\s+every\s+scene)"
        r"[^\n]{0,120}"
        r"(autosave_turn(?:\.sh)?|scene_tick(?:\.sh)?|save_rawlog(?:\.sh)?|生ログ保存)",
        re.I,
    )
    every_scene_negation = re.compile(
        r"(しない|不要|使うな|実行するな|内部カウントのみ|10/10|10\s*シーン|到達時だけ|"
        r"do\s+not|don't|not\s+run|no\s+need|only\s+at|only\s+when)",
        re.I,
    )

    for path in candidates:
        text = read_text(path)
        lower = text.lower()
        has_lightweight_autosave_policy = re.search(
            r"毎シーン\s*`?autosave_turn|通常シーン終了時は内部カウントのみ|毎シーン補助コマンドを実行してテンポを落とすな",
            text,
        )
        if (
            ("autosave" in lower or "自動セーブ" in text)
            and "scene_tick" in lower
            and "autosave_turn" in lower
            and not has_lightweight_autosave_policy
        ):
            add(findings, "WARN", path, "mentions multiple autosave mechanisms; verify cadence and responsibility do not conflict")

        cadence_hits = {match.group(1).lower() for match in cadence_pattern.finditer(text)}
        if len(cadence_hits) >= 3 and not has_lightweight_autosave_policy:
            add(findings, "WARN", path, "multiple save cadence phrases found; check for autosave timing contradictions")

        match = source_pattern.search(text)
        if match:
            add(findings, "ERROR", path, "hotset appears described as source of truth; it should remain a compact resume cache", line_number(text, match.start()))

        for line_no, line in enumerate(text.splitlines(), start=1):
            if every_scene_command.search(line) and not every_scene_negation.search(line):
                add(
                    findings,
                    "ERROR",
                    path,
                    "autosave helper appears mandatory every scene; fast flow should count internally and run autosave_turn only at 10/10 or explicit save",
                    line_no,
                )


def scan_sidecar_mandatory_reads(root: Path, findings: list[Finding]) -> None:
    sidecar_term = re.compile(
        r"(sidecar|checkpoint(?:s)?|current/checkpoints|archive/checkpoints|"
        r"indexes/event_index\.md|event_index\.md|current/mechanics_card\.md|mechanics_card\.md)",
        re.I,
    )
    mandatory_read = re.compile(
        r"(必読|必ず読む|必ず読|毎回読む|毎回読|標準読込|標準読み込み|標準の正本|読み込み対象|"
        r"must\s+read|always\s+read|mandatory\s+read|required\s+read|required\s+context|standard\s+read)",
        re.I,
    )
    conditional_or_negative = re.compile(
        r"(ではない|入れるな|必要(?:が出た|時|な時|なら|に応じて)|時だけ|だけ読む|軽く読む|"
        r"optional|only\s+when|when\s+needed|as\s+needed|not\s+(?:a\s+)?(?:must|mandatory|required)|do\s+not)",
        re.I,
    )

    candidates = markdown_files(root / "prompt") + markdown_files(root / "templates/session")
    config = root / "scenarios" / "liria" / "config.sh"
    if config.exists():
        candidates.append(config)

    for path in candidates:
        lines = read_text(path).splitlines()
        for index, line in enumerate(lines):
            if not sidecar_term.search(line):
                continue
            start = max(0, index - 2)
            end = min(len(lines), index + 3)
            window = "\n".join(lines[start:end])
            if mandatory_read.search(window) and not conditional_or_negative.search(window):
                add(
                    findings,
                    "WARN",
                    path,
                    "sidecar/checkpoint file appears in mandatory read wording; keep these optional and need-driven for fast resume",
                    index + 1,
                )


def scan_hotset(path: Path, findings: list[Finding]) -> None:
    if not path.exists():
        add(findings, "WARN", path, "hotset.md is missing")
        return
    text = read_text(path)
    if len(text) > MAX_HOTSET_CHARS:
        add(findings, "WARN", path, f"hotset is large ({len(text)} chars); keep it as a compact resume cache")
    if re.search(r"正本\s*[:：]\s*(はい|yes)|hotset[^\n]{0,80}source of truth|archive|全文ログ|full log", text, flags=re.I):
        add(findings, "WARN", path, "hotset contains source-of-truth/archive language; verify it is only a resume cache")
    if not re.search(r"現在フェーズ|再開アンカー|resume anchor", text, flags=re.I):
        add(findings, "WARN", path, "hotset missing obvious resume anchors")


def scan_cast_index(session: Path, findings: list[Finding]) -> None:
    cast_index = session / "indexes" / "cast_index.md"
    if not cast_index.exists():
        add(findings, "WARN", cast_index, "cast_index.md is missing")
        return
    text = read_text(cast_index)
    if re.search(r"未命名|current\s*参照|gm current", text, flags=re.I):
        add(findings, "WARN", cast_index, "unresolved cast reference remains in index")
    if not re.search(r"優先して読む時|read priority|when to read", text, flags=re.I):
        add(findings, "WARN", cast_index, "missing read-priority guidance")

    npc_dir = session / "cast" / "npc"
    npc_cards = list(npc_dir.glob("*.md")) if npc_dir.exists() else []
    pressure_text = ""
    for rel in ("current/gm.md", "current/case.md", "current/hotset.md"):
        candidate = session / rel
        if candidate.exists():
            pressure_text += "\n" + read_text(candidate)
    if re.search(r"敵幹部|主要人物|上位存在|scene lead|回収員|現場調整|外部面談|organization contact", pressure_text, flags=re.I):
        if not [path for path in npc_cards if path.name != ".gitkeep"]:
            add(findings, "WARN", npc_dir, "active important NPC pressure found but no cast/npc/*.md cards exist")


def scan_event_index(session: Path, findings: list[Finding]) -> None:
    event_index = session / "indexes" / "event_index.md"
    if not event_index.exists():
        add(findings, "WARN", event_index, "event_index.md is missing")
        return
    text = read_text(event_index)
    if len(text) > MAX_INDEX_CHARS:
        add(findings, "WARN", event_index, f"event index is large ({len(text)} chars); consider archiving prose and keeping concise anchors")
    long_bullets = [(idx, line) for idx, line in enumerate(text.splitlines(), start=1) if re.match(r"\s*[-*]\s+", line) and len(line) > 260]
    if long_bullets:
        add(findings, "WARN", event_index, "long event-index bullet may be full prose instead of an anchor", long_bullets[0][0])
    if not re.search(r"event|出来事|事件|日付|anchor|scene", text, flags=re.I):
        add(findings, "WARN", event_index, "event index has no obvious event/date/anchor language")


def scan_session(session: Path, findings: list[Finding]) -> None:
    scan_hotset(session / "current" / "hotset.md", findings)
    scan_cast_index(session, findings)
    scan_event_index(session, findings)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only LIRIA prompt/session hygiene auditor.")
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    parser.add_argument("--session", help="optional session directory, e.g. saves/session_002")
    parser.add_argument("--fail-on-warning", action="store_true", help="exit 1 when warnings are present")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    if not (root / "play.sh").exists() or not (root / "prompt").exists():
        print(f"ERROR: {root} does not look like the LIRIA repo root", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    scan_prompt_profiles(root, findings)
    scan_generated_prompt_artifacts(root, findings)
    scan_prompt_bloat(root, findings)
    scan_hard_numbered_choices(root, findings)
    scan_autosave_contradictions(root, findings)
    scan_sidecar_mandatory_reads(root, findings)

    if args.session:
        session = Path(args.session)
        if not session.is_absolute():
            session = root / session
        session = session.resolve()
        if not session.exists() or not session.is_dir():
            print(f"ERROR: session path does not exist: {session}", file=sys.stderr)
            return 2
        scan_session(session, findings)
    else:
        scan_session(root / "templates" / "session", findings)

    for finding in findings:
        print(finding.format(root))

    errors = sum(1 for finding in findings if finding.level == "ERROR")
    warnings = sum(1 for finding in findings if finding.level == "WARN")
    infos = sum(1 for finding in findings if finding.level == "INFO")
    print(f"SUMMARY: {errors} error(s), {warnings} warning(s), {infos} info")

    if errors or (args.fail_on_warning and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
