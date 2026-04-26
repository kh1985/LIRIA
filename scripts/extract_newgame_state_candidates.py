#!/usr/bin/env python3
"""Generate reviewable normal-newgame state proposals from session logs.

By default this script is proposal-only. With --apply-safe, it can fill only
clearly uninitialized newgame state files after creating a checkpoint backup.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATTERNS = ("raw_*.log", "raw_*.md", "live_*.log", "live_*.md")
SUPPLEMENTAL_PATTERNS = (*SOURCE_PATTERNS, "autosave_watcher_*.log")
APPLY_TARGETS = (
    "design/initial_answers.md",
    "design/story_reference.md",
    "design/story_spine.md",
    "design/organization_cast.md",
    "current/player.md",
    "current/relationships.md",
    "current/case.md",
    "current/hotset.md",
)

ANSI_RE = re.compile(
    r"\x1b\[[0-?]*[ -/]*[@-~]"
    r"|\x1b\][^\x07]*(?:\x07|\x1b\\)"
    r"|\x1b[@-_]"
)
JAPANESE_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
USER_PROMPT_RE = re.compile(r"(?:^|\s)›\s*(.+)$")
WATCHER_INPUT_RE = re.compile(r"(?:tick from input|skip meta/input):\s*(.+)$")


@dataclass(frozen=True)
class SourceBundle:
    session_name: str
    session_path: Path
    primary_path: Path
    supplemental_paths: list[Path]


@dataclass(frozen=True)
class ExtractedState:
    user_inputs: list[str]
    answers: dict[str, list[str]]
    first_scene: list[str]
    assembly_notes: list[str]
    case_notes: list[str]
    appearance_notes: list[str]
    source_excerpt_notes: list[str]


@dataclass(frozen=True)
class ApplyResult:
    backup_path: Path | None
    changed: list[str]
    skipped: list[str]


def main() -> int:
    args = parse_args()
    bundle = resolve_sources(args.session, args.source_path or args.source)
    texts = {path: read_text(path) for path in bundle.supplemental_paths}
    primary_text = texts.get(bundle.primary_path, read_text(bundle.primary_path))

    extracted = extract_state(primary_text, texts)
    proposal = build_proposal(bundle, extracted)

    output_path = args.output or default_output_path(bundle.session_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(proposal, encoding="utf-8")

    apply_result: ApplyResult | None = None
    if args.apply_safe:
        apply_result = apply_safe(bundle, extracted)

    if args.stdout:
        print(proposal)
    print(f"wrote newgame state candidate proposal: {display_path(output_path)}")
    if apply_result is None:
        print("mode: proposal only; session state files were not modified")
    else:
        print("mode: safe apply")
        if apply_result.backup_path is not None:
            print(f"backup: {display_path(apply_result.backup_path)}")
        if apply_result.changed:
            print("changed files:")
            for rel_path in apply_result.changed:
                print(f"- {rel_path}")
        else:
            print("changed files: none")
        if apply_result.skipped:
            print("skipped files:")
            for item in apply_result.skipped:
                print(f"- {item}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract normal newgame Q&A and first-scene candidates into a reviewable proposal markdown.",
    )
    parser.add_argument("session", help="Session name, e.g. session_manual_story_test_002, or saves/<session> path.")
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        help="Optional raw_* or live_* source log. Defaults to the latest raw/live log for the session.",
    )
    parser.add_argument(
        "--source",
        dest="source_path",
        type=Path,
        help="Optional raw_* or live_* source log. Overrides the positional source.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional proposal output path. Defaults to saves/<session>/archive/logs/newgame_state_candidates_<timestamp>.md.",
    )
    parser.add_argument(
        "--apply-safe",
        action="store_true",
        help="After writing the proposal, fill only clearly uninitialized session state files. Existing human-edited content is not overwritten.",
    )
    parser.add_argument("--stdout", action="store_true", help="Also print the generated proposal to stdout.")
    return parser.parse_args()


def resolve_sources(session_arg: str, source_arg: Path | None) -> SourceBundle:
    session_path = Path(session_arg)
    if not session_path.parts or session_path.parts[0] != "saves":
        session_path = ROOT / "saves" / session_arg
    elif not session_path.is_absolute():
        session_path = ROOT / session_path
    session_path = session_path.resolve()

    if not session_path.is_dir():
        raise SystemExit(f"session directory not found: {display_path(session_path)}")

    logs_dir = session_path / "archive" / "logs"
    if not logs_dir.is_dir():
        raise SystemExit(f"session has no archive/logs directory: {display_path(logs_dir)}")

    primary_path = resolve_source_path(source_arg, logs_dir)
    supplemental_paths = collect_supplemental_paths(logs_dir, primary_path)

    return SourceBundle(
        session_name=session_path.name,
        session_path=session_path,
        primary_path=primary_path,
        supplemental_paths=supplemental_paths,
    )


def resolve_source_path(source_arg: Path | None, logs_dir: Path) -> Path:
    if source_arg:
        path = source_arg
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        if not path.is_file():
            raise SystemExit(f"source file not found: {display_path(path)}")
        return path

    candidates: list[Path] = []
    for pattern in SOURCE_PATTERNS:
        candidates.extend(logs_dir.glob(pattern))
    if not candidates:
        raise SystemExit(f"no raw/live logs found in {display_path(logs_dir)}")
    return latest_path(candidates)


def collect_supplemental_paths(logs_dir: Path, primary_path: Path) -> list[Path]:
    paths: list[Path] = []
    for pattern in SUPPLEMENTAL_PATTERNS:
        paths.extend(logs_dir.glob(pattern))
    unique = {path.resolve(): path.resolve() for path in paths}
    unique[primary_path.resolve()] = primary_path.resolve()
    return sorted(unique.values(), key=lambda path: (path.name, path.stat().st_mtime))


def latest_path(paths: list[Path]) -> Path:
    return max((path.resolve() for path in paths), key=lambda path: (path.stat().st_mtime, path.name))


def read_text(path: Path | None) -> str:
    if path is None:
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def extract_state(primary_text: str, texts: dict[Path, str]) -> ExtractedState:
    all_lines: list[str] = []
    watcher_inputs: list[str] = []
    transcript_inputs: list[str] = []
    source_excerpt_notes: list[str] = []

    for path, text in texts.items():
        cleaned = clean_transcript_text(text)
        lines = meaningful_lines(cleaned)
        all_lines.extend(lines)
        watcher_inputs.extend(collect_watcher_inputs(cleaned))
        if path.name.startswith(("raw_", "live_")):
            transcript_inputs.extend(collect_prompt_inputs(cleaned))
            source_excerpt_notes.append(f"scanned `{display_path(path)}`")

    primary_lines = meaningful_lines(clean_transcript_text(primary_text))
    first_scene = find_first_scene(primary_lines) or find_first_scene(all_lines)
    appearance_notes = extract_appearance_notes(all_lines)
    if watcher_inputs:
        user_inputs = [item for item in watcher_inputs if is_probable_player_answer(item)]
    else:
        user_inputs = collapse_adjacent_duplicates([item for item in transcript_inputs if is_probable_player_answer(item)])
    answers = assign_answers(user_inputs)
    case_notes = derive_case_notes(first_scene, answers)
    assembly_notes = derive_assembly_notes(answers, first_scene, case_notes)

    return ExtractedState(
        user_inputs=user_inputs,
        answers=answers,
        first_scene=first_scene,
        assembly_notes=assembly_notes,
        case_notes=case_notes,
        appearance_notes=appearance_notes,
        source_excerpt_notes=source_excerpt_notes,
    )


def clean_transcript_text(text: str) -> str:
    text = ANSI_RE.sub("", text)
    text = text.replace("\r", "\n").replace("\x07", "")
    text = "".join(ch if ch in "\n\t" or ord(ch) >= 32 else " " for ch in text)
    return text


def meaningful_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = normalize_space(raw_line)
        if not line:
            continue
        if is_terminal_noise(line):
            continue
        if JAPANESE_RE.search(line) or "Q1.5" in line or re.search(r"\bQ[0-6]\b", line) or "→" in line:
            lines.append(line)
    return collapse_repeated_lines(lines)


def is_terminal_noise(line: str) -> bool:
    lowered = line.lower()
    skip_fragments = (
        "openai codex",
        "token usage",
        "esc to interrupt",
        "use /skills",
        "gpt-5",
        "~/desktop/work",
        "booting mcp",
        "model changed",
        "find and fix a bug",
        "working",
        "thinking",
        "explored",
        "waiting for background",
        "python - <<",
        "if re.search",
        "for kw in",
        "kw ",
        "read autosave_watcher",
    )
    if any(fragment in lowered for fragment in skip_fragments):
        return True
    if line.startswith(("└", "│", "╭", "╰", ">", "› /", "• Model")):
        return True
    return False


def collect_watcher_inputs(text: str) -> list[str]:
    inputs: list[str] = []
    for raw_line in clean_transcript_text(text).splitlines():
        line = normalize_space(raw_line)
        if not line:
            continue

        watcher_input = WATCHER_INPUT_RE.search(line)
        if watcher_input:
            inputs.append(sanitize_user_input(watcher_input.group(1)))
    return inputs


def collect_prompt_inputs(text: str) -> list[str]:
    inputs: list[str] = []
    for raw_line in clean_transcript_text(text).splitlines():
        line = normalize_space(raw_line)
        if not line:
            continue
        prompt = USER_PROMPT_RE.search(line)
        if prompt:
            inputs.append(sanitize_user_input(prompt.group(1)))
    return inputs


def sanitize_user_input(text: str) -> str:
    value = normalize_space(text)
    value = re.sub(r"\btab to queue message\b.*$", "", value, flags=re.IGNORECASE).strip()
    value = re.sub(r"\b\d+% context left\b.*$", "", value, flags=re.IGNORECASE).strip()
    return value


def is_probable_player_answer(text: str) -> bool:
    value = normalize_space(text).strip("。")
    if not value:
        return False
    lowered = value.lower()
    skip_fragments = (
        "liria.md のルール",
        "今回の session",
        "saves/",
        "launcher",
        "標準保存先",
        "repo root",
        "session 直下",
        "use /skills",
        "/model",
        "model changed",
        "find and fix",
        "python ",
        "bash ",
        "sed -n",
        "rg ",
        "tail -n",
    )
    if any(fragment in lowered for fragment in skip_fragments):
        return False
    if lowered in {"q", "quit", "exit"}:
        return False
    if value.startswith(("/", "•", "└")):
        return False
    if re.match(r"^\(?\s*gm(?:\s|$)", lowered):
        return False
    if len(value) > 180 and "新しいゲーム" not in value:
        return False
    return JAPANESE_RE.search(value) is not None


def assign_answers(inputs: list[str]) -> dict[str, list[str]]:
    answers: dict[str, list[str]] = {
        "Q0": [],
        "Q1": [],
        "Q1.5": [],
        "Q2": [],
        "Q3": [],
        "Q4": [],
        "Q5": [],
        "Q6": [],
        "Optional Avoid Notes": [],
        "Post-Q&A Inputs": [],
    }

    # Normal newgame currently asks Q0, Q1, Q1.5, Q2 sub-questions,
    # Q3 plus constraint follow-ups, then Q4-Q6 and optional avoid notes.
    mapping = [
        ("Q0", 1),
        ("Q1", 1),
        ("Q1.5", 1),
        ("Q2", 4),
        ("Q3", 3),
        ("Q4", 1),
        ("Q5", 1),
        ("Q6", 1),
        ("Optional Avoid Notes", 1),
    ]
    cursor = 0
    for key, count in mapping:
        for _ in range(count):
            if cursor >= len(inputs):
                break
            answers[key].append(inputs[cursor])
            cursor += 1
    if cursor < len(inputs):
        answers["Post-Q&A Inputs"].extend(inputs[cursor:])
    return answers


def extract_appearance_notes(lines: list[str]) -> list[str]:
    wanted = ("身長", "体型", "基本服装", "髪型", "顔つき", "雰囲気")
    notes: list[str] = []
    for line in lines:
        stripped = line.lstrip("- ")
        if any(stripped.startswith(f"{key}：") or stripped.startswith(f"{key}:") for key in wanted):
            notes.append(stripped)
    return unique_preserving_order(notes)[:8]


def find_first_scene(lines: list[str]) -> list[str]:
    for index, line in enumerate(lines):
        if "→" not in line or "どうする" not in line:
            continue
        start = max(0, index - 28)
        end = min(len(lines), index + 6)
        block = trim_scene_block(lines[start:end])
        if looks_like_scene_block(block):
            return block
    return []


def trim_scene_block(block: list[str]) -> list[str]:
    scene_start_signals = (
        "代々木",
        "事務所",
        "机の上",
        "向かいには",
        "彼女",
        "志乃崎",
        "封筒",
        "聞けたこと",
        "昨夜",
    )
    for index, line in enumerate(block):
        if any(signal in line for signal in scene_start_signals):
            return block[index:]
    return block


def looks_like_scene_block(block: list[str]) -> bool:
    joined = "\n".join(block)
    if "Q1" in joined or "Q2" in joined or "Q3" in joined:
        return False
    scene_signals = ("封筒", "写真", "鍵", "相談", "依頼", "事務所", "机", "相手", "彼女", "志乃崎")
    return sum(1 for signal in scene_signals if signal in joined) >= 2


def derive_case_notes(first_scene: list[str], answers: dict[str, list[str]]) -> list[str]:
    joined = "\n".join(first_scene)
    q6 = first_value(answers, "Q6")
    notes = [
        f"title: {derive_case_title(joined, q6)}",
        "phase: intake / first contact",
        f"visible problem: {derive_visible_problem(joined, q6)}",
        f"visible request: {derive_visible_request(joined, q6)}",
        f"short goal: {derive_short_goal(joined)}",
        f"handles: {derive_handles(joined)}",
        f"progress condition: {derive_progress_condition(joined)}",
        f"if ignored: {derive_if_ignored(joined)}",
        f"next visible change: {derive_next_visible_change(joined)}",
        f"relationship stake: {derive_relationship_stake(joined)}",
    ]
    return notes


def derive_case_title(scene: str, q6: str) -> str:
    if "封筒" in scene and "鍵" in scene:
        return f"{scene_person_name(scene)}の部屋に届いた封筒と合鍵"
    if q6:
        return q6
    return "TODO: first visible disturbance"


def derive_visible_problem(scene: str, q6: str) -> str:
    if "部屋" in scene and "写真" in scene and "鍵" in scene:
        return "依頼人の部屋の中を撮った写真と、本人のものに見える合鍵が封筒で届いた。"
    if "部屋" in scene and "鍵" in scene and "管理会社" in scene:
        return "店の常連が部屋に戻らず、最後に残した鍵と管理会社の連絡票が相談者の前にある。"
    return q6 or "TODO: visible problem from first scene"


def derive_visible_request(scene: str, q6: str) -> str:
    if "管理会社" in scene:
        return "大ごとにする前に、封筒・写真・鍵・出入りの異常を確認してほしい。"
    if q6:
        return "言いにくい相談を聞き、最初に触れる人・物・場所を確認する。"
    return "TODO: visible request"


def derive_short_goal(scene: str) -> str:
    if "封筒" in scene and "鍵" in scene:
        return "封筒の中身、鍵の同一性、部屋への侵入経路、管理会社へ言う前の確認点を絞る。"
    return "TODO: short goal"


def derive_handles(scene: str) -> str:
    handles: list[str] = []
    person_name = scene_person_name(scene)
    if person_name != "相談者":
        handles.append(f"person: {person_name}")
    if "封筒" in scene:
        handles.append("object: 白い封筒")
    if "写真" in scene:
        handles.append("record: 部屋の奥の棚を撮った写真")
    if "鍵" in scene:
        handles.append("object: 合鍵 / 元の鍵")
    if "部屋" in scene or "アパート" in scene:
        handles.append("place: 二階の外廊下つきアパート")
    if "管理会社" in scene:
        handles.append("record: 管理会社の合鍵管理")
    return "; ".join(handles) if handles else "TODO: person/object/place/record handles"


def derive_progress_condition(scene: str) -> str:
    if "封筒" in scene:
        return "封筒・写真・鍵を確認し、誰がいつ部屋へ入れたかの候補を最低1つ具体化する。"
    return "TODO: progress condition"


def derive_if_ignored(scene: str) -> str:
    if "部屋" in scene:
        return "侵入者または鍵の複製者が再度接触し、依頼人の生活圏と信用がさらに揺れる。"
    return "TODO: if ignored"


def derive_next_visible_change(scene: str) -> str:
    if "ここで見ますか" in scene or "封筒" in scene:
        return "封筒を開けるか、聞き込みの段取りを立てるかを選ぶ場面。"
    return "TODO: next visible change"


def derive_relationship_stake(scene: str) -> str:
    person_name = scene_person_name(scene)
    if person_name != "相談者":
        return f"{person_name}が勘違いで済ませたい恐怖を、主人公がどこまで真面目に受け取るか。"
    return "TODO: relationship stake"


def scene_person_name(scene: str) -> str:
    for name in ("篠宮", "志乃崎"):
        if name in scene:
            return name
    return "相談者"


def derive_assembly_notes(
    answers: dict[str, list[str]],
    first_scene: list[str],
    case_notes: list[str],
) -> list[str]:
    q1 = first_value(answers, "Q1")
    q2 = "; ".join(answers.get("Q2", []))
    q3 = "; ".join(answers.get("Q3", []))
    q4 = first_value(answers, "Q4")
    q5 = first_value(answers, "Q5")
    q6 = first_value(answers, "Q6")
    scene = "\n".join(first_scene)

    notes = [
        f"life / base: {q1 or 'TODO'}",
        f"inner: {q2 or 'TODO'}",
        f"ability / rule: {q3 or 'TODO'}",
        f"romance / heroine bias: {q4 or 'TODO'}",
        f"initial relationship surface: {q5 or 'TODO'}",
        f"first disturbance: {q6 or 'TODO'}",
    ]
    if "封筒" in scene and "鍵" in scene:
        notes.extend(
            [
                "selection signal: private room / duplicate key / photograph / apartment management record",
                "session-derived engine: everyday service work meets impossible access to private space",
                "organization pressure: local / record / management-company contact surface",
            ]
        )
    notes.extend(case_notes[:4])
    return notes


def build_proposal(bundle: SourceBundle, state: ExtractedState) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = [
        "# Normal Newgame State Candidate Proposal",
        "",
        "## Summary",
        "",
        f"- session: `{bundle.session_name}`",
        f"- generated at: {now}",
        f"- primary source: `{display_path(bundle.primary_path)}`",
        "- source priority: latest raw/live log, with same-session raw/live/autosave watcher logs used as recovery hints",
        "- mode: proposal only",
        "- files changed by this script: this proposal markdown only",
        "- files intentionally not modified: `current/*`, `design/*`, `cast/*`, `indexes/*`",
        "",
        "## Review Rule",
        "",
        "Do not paste this whole file blindly. Review each block, then manually apply only the pieces that match the actual session state.",
        "",
        "## Source Excerpts",
        "",
        "### Scanned Sources",
        "",
        format_items(state.source_excerpt_notes, empty="- No supplemental source list was built."),
        "",
        "### Q0-Q6 / Q1.5 / Optional Avoid Notes",
        "",
        format_answer_dump(state.answers, state.appearance_notes),
        "",
        "### First Scene Candidate",
        "",
        fenced_markdown(format_items(state.first_scene, empty="- TODO: first scene not found in raw/live logs.")),
        "",
        "### Initial Story Assembly Candidates",
        "",
        format_items(state.assembly_notes, empty="- TODO: Initial Story Assembly candidates not found."),
        "",
        "### current/case.md Candidates",
        "",
        format_items(state.case_notes, empty="- TODO: active case candidates not found."),
        "",
        "## Proposed Updates",
        "",
        "### design/initial_answers.md",
        "",
        "<!-- liria-apply-target: design/initial_answers.md -->",
        format_initial_answers(state),
        "",
        "### design/story_reference.md",
        "",
        "<!-- liria-apply-target: design/story_reference.md -->",
        format_story_reference(state),
        "",
        "### design/story_spine.md",
        "",
        "<!-- liria-apply-target: design/story_spine.md -->",
        format_story_spine(state),
        "",
        "### design/organization_cast.md",
        "",
        "<!-- liria-apply-target: design/organization_cast.md -->",
        format_organization_cast(state),
        "",
        "### current/player.md",
        "",
        "<!-- liria-apply-target: current/player.md -->",
        format_player(state),
        "",
        "### current/gm.md",
        "",
        format_gm(state),
        "",
        "### current/relationships.md",
        "",
        "<!-- liria-apply-target: current/relationships.md -->",
        format_relationships(state),
        "",
        "### current/case.md",
        "",
        "<!-- liria-apply-target: current/case.md -->",
        format_case(state),
        "",
        "### current/hotset.md",
        "",
        "<!-- liria-apply-target: current/hotset.md -->",
        format_hotset(state),
        "",
        "## Manual Apply Checklist",
        "",
        "- [ ] Compare this proposal with current session files before editing.",
        "- [ ] Save Q0-Q6 / Q1.5 / Optional Avoid Notes raw answers in `design/initial_answers.md`.",
        "- [ ] Apply only the selected story reference / spine / organization cast candidates.",
        "- [ ] Update `current/case.md` before resuming from the first scene.",
        "- [ ] Keep `current/hotset.md` short; do not use it as the only source of truth.",
        f"- [ ] Run `bash scripts/check_session_integrity.sh {bundle.session_name}` after manual application.",
        "",
    ]
    return "\n".join(lines)


def format_answer_dump(answers: dict[str, list[str]], appearance_notes: list[str]) -> str:
    lines: list[str] = []
    for key in ("Q0", "Q1", "Q1.5", "Q2", "Q3", "Q4", "Q5", "Q6", "Optional Avoid Notes"):
        lines.append(f"#### {key}")
        lines.append("")
        lines.append(format_items(answers.get(key, []), empty="- TODO: not found in logs."))
        if key == "Q1.5" and appearance_notes:
            lines.append("")
            lines.append("GM appearance completion candidates:")
            lines.append(format_items(appearance_notes, empty="- TODO"))
        lines.append("")
    return "\n".join(lines).strip()


def format_initial_answers(state: ExtractedState) -> str:
    answers = state.answers
    lines = [
        "```markdown",
        "# Initial Answers",
        "",
        "## Q0: World Premise",
        f"- raw answer: {first_value(answers, 'Q0') or 'TODO'}",
        "- GM interpretation: 現代＋能力者。能力者や説明不能な違和感は、関係者の間では半ば公然。",
        "",
        "## Q1: Life Base",
        f"- raw answer: {first_value(answers, 'Q1') or 'TODO'}",
        "",
        "## Q1.5: Appearance Profile",
        f"- raw answer: {first_value(answers, 'Q1.5') or 'TODO'}",
        format_items(state.appearance_notes, empty="- GM completion: TODO"),
        "",
        "## Q2: Inner",
        format_items(answers.get("Q2", []), empty="- TODO"),
        "",
        "## Q3: Ability / Action Point",
        format_items(answers.get("Q3", []), empty="- TODO"),
        "",
        "## Q4: Romance Preference",
        f"- raw answer: {first_value(answers, 'Q4') or 'TODO'}",
        "",
        "## Q5: Initial Heroine / Initial Relationship",
        f"- raw answer: {first_value(answers, 'Q5') or 'TODO'}",
        "",
        "## Q6: First Daily Disturbance",
        f"- raw answer: {first_value(answers, 'Q6') or 'TODO'}",
        "",
        "## Optional Avoid Notes",
        format_items(answers.get("Optional Avoid Notes", []), empty="- none found / TODO"),
        "",
        "## Generated Seeds",
        format_items(state.assembly_notes, empty="- TODO"),
        "```",
    ]
    return "\n".join(lines)


def format_story_reference(state: ExtractedState) -> str:
    return "\n".join(
        [
            "```markdown",
            "## Light Story Reference Pass",
            "",
            "### Selection Signals",
            format_items(state.assembly_notes[:9], empty="- TODO"),
            "",
            "### Selected Reference Engines",
            "- engine: session-derived everyday-private-space intrusion",
            "  - source type: session-derived",
            "  - matched signals: 便利屋 / 人が集まるもの / 部屋の写真 / 合鍵 / 管理会社記録",
            "  - role: pressure / place / record / relationship",
            "  - LIRIA conversion: 日常の依頼から、生活圏・記録・鍵管理に食い込む違和感へ変換する。",
            "  - avoid direct imitation: 固有作品名、名場面、台詞を持ち込まない。",
            "",
            "### Candidate Shortlist",
            "- candidate: session-derived everyday-private-space intrusion",
            "  - source type: session-derived",
            "  - matched signals: private room / duplicate key / photograph / management record",
            "  - considered as: pressure / place / record / relationship",
            "  - why considered: 初回シーンの具体物と制度窓口が一致する。",
            "  - selected: yes",
            "  - rejection reason:",
            "  - copy-risk: low",
            "",
            "### Conversion Notes",
            "- 現代社会への変換: アパート、郵便受け、管理会社、合鍵管理。",
            "- 生活導線への変換: 代々木の便利屋事務所へ持ち込まれた言いにくい相談。",
            "- 恋愛/ヒロインへの変換: 相談者の恐怖と信用を、距離感の近い関係熱へつなげる余地。",
            "- 能力/作用点への変換: 岩のような硬化は、守る・受ける・侵入現場で耐える場面に効く。",
            "- 関係組織への変換: 管理会社、鍵管理、近隣、建物の出入り記録。",
            "```",
        ]
    )


def format_story_spine(state: ExtractedState) -> str:
    title = value_after_prefix(state.case_notes, "title") or "TODO"
    candidate = candidate_label(state)
    return "\n".join(
        [
            "```markdown",
            "## Main Question",
            "",
            "- この話が主人公とヒロインに問うこと: 勘違いで済ませたい小さな恐怖を、誰かの生活を守る仕事としてどこまで引き受けるか。",
            "",
            "## Reveal Ladder",
            "",
            f"1. visible first sign: {title}",
            "2. first concrete lead: 封筒、写真、合鍵、元の鍵、郵便受け。",
            "3. organization / pressure becomes clearer: 管理会社または鍵管理の記録に不整合が出る。",
            "4. heroine tie becomes unavoidable: 相談者の生活圏と信用が直接揺れる。",
            "5. late-stage truth or choice seed: 誰の安全を優先し、どこまで大ごとにするかを選ぶ。",
            "",
            "## Pressure Direction",
            "",
            f"- if ignored: {value_after_prefix(state.case_notes, 'if ignored') or 'TODO'}",
            f"- next visible move: {value_after_prefix(state.case_notes, 'next visible change') or 'TODO'}",
            "- who acts: 相談者、主人公、管理会社または近隣の接触面。",
            "- what changes in life/work/relationship: 便利屋としての信用と、相談者との信頼距離。",
            "",
            "## Heroine Tie",
            "",
            f"- heroine / candidate: {candidate}",
            f"  - life stake: {value_after_prefix(state.case_notes, 'relationship stake') or 'TODO'}",
            "  - emotional stake: 勘違いで済んでほしい恐怖を他人に預ける。",
            "  - how she can act autonomously: 封筒、写真、鍵、管理会社への連絡可否を自分で選ぶ。",
            "```",
        ]
    )


def format_organization_cast(state: ExtractedState) -> str:
    return "\n".join(
        [
            "```markdown",
            "## Organization Cast Summary",
            "",
            "- organization: 管理会社 / 建物管理 / 鍵管理に関わる窓口",
            "- pressure scale: local / record",
            "- posture: まだ未接触。大ごとにすると生活と信用へ波及する。",
            "- contact surface: 管理会社、近隣、郵便受け、合鍵管理記録",
            "",
            "## Major Figures",
            "",
            "### 管理会社の窓口担当",
            "",
            "- status: seed",
            "- role in organization: 合鍵・入退去・苦情窓口の一次対応",
            "- public face: 事務的で、記録上の正しさを優先する",
            "- contradiction: 大ごとにしたくない依頼人と、記録を残したい手続きの間に立つ",
            "- pressure method: 報告書、確認電話、管理規約、鍵交換の手続き",
            "- knows: TODO",
            "- suspects: TODO",
            "- unknown: TODO",
            "",
            "### 建物の近隣接触者",
            "",
            "- status: seed",
            "- role in organization: 組織ではなく生活圏の証言窓口",
            "- public face: 外廊下や郵便受けの変化を見ている可能性",
            "- pressure method: 噂、目撃、余計な親切、沈黙",
            "- knows: TODO",
            "- suspects: TODO",
            "- unknown: TODO",
            "```",
        ]
    )


def format_player(state: ExtractedState) -> str:
    return "\n".join(
        [
            "```markdown",
            "## Profile",
            f"- 生活基盤: {first_value(state.answers, 'Q1') or 'TODO'}",
            "",
            "## Appearance Profile",
            format_items(state.appearance_notes, empty="- TODO: Q1.5 appearance completion not found."),
            "",
            "## Visual Character Sheet",
            "- model sheet status: none",
            "- current appearance lock: Q1.5 appearance profile",
            "- image prompt anchor: （prompt-ready 以上の時だけ）",
            "- generated asset references: （image-generated の時だけ）",
            "",
            "## Inner",
            format_items(state.answers.get("Q2", []), empty="- TODO"),
            "",
            "## Ability Constraint Profile",
            format_items(state.answers.get("Q3", []), empty="- TODO"),
            "- output scale: TODO",
            "- trigger condition: TODO",
            "- range / target: TODO",
            "- uses / cooldown: TODO",
            "- cost: TODO",
            "- trace: TODO",
            "- collateral: TODO",
            "- social risk: TODO",
            "- relationship risk: TODO",
            "- escalation rule: TODO",
            "",
            "## Ability Runtime",
            "- 能力使用残回数: TODO",
            "- cooldown: TODO",
            "- 直近の使用痕跡: TODO",
            "",
            "## Life Base",
            f"- 拠点/仕事/生活: {first_value(state.answers, 'Q1') or 'TODO'}",
            "",
            "## Work Profile",
            f"- 仕事/収入: {first_value(state.answers, 'Q1') or 'TODO'}",
            "",
            "## Equipment / Tools",
            "- 名称: 初期装備 / 日常道具",
            "  - 行動選択肢: 調査、連絡、移動、聞き込み",
            "  - リスク: 生活圏と信用に波及する",
            "  - 痕跡: 連絡履歴、訪問記録、聞き込み相手",
            "  - 関係リスク: 相談者の信頼を損ねる可能性",
            "",
            "## Current Status",
            "- 現在フェーズ: 初回相談 / first contact",
            "",
            "## Current Hooks",
            f"- {value_after_prefix(state.case_notes, 'title') or 'TODO'}",
            "```",
        ]
    )


def format_gm(state: ExtractedState) -> str:
    return "\n".join(
        [
            "```markdown",
            "## World Seed",
            f"- Q0 raw answer: {first_value(state.answers, 'Q0') or 'TODO'}",
            "",
            "## First Daily Disturbance",
            f"- Q6 raw answer: {first_value(state.answers, 'Q6') or 'TODO'}",
            "",
            "## Incident Seeds",
            format_items(state.assembly_notes, empty="- TODO"),
            "",
            "## 現在のフック / Active Hooks",
            f"- 1: {value_after_prefix(state.case_notes, 'title') or 'TODO'}",
            "  - case_id: first_case",
            "",
            "## 自動セーブ管理 / Autosave Counter",
            "- Q&A / setup / gm相談は通常シーンに数えない。",
            "- 前回保存からのシーン数: review-current-value",
            "```",
        ]
    )


def format_relationships(state: ExtractedState) -> str:
    candidate = candidate_label(state)
    return "\n".join(
        [
            "```markdown",
            "## Romance Preferences",
            f"- raw answer: {first_value(state.answers, 'Q4') or 'TODO'}",
            "",
            "## Heroine Generation Bias",
            f"- initial relation preference: {first_value(state.answers, 'Q5') or 'TODO'}",
            "",
            "## Active Heroines",
            f"- 名前: {candidate}",
            "  - bond: TODO",
            "  - AFFINITY: TODO",
            f"  - 現在の関係フック: {value_after_prefix(state.case_notes, 'relationship stake') or 'TODO'}",
            "  - Heroine Crisis Role: civilian / wildcard",
            "```",
        ]
    )


def format_case(state: ExtractedState) -> str:
    handles = split_handles(value_after_prefix(state.case_notes, "handles"))
    non_handle_notes = [item for item in state.case_notes if not item.startswith("handles:")]
    lines = [
        "```markdown",
        "## Active Case",
        "- id: first_case",
        *[f"- {item}" for item in non_handle_notes],
        "- handles:",
    ]
    lines.extend(f"  - {handle}" for handle in handles)
    lines.append("```")
    return "\n".join(lines)


def split_handles(handles: str) -> list[str]:
    values = [part.strip() for part in handles.split(";") if part.strip()]
    return values or ["TODO: person/object/place/record handles"]


def format_hotset(state: ExtractedState) -> str:
    return "\n".join(
        [
            "```markdown",
            "## 現在の背骨",
            "- 現在フェーズ: 初回相談 / first contact",
            f"- 再開アンカー: {value_after_prefix(state.case_notes, 'next visible change') or 'TODO'}",
            f"- 能力と身体: {'; '.join(state.answers.get('Q3', [])) or 'TODO'}",
            f"- 現在の事業 / 世界 / 生活状況: {first_value(state.answers, 'Q1') or 'TODO'}",
            "",
            "## Active Case 抜粋",
            "- case_id: first_case",
            f"- short goal: {value_after_prefix(state.case_notes, 'short goal') or 'TODO'}",
            f"- handles: {value_after_prefix(state.case_notes, 'handles') or 'TODO'}",
            f"- if ignored: {value_after_prefix(state.case_notes, 'if ignored') or 'TODO'}",
            f"- next visible change: {value_after_prefix(state.case_notes, 'next visible change') or 'TODO'}",
            "```",
        ]
    )


def build_apply_blocks(state: ExtractedState) -> dict[str, str]:
    return {
        "design/initial_answers.md": strip_fenced_markdown(format_initial_answers(state)),
        "design/story_reference.md": strip_fenced_markdown(format_story_reference(state)),
        "design/story_spine.md": strip_fenced_markdown(format_story_spine(state)),
        "design/organization_cast.md": strip_fenced_markdown(format_organization_cast(state)),
        "current/player.md": strip_fenced_markdown(format_player(state)),
        "current/relationships.md": strip_fenced_markdown(format_relationships(state)),
        "current/case.md": strip_fenced_markdown(format_case(state)),
        "current/hotset.md": strip_fenced_markdown(format_hotset(state)),
    }


def strip_fenced_markdown(text: str) -> str:
    lines = text.splitlines()
    if len(lines) >= 2 and lines[0].strip() == "```markdown" and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1]).strip() + "\n"
    return text.strip() + "\n"


def apply_safe(bundle: SourceBundle, state: ExtractedState) -> ApplyResult:
    blocks = build_apply_blocks(state)
    changed: list[str] = []
    skipped: list[str] = []
    backup_path: Path | None = None

    for rel_path in APPLY_TARGETS:
        target = bundle.session_path / rel_path
        current_text = read_text(target) if target.exists() else ""
        if has_meaningful_state(rel_path, current_text):
            skipped.append(f"{rel_path} (already has state)")
            continue

        if not block_has_applyable_state(rel_path, blocks[rel_path]):
            skipped.append(f"{rel_path} (proposal block is too incomplete)")
            continue

        if backup_path is None:
            backup_path = create_backup_dir(bundle.session_path)

        if target.exists():
            backup_file = backup_path / rel_path
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup_file)

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(blocks[rel_path], encoding="utf-8")
        changed.append(rel_path)

    if backup_path is not None:
        write_apply_manifest(backup_path, changed, skipped)

    return ApplyResult(backup_path=backup_path, changed=changed, skipped=skipped)


def create_backup_dir(session_path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    checkpoints = session_path / "archive" / "checkpoints"
    base_name = f"pre_newgame_apply_{timestamp}"
    for index in range(100):
        suffix = "" if index == 0 else f"_{index:02d}"
        backup_dir = checkpoints / f"{base_name}{suffix}"
        if not backup_dir.exists():
            backup_dir.mkdir(parents=True)
            return backup_dir
    raise SystemExit(f"could not create unique backup directory under {display_path(checkpoints)}")


def write_apply_manifest(backup_path: Path, changed: list[str], skipped: list[str]) -> None:
    lines = [
        "# pre_newgame_apply backup",
        "",
        "## Changed Files",
        "",
        format_items(changed, empty="- none"),
        "",
        "## Skipped Files",
        "",
        format_items(skipped, empty="- none"),
        "",
    ]
    (backup_path / "MANIFEST.md").write_text("\n".join(lines), encoding="utf-8")


def has_meaningful_state(rel_path: str, text: str) -> bool:
    if not text.strip():
        return False

    keys_by_path = {
        "design/initial_answers.md": ("raw answer", "visible request", "organization pressure scale", "minimal story spine"),
        "design/story_reference.md": ("matched signals", "LIRIA conversion", "現代社会への変換", "selected"),
        "design/story_spine.md": ("この話が主人公とヒロインに問うこと", "visible first sign", "if ignored", "next visible move"),
        "design/organization_cast.md": ("organization", "pressure scale", "role in organization", "public face", "pressure method"),
        "current/player.md": ("身長", "体型", "基本服装", "current appearance lock", "概要", "拠点/仕事/生活"),
        "current/relationships.md": ("raw answer", "initial relation preference", "現在の関係フック", "AFFINITY"),
        "current/case.md": ("title", "visible problem", "visible request", "short goal", "progress condition", "if ignored", "next visible change"),
        "current/hotset.md": ("現在フェーズ", "再開アンカー", "short goal", "next visible change"),
    }
    return any(has_filled_key(text, key) for key in keys_by_path.get(rel_path, ()))


def block_has_applyable_state(rel_path: str, text: str) -> bool:
    return has_meaningful_state(rel_path, text)


def has_filled_key(text: str, key: str) -> bool:
    key_pattern = r"[ \t]+".join(re.escape(part) for part in key.split())
    pattern = re.compile(rf"^[ \t>-]*(?:[-*][ \t]*)?{key_pattern}[ \t]*[:：][ \t]*(.*)$", re.MULTILINE)
    for match in pattern.finditer(text):
        if is_meaningful_value(match.group(1)):
            return True
    return False


def is_meaningful_value(value: str) -> bool:
    normalized = normalize_space(value).strip("`*_")
    if not normalized:
        return False
    lowered = normalized.lower()
    placeholders = {
        "todo",
        "tbd",
        "none",
        "none found / todo",
        "review-current-value",
        "yes/no",
        "optional internal audit only",
        "seed | active | promoted to cast/npc | archived",
        "frontline / support / civilian / wildcard",
        "default stock / story_media_stock / user hint / session-derived",
        "romance / pressure / texture / rule / place / inner",
    }
    if lowered in placeholders:
        return False
    if lowered.startswith("todo:"):
        return False
    if normalized in {"なし", "未定", "いいえ", "（prompt-ready 以上の時だけ）", "（image-generated の時だけ）"}:
        return False
    if "|" in normalized and " / " in normalized:
        return False
    return True


def default_output_path(session_path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return session_path / "archive" / "logs" / f"newgame_state_candidates_{timestamp}.md"


def format_items(items: list[str], *, empty: str) -> str:
    if not items:
        return empty
    return "\n".join(f"- {item}" for item in items)


def fenced_markdown(text: str) -> str:
    return "\n".join(["```markdown", text, "```"])


def first_value(answers: dict[str, list[str]], key: str) -> str:
    values = answers.get(key, [])
    return values[0] if values else ""


def value_after_prefix(items: list[str], prefix: str) -> str:
    needle = prefix + ":"
    for item in items:
        if item.startswith(needle):
            return item[len(needle) :].strip()
    return ""


def candidate_label(state: ExtractedState) -> str:
    title = value_after_prefix(state.case_notes, "title")
    match = re.match(r"([^の]+)の", title)
    if match:
        return match.group(1)
    return "first相談者"


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def collapse_repeated_lines(lines: list[str]) -> list[str]:
    result: list[str] = []
    previous = ""
    for line in lines:
        if line == previous:
            continue
        result.append(line)
        previous = line
    return result


def collapse_adjacent_duplicates(items: list[str]) -> list[str]:
    result: list[str] = []
    previous = ""
    for item in items:
        normalized = normalize_space(item)
        if not normalized or normalized == previous:
            continue
        result.append(normalized)
        previous = normalized
    return result


def unique_preserving_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = normalize_space(item)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def display_path(path: Path) -> str:
    try:
        resolved = path.resolve()
    except OSError:
        resolved = path
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
