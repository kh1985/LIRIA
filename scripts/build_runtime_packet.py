#!/usr/bin/env python3
"""Build a compact runtime packet from an existing LIRIA session directory.

The script is intentionally read-only and dependency-free. It prefers the
layout documented by templates/session, while accepting sparse or partially
missing sessions without failing.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable


MISSING = "(missing)"
PLACEHOLDERS = {
    "",
    "-",
    "TBD",
    "TODO",
    "N/A",
    "n/a",
    "none",
    "None",
    "null",
    "__SESSION_NAME__",
    "__SCENARIO_ID__",
    "__CREATED_AT__",
    "未定",
    "なし",
    "seed | active | paused | merging | retiring | closed",
    "active | recurring | archived",
    "proposed | selected | packaged | queued | generating | generated | failed",
    "named one-shot | recurring contact | dossier candidate",
}

DEFAULT_READ_PRIORITIES = [
    "`current/hotset.md`",
    "`current/case.md`",
    "`current/gm.md`, `current/player.md`, `current/relationships.md` focused excerpts; legacy `current/harem.md` is read-only fallback",
    "`indexes/cast_index.md`",
    "Relevant `cast/heroine/*.md` and `cast/npc/*.md`",
    "`indexes/decision_index.md`",
    "`current/mechanics_card.md` when rules matter",
    "`indexes/event_index.md` when archived detail matters",
    "Relevant `design/*.md`",
    "Only selected files from `archive/*`",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a compact markdown Runtime Packet for a LIRIA session."
    )
    parser.add_argument(
        "--session",
        required=True,
        help="Session directory, usually saves/<session_name>.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError, OSError, UnicodeDecodeError):
        return ""


def clean(value: str | None) -> str:
    if value is None:
        return ""
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    return "" if value in PLACEHOLDERS else value


def value_or_missing(value: str | None) -> str:
    return clean(value) or MISSING


def dedupe(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        item = clean(value)
        key = item.casefold()
        if not item or key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def first_present(*values: str | None) -> str:
    for value in values:
        item = clean(value)
        if item:
            return item
    return ""


def existing_path(session: Path, candidates: Iterable[str]) -> Path | None:
    for relative in candidates:
        path = session / relative
        if path.is_file():
            return path
    return None


def first_existing_text(session: Path, candidates: Iterable[str]) -> str:
    path = existing_path(session, candidates)
    return read_text(path) if path else ""


def section(text: str, heading: str) -> str:
    """Return a markdown heading section by exact heading text, any depth."""
    wanted = heading.strip().casefold()
    lines = text.splitlines()
    start: int | None = None
    level = 0

    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        title = match.group(2).strip().casefold()
        if title == wanted:
            start = index + 1
            level = len(match.group(1))
            break

    if start is None:
        return ""

    end = len(lines)
    for index in range(start, len(lines)):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", lines[index])
        if match and len(match.group(1)) <= level:
            end = index
            break
    return "\n".join(lines[start:end]).strip()


def bullet_value(block: str, *keys: str) -> str:
    keys_folded = {key.casefold() for key in keys}
    for line in block.splitlines():
        match = re.match(r"^\s*-\s+([^:：]+)\s*[:：]\s*(.*?)\s*$", line)
        if match and match.group(1).strip().casefold() in keys_folded:
            value = clean(match.group(2))
            if value:
                return value
    return ""


def nested_bullets(block: str, parent_key: str) -> list[str]:
    lines = block.splitlines()
    parent_folded = parent_key.casefold()
    out: list[str] = []

    for index, line in enumerate(lines):
        parent = re.match(r"^(\s*)-\s+([^:：]+)\s*[:：]\s*(.*?)\s*$", line)
        if not parent or parent.group(2).strip().casefold() != parent_folded:
            continue

        inline = clean(parent.group(3))
        if inline:
            out.append(inline)

        parent_indent = len(parent.group(1))
        for child_line in lines[index + 1 :]:
            if not child_line.strip():
                continue
            indent = len(child_line) - len(child_line.lstrip(" "))
            if indent <= parent_indent and re.match(r"^\s*-\s+", child_line):
                break
            if indent <= parent_indent and re.match(r"^#{1,6}\s+", child_line):
                break
            child = re.match(r"^\s*-\s+([^:：]+?)(?:\s*[:：]\s*(.*?))?\s*$", child_line)
            if not child:
                continue
            key = clean(child.group(1))
            value = clean(child.group(2) or "")
            has_separator = bool(re.match(r"^\s*-\s+.*?[:：]", child_line))
            if key and value:
                out.append(f"{key}: {value}")
            elif key and not has_separator:
                out.append(key)
        break

    return dedupe(out)


def ordered_items(block: str) -> list[str]:
    items = []
    for line in block.splitlines():
        match = re.match(r"^\s*\d+[.)]\s+(.*?)\s*$", line)
        if match:
            items.append(match.group(1))
    return dedupe(items)


def table_rows(block: str) -> list[list[str]]:
    rows = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [clean(cell) for cell in stripped.strip("|").split("|")]
        if any(cells):
            rows.append(cells)
    return rows


def find_heading_names(block: str, level: int = 3) -> list[str]:
    names = []
    marker = "#" * level
    for line in block.splitlines():
        match = re.match(rf"^{re.escape(marker)}\s+(.+?)\s*$", line)
        if match:
            name = clean(match.group(1).strip("[]"))
            if name and "仮ID" not in name and "名前" not in name:
                names.append(name)
    return dedupe(names)


def extract_case(case_text: str, hotset_text: str) -> dict[str, list[str] | str]:
    active = section(case_text, "Active Case") or case_text
    current_spine = section(hotset_text, "現在の背骨")
    return {
        "active_case_id": first_present(
            bullet_value(active, "id"),
            bullet_value(section(hotset_text, "Active Case 抜粋"), "case_id"),
        ),
        "linked_branch": bullet_value(active, "linked branch"),
        "linked_organization": bullet_value(active, "linked organization"),
        "contact_surface": bullet_value(active, "contact surface"),
        "short_goal": first_present(
            bullet_value(active, "short goal"),
            bullet_value(section(hotset_text, "Active Case 抜粋"), "short goal"),
        ),
        "reveal_step": bullet_value(active, "reveal step"),
        "current_phase": bullet_value(current_spine, "現在フェーズ", "current phase"),
        "resume_anchor": bullet_value(current_spine, "再開アンカー", "resume anchor"),
        "due_trigger": bullet_value(active, "due / trigger", "due", "trigger"),
        "handles": nested_bullets(active, "handles")
        or nested_bullets(section(hotset_text, "Active Case 抜粋"), "handles"),
        "if_ignored": first_present(
            bullet_value(active, "if ignored"),
            bullet_value(section(hotset_text, "Active Case 抜粋"), "if ignored"),
        ),
        "next_visible_change": first_present(
            bullet_value(active, "next visible change"),
            bullet_value(section(hotset_text, "Active Case 抜粋"), "next visible change"),
        ),
    }


def extract_story_spine(story_text: str) -> dict[str, list[str] | str]:
    main_question = bullet_value(section(story_text, "Main Question"), "この話が主人公とヒロインに問うこと")
    branch_state = section(story_text, "Branch State")
    active_branch = nested_block_after_bullet(branch_state, "current active branch")
    pressure = section(story_text, "Pressure Direction")
    heroine_tie = section(story_text, "Heroine Tie")
    org_tie = section(story_text, "Organization Tie")
    invariants = nested_bullets(branch_state, "invariants")

    return {
        "spine_main_question": main_question,
        "active_branch_id": bullet_value(active_branch, "id"),
        "branch_status": bullet_value(active_branch, "status"),
        "branch_linked_case": bullet_value(active_branch, "linked case"),
        "branch_linked_org": bullet_value(active_branch, "linked organization"),
        "branch_contact": bullet_value(active_branch, "contact surface"),
        "branch_next_reveal": bullet_value(active_branch, "next reveal step"),
        "branch_due": bullet_value(active_branch, "due / trigger", "due", "trigger"),
        "pressure_if_ignored": bullet_value(pressure, "if ignored"),
        "pressure_next_move": bullet_value(pressure, "next visible move"),
        "heroine_life_stake": bullet_value(heroine_tie, "life stake"),
        "org_related": bullet_value(org_tie, "related organization"),
        "org_contact": bullet_value(org_tie, "contact surface"),
        "org_npc": bullet_value(org_tie, "contact NPC / role", "important NPC link"),
        "continuity_invariants": invariants,
    }


def nested_block_after_bullet(block: str, parent_key: str) -> str:
    lines = block.splitlines()
    parent_folded = parent_key.casefold()
    for index, line in enumerate(lines):
        parent = re.match(r"^(\s*)-\s+([^:：]+)\s*[:：]?\s*(.*?)\s*$", line)
        if not parent or parent.group(2).strip().casefold() != parent_folded:
            continue
        parent_indent = len(parent.group(1))
        collected = []
        for child_line in lines[index + 1 :]:
            if not child_line.strip():
                collected.append(child_line)
                continue
            indent = len(child_line) - len(child_line.lstrip(" "))
            if indent <= parent_indent and re.match(r"^\s*-\s+", child_line):
                break
            collected.append(child_line)
        return "\n".join(collected)
    return ""


def extract_major_npcs(session: Path, org_cast_text: str, cast_index_text: str) -> list[str]:
    values: list[str] = []
    values.extend(find_heading_names(section(org_cast_text, "Major Figures"), level=3))
    values.extend(nested_bullets(section(org_cast_text, "Organization Relation Ledger"), "major NPCs"))

    npc_section = section(cast_index_text, "npc")
    for row in table_rows(npc_section):
        if row and row[0].casefold() != "名前":
            values.append(row[0])

    npc_dir = session / "cast" / "npc"
    if npc_dir.is_dir():
        for path in sorted(npc_dir.glob("*.md")):
            if path.name == ".gitkeep":
                continue
            values.append(path.stem)

    return [
        item
        for item in dedupe(values)
        if item.casefold() != "tbd" and "TBD" not in item and "未定" not in item
    ]


def extract_read_priorities(session: Path) -> list[str]:
    readme = first_existing_text(session, ["README.md", "readme.md"])
    priorities = ordered_items(section(readme, "Read Priority"))
    return priorities or DEFAULT_READ_PRIORITIES


def format_list(items: Iterable[str], empty: str = MISSING) -> list[str]:
    cleaned = dedupe(items)
    if not cleaned:
        return [f"- {empty}"]
    return [f"- {item}" for item in cleaned]


def build_packet(session: Path) -> str:
    case_text = first_existing_text(session, ["current/case.md", "case.md"])
    hotset_text = first_existing_text(session, ["current/hotset.md", "hotset.md"])
    story_text = first_existing_text(session, ["design/story_spine.md", "story_spine.md"])
    org_cast_text = first_existing_text(session, ["design/organization_cast.md", "organization_cast.md"])
    cast_index_text = first_existing_text(session, ["indexes/cast_index.md", "cast_index.md"])

    case = extract_case(case_text, hotset_text)
    spine = extract_story_spine(story_text)

    active_case_id = first_present(
        str(case["active_case_id"]),
        str(spine["branch_linked_case"]),
    )
    active_branch_id = first_present(
        str(spine["active_branch_id"]),
        str(case["linked_branch"]),
    )
    branch_status = str(spine["branch_status"])
    linked_org = first_present(
        str(case["linked_organization"]),
        str(spine["branch_linked_org"]),
        str(spine["org_related"]),
    )
    contact = first_present(
        str(case["contact_surface"]),
        str(spine["branch_contact"]),
        str(spine["org_contact"]),
        str(spine["org_npc"]),
    )
    reveal = first_present(
        str(case["reveal_step"]),
        str(spine["branch_next_reveal"]),
        str(case["current_phase"]),
        str(case["resume_anchor"]),
    )
    if_ignored_due = combine_parts(
        ("if ignored", first_present(str(case["if_ignored"]), str(spine["pressure_if_ignored"]))),
        ("due / trigger", first_present(str(case["due_trigger"]), str(spine["branch_due"]))),
        ("next visible", first_present(str(case["next_visible_change"]), str(spine["pressure_next_move"]))),
    )

    lines = [
        f"# Runtime Packet: {session.name}",
        "",
        f"- session: `{session}`",
        f"- active_case_id: {value_or_missing(active_case_id)}",
        f"- active_branch_id: {value_or_missing(active_branch_id)}",
        f"- branch_status: {value_or_missing(branch_status)}",
        f"- spine_main_question: {value_or_missing(str(spine['spine_main_question']))}",
        f"- reveal/current step: {value_or_missing(reveal)}",
        f"- short_goal: {value_or_missing(str(case['short_goal']))}",
        f"- linked org/contact: {value_or_missing(join_nonempty([linked_org, contact], ' / '))}",
        f"- heroine life stake: {value_or_missing(str(spine['heroine_life_stake']))}",
        f"- if_ignored_due: {value_or_missing(if_ignored_due)}",
        "",
        "## Concrete Handles",
        *format_list(case["handles"] if isinstance(case["handles"], list) else []),
        "",
        "## Major NPC IDs",
        *format_list(extract_major_npcs(session, org_cast_text, cast_index_text)),
        "",
        "## Continuity Invariants",
        *format_list(spine["continuity_invariants"] if isinstance(spine["continuity_invariants"], list) else []),
        "",
        "## Read Priorities",
    ]

    for index, item in enumerate(extract_read_priorities(session), start=1):
        lines.append(f"{index}. {item}")

    if not session.exists():
        lines.extend(["", "> session path does not exist; all fields are best-effort missing values."])

    return "\n".join(lines).rstrip() + "\n"


def join_nonempty(values: Iterable[str], sep: str) -> str:
    return sep.join(dedupe(values))


def combine_parts(*parts: tuple[str, str]) -> str:
    rendered = []
    for label, value in parts:
        item = clean(value)
        if item:
            rendered.append(f"{label}: {item}")
    return "; ".join(rendered)


def main() -> int:
    args = parse_args()
    session = Path(args.session)
    print(build_packet(session), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
