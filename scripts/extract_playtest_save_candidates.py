#!/usr/bin/env python3
"""Generate reviewable save-state proposals from AI Persona Playtest output.

This script is intentionally proposal-only. It writes a markdown review packet
under archive/logs and never edits current/, design/, cast/, or indexes/.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE_RE = re.compile(r"^(analysis|raw)_(\d{8}_\d{6})_ai_persona_playtest\.md$")


@dataclass(frozen=True)
class SourceBundle:
    session_name: str
    session_path: Path
    primary_path: Path
    primary_kind: str
    raw_path: Path | None
    analysis_path: Path | None


@dataclass(frozen=True)
class PersonCandidate:
    name: str
    kind: str
    summary: str
    source_group: str


def main() -> int:
    args = parse_args()
    bundle = resolve_sources(args.session, args.source_path or args.source)

    primary_text = read_text(bundle.primary_path)
    raw_text = read_text(bundle.raw_path) if bundle.raw_path else ""
    analysis_text = read_text(bundle.analysis_path) if bundle.analysis_path else ""

    primary_groups = save_groups_for_primary(bundle.primary_kind, primary_text)
    supplemental_groups: dict[str, list[str]] = {}
    if bundle.primary_kind == "analysis" and raw_text:
        supplemental_groups = parse_save_groups(extract_section(raw_text, "Save Notes"))
    elif bundle.primary_kind == "raw" and analysis_text:
        supplemental_groups = parse_save_groups(extract_section(analysis_text, "Save Candidates"))

    groups = merge_groups(primary_groups, supplemental_groups)
    manga_candidates = collect_first_section(
        [primary_text, analysis_text, raw_text],
        "Manga Candidates",
    )
    risks = collect_first_section([analysis_text, primary_text], "Risks To Review")

    proposal = build_proposal(bundle=bundle, groups=groups, manga_candidates=manga_candidates, risks=risks)
    output_path = args.output or default_output_path(bundle.session_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(proposal, encoding="utf-8")

    if args.stdout:
        print(proposal)
    print(f"wrote save candidate proposal: {display_path(output_path)}")
    print("mode: proposal only; session state files were not modified")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract AI Persona Playtest Save Candidates into a reviewable proposal markdown.",
    )
    parser.add_argument("session", help="Session name, e.g. session_story_wiring_test_001, or saves/<session> path.")
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        help="Optional raw_* or analysis_* playtest report path. Defaults to latest analysis report for the session.",
    )
    parser.add_argument(
        "--source",
        dest="source_path",
        type=Path,
        help="Optional raw_* or analysis_* playtest report path. Overrides the positional source.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional proposal output path. Defaults to saves/<session>/archive/logs/save_candidates_<timestamp>.md.",
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

    session_name = session_path.name
    logs_dir = session_path / "archive/logs"
    if not logs_dir.is_dir():
        raise SystemExit(f"session has no archive/logs directory: {display_path(logs_dir)}")

    primary_path = resolve_source_path(source_arg, logs_dir)
    primary_kind, timestamp = classify_source(primary_path)
    raw_path = logs_dir / f"raw_{timestamp}_ai_persona_playtest.md"
    analysis_path = logs_dir / f"analysis_{timestamp}_ai_persona_playtest.md"

    return SourceBundle(
        session_name=session_name,
        session_path=session_path,
        primary_path=primary_path,
        primary_kind=primary_kind,
        raw_path=raw_path if raw_path.is_file() else None,
        analysis_path=analysis_path if analysis_path.is_file() else None,
    )


def resolve_source_path(source_arg: Path | None, logs_dir: Path) -> Path:
    if source_arg:
        path = source_arg
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        if not path.is_file():
            raise SystemExit(f"source file not found: {display_path(path)}")
        return path

    analyses = sorted(logs_dir.glob("analysis_*_ai_persona_playtest.md"))
    if analyses:
        return analyses[-1]
    raws = sorted(logs_dir.glob("raw_*_ai_persona_playtest.md"))
    if raws:
        return raws[-1]
    raise SystemExit(f"no AI Persona Playtest analysis/raw logs found in {display_path(logs_dir)}")


def classify_source(path: Path) -> tuple[str, str]:
    match = SOURCE_RE.match(path.name)
    if not match:
        raise SystemExit(
            "source must be named analysis_YYYYMMDD_HHMMSS_ai_persona_playtest.md "
            f"or raw_YYYYMMDD_HHMMSS_ai_persona_playtest.md: {display_path(path)}"
        )
    return match.group(1), match.group(2)


def read_text(path: Path | None) -> str:
    if path is None:
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def save_groups_for_primary(kind: str, text: str) -> dict[str, list[str]]:
    heading = "Save Candidates" if kind == "analysis" else "Save Notes"
    groups = parse_save_groups(extract_section(text, heading))
    if groups:
        return groups
    fallback_heading = "Save Notes" if kind == "analysis" else "Save Candidates"
    return parse_save_groups(extract_section(text, fallback_heading))


def extract_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    heading_re = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.IGNORECASE)
    in_section = False
    collected: list[str] = []
    for line in lines:
        stripped = line.strip()
        if heading_re.match(stripped):
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if in_section:
            collected.append(line.rstrip())
    return "\n".join(collected).strip()


def parse_save_groups(section_text: str) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    current = "General"
    known_groups = {
        "Initial Story Assembly",
        "Light Story Reference Pass",
        "Active Case",
        "Story Spine",
        "Organization Cast",
        "Relationships",
    }
    for raw_line in section_text.splitlines():
        item = clean_item(raw_line)
        if not item:
            continue
        heading = item.rstrip(":：").strip()
        if heading in known_groups and item.endswith((":","：")):
            current = heading
            groups.setdefault(current, [])
            continue
        groups.setdefault(current, [])
        groups[current].append(item)
    return groups


def clean_item(line: str) -> str:
    stripped = line.strip()
    stripped = re.sub(r"^[-*]\s+", "", stripped)
    stripped = re.sub(r"^\d+[.)．]\s+", "", stripped)
    return stripped.strip()


def merge_groups(primary: dict[str, list[str]], supplemental: dict[str, list[str]]) -> dict[str, list[str]]:
    merged: dict[str, list[str]] = {}
    for source in (primary, supplemental):
        for group, items in source.items():
            target = merged.setdefault(group, [])
            for item in items:
                if item not in target:
                    target.append(item)
    return merged


def collect_first_section(texts: list[str], heading: str) -> list[str]:
    for text in texts:
        if not text:
            continue
        section = extract_section(text, heading)
        items = [clean_item(line) for line in section.splitlines()]
        items = [item for item in items if item]
        if items:
            return unique(items)
    return []


def build_proposal(
    *,
    bundle: SourceBundle,
    groups: dict[str, list[str]],
    manga_candidates: list[str],
    risks: list[str],
) -> str:
    active_case = parse_key_values(groups.get("Active Case", []))
    story_spine = parse_key_values(groups.get("Story Spine", []))
    relationships = groups.get("Relationships", [])
    people = extract_people(groups)
    heroine_candidates = [person for person in people if person.kind == "heroine"]
    npc_candidates = [person for person in people if person.kind == "npc"]
    if not npc_candidates:
        npc_candidates = infer_npc_candidates(groups)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = [
        "# AI Persona Playtest Save Candidate Proposal",
        "",
        "## Summary",
        "",
        f"- session: `{bundle.session_name}`",
        f"- generated at: {now}",
        f"- primary source: `{display_path(bundle.primary_path)}`",
        f"- primary input priority: `{bundle.primary_kind}`",
        f"- companion raw log: `{display_path(bundle.raw_path) if bundle.raw_path else 'not found'}`",
        f"- companion analysis report: `{display_path(bundle.analysis_path) if bundle.analysis_path else 'not found'}`",
        "- mode: proposal only",
        "- files changed by this script: this proposal markdown only",
        "- files intentionally not modified: `current/*`, `design/*`, `cast/*`, `indexes/*`",
        "",
        "## Review Rule",
        "",
        "Do not paste this whole file blindly. Review each block, then manually apply only the pieces that match the actual session state.",
        "",
        "## Source Save Candidates",
        "",
        format_group_dump(groups),
        "",
        "## Proposed Updates",
        "",
        "### design/story_reference.md",
        "",
        format_story_reference(groups),
        "",
        "### design/story_spine.md",
        "",
        format_story_spine(groups, story_spine),
        "",
        "### design/organization_cast.md",
        "",
        format_organization_cast(groups, npc_candidates, heroine_candidates),
        "",
        "### current/case.md",
        "",
        format_case(active_case, groups.get("Active Case", [])),
        "",
        "### current/hotset.md",
        "",
        format_hotset(active_case, story_spine, relationships),
        "",
        "### cast/heroine/*.md creation candidates",
        "",
        format_heroine_candidates(heroine_candidates, relationships, active_case),
        "",
        "### cast/npc/*.md creation candidates",
        "",
        format_npc_candidates(npc_candidates, active_case),
        "",
        "### indexes/cast_index.md",
        "",
        format_cast_index(heroine_candidates, npc_candidates),
        "",
        "### Manga Candidates",
        "",
        format_items(manga_candidates, empty="- No manga candidates found."),
        "",
        "### Risks To Review",
        "",
        format_items(risks, empty="- No explicit risks found in the analysis report."),
        "",
        "## Manual Apply Checklist",
        "",
        "- [ ] Compare this proposal with current session files before editing.",
        "- [ ] Update `design/story_reference.md` with only selected engines and LIRIA conversion notes.",
        "- [ ] Update `design/story_spine.md` with Main Question / Reveal Ladder / Pressure Direction / Heroine Tie.",
        "- [ ] Update `design/organization_cast.md` before letting organization contacts speak again.",
        "- [ ] Update `current/case.md` and keep it short: visible problem, request, handles, progress, if ignored, next visible change.",
        "- [ ] Create only the heroine/NPC sheets that are actually recurring or scene-leading.",
        "- [ ] Update `indexes/cast_index.md` after creating cast files.",
        "- [ ] Run `bash scripts/check_session_integrity.sh {}` after manual application.".format(bundle.session_name),
        "",
    ]
    return "\n".join(lines)


def format_group_dump(groups: dict[str, list[str]]) -> str:
    if not groups:
        return "- No Save Candidates / Save Notes section found."
    parts: list[str] = []
    for group, items in groups.items():
        parts.append(f"#### {group}")
        parts.append("")
        parts.append(format_items(items, empty="- No items."))
        parts.append("")
    return "\n".join(parts).strip()


def format_story_reference(groups: dict[str, list[str]]) -> str:
    initial = groups.get("Initial Story Assembly", [])
    light_lines = [item for item in initial if "Light Story Reference Pass" in item or "selected engine" in item.lower()]
    avoid_lines = [item for item in initial if "Avoid" in item or "避け" in item]
    signal_lines = [item for item in initial if item not in light_lines and item not in avoid_lines]
    result = [
        "```markdown",
        "## Light Story Reference Pass",
        "",
        "### Selection Signals",
        format_items(signal_lines, empty="- TODO: extract concrete life / romance / ability / institution signals."),
        "",
        "### Selected Reference Engines",
        format_items(light_lines, empty="- TODO: choose 1-3 abstract reference engines without source names."),
        "",
        "### Avoid Direct Imitation",
        format_items(avoid_lines, empty="- Do not carry source work names, characters, famous scenes, or dialogue into LIRIA."),
        "```",
    ]
    return "\n".join(result)


def format_story_spine(groups: dict[str, list[str]], parsed: dict[str, str]) -> str:
    items = groups.get("Story Spine", [])
    if not items:
        return "```markdown\n## Story Spine\n- TODO: Main Question / Reveal Ladder / Pressure Direction / Heroine Tie\n```"
    return "\n".join(["```markdown", "## Story Spine", *[f"- {item}" for item in items], "```"])


def format_organization_cast(
    groups: dict[str, list[str]],
    npc_candidates: list[PersonCandidate],
    heroine_candidates: list[PersonCandidate],
) -> str:
    org_items = groups.get("Organization Cast", [])
    if not org_items:
        return "```markdown\n## Major Figures\n- TODO: add 3-5 figures if organization pressure exists.\n```"
    lines = ["```markdown", "## Major Figures", ""]
    for person in [*heroine_candidates, *npc_candidates]:
        lines.extend(
            [
                f"### {person.name}",
                "",
                f"- status: seed",
                f"- role in organization: {person.summary}",
                "- public face: TODO",
                "- belief: TODO",
                "- contradiction: TODO",
                "- pressure method: TODO",
                "- knows: TODO",
                "- suspects: TODO",
                "- unknown: TODO",
                "- speech discipline: abstract terms must return to concrete objects, people, procedures, or places within two sentences",
                "",
            ]
        )
    lines.extend(["## Source Notes", *[f"- {item}" for item in org_items], "```"])
    return "\n".join(lines)


def format_case(parsed: dict[str, str], source_items: list[str]) -> str:
    fields = [
        "id",
        "title",
        "phase",
        "visible problem",
        "visible request",
        "short goal",
        "handles",
        "progress condition",
        "if ignored",
        "next visible change",
        "relationship stake",
    ]
    lines = ["```markdown", "## Active Case"]
    for field in fields:
        value = parsed.get(field, "")
        if value:
            lines.append(f"- {field}: {value}")
    if len(lines) == 2 and source_items:
        lines.extend(f"- {item}" for item in source_items)
    elif len(lines) == 2:
        lines.append("- TODO: no active case candidate found.")
    lines.append("```")
    return "\n".join(lines)


def format_hotset(active_case: dict[str, str], story_spine: dict[str, str], relationships: list[str]) -> str:
    anchor = active_case.get("next visible change") or active_case.get("short goal") or "TODO"
    title = active_case.get("title") or "TODO"
    pressure = story_spine.get("Pressure Direction") or story_spine.get("Pressure direction") or "TODO"
    heroine_tie = story_spine.get("Heroine Tie") or "TODO"
    lines = [
        "```markdown",
        "- 再開アンカー: " + anchor,
        "- active case: " + title,
        "- next 1-2 scene pressure: " + pressure,
        "- heroine / relationship heat: " + heroine_tie,
    ]
    if relationships:
        lines.append("- relationship notes:")
        lines.extend(f"  - {item}" for item in relationships[:5])
    lines.append("```")
    return "\n".join(lines)


def format_heroine_candidates(
    candidates: list[PersonCandidate],
    relationships: list[str],
    active_case: dict[str, str],
) -> str:
    if not candidates:
        return "- No heroine sheet candidates found. Review `Relationships` manually if a heroine candidate appeared."
    blocks: list[str] = []
    next_trigger = active_case.get("next visible change") or active_case.get("short goal") or "TODO"
    for person in candidates:
        path = f"cast/heroine/{safe_filename(person.name)}.md"
        blocks.extend(
            [
                f"#### `{path}`",
                "",
                "```markdown",
                f"# {person.name}",
                "",
                "## Core",
                f"- role: {person.summary}",
                "- model sheet status: text-only",
                "- Heroine Crisis Role: TODO",
                "- boundary / consent line: TODO",
                "- relationship hook: TODO",
                f"- next appearance trigger: {next_trigger}",
                "",
                "## Relationship Source Notes",
                format_items(relationships, empty="- TODO"),
                "```",
                "",
            ]
        )
    return "\n".join(blocks).strip()


def format_npc_candidates(candidates: list[PersonCandidate], active_case: dict[str, str]) -> str:
    if not candidates:
        return "- No NPC promotion candidates found."
    next_trigger = active_case.get("next visible change") or active_case.get("short goal") or "TODO"
    blocks: list[str] = []
    for person in candidates:
        path = f"cast/npc/{safe_filename(person.name)}.md"
        blocks.extend(
            [
                f"#### `{path}`",
                "",
                "```markdown",
                f"# {person.name}",
                "",
                "- visible label: " + person.name,
                "- identity status: confirmed | alias | unknown",
                f"- role in organization: {person.summary}",
                "- affiliation / contact surface: TODO",
                "- knows: TODO",
                "- suspects: TODO",
                "- unknown: TODO",
                "- speech discipline: abstract terms must return to concrete objects, people, procedures, or places within two sentences",
                "- relationship hook with protagonist: TODO",
                "- relationship hook with heroine/NPC: TODO",
                f"- next appearance trigger: {next_trigger}",
                "```",
                "",
            ]
        )
    return "\n".join(blocks).strip()


def format_cast_index(heroine_candidates: list[PersonCandidate], npc_candidates: list[PersonCandidate]) -> str:
    lines = ["```markdown", "## heroine", "", "| 名前 | ファイル | 現在地 | 主な役割 | 優先して読む時 |", "|---|---|---|---|---|"]
    if heroine_candidates:
        for person in heroine_candidates:
            lines.append(
                f"| {person.name} | `cast/heroine/{safe_filename(person.name)}.md` | TODO | {table_cell(person.summary)} | 恋愛/生活/事件がこの人物に触れる時 |"
            )
    else:
        lines.append("| TODO | TODO | TODO | TODO | TODO |")
    lines.extend(["", "## npc", "", "| 名前 | ファイル | 現在地 | 主な役割 | 優先して読む時 |", "|---|---|---|---|---|"])
    if npc_candidates:
        for person in npc_candidates:
            lines.append(
                f"| {person.name} | `cast/npc/{safe_filename(person.name)}.md` | TODO | {table_cell(person.summary)} | 再登場、scene lead、組織接触、口調確認時 |"
            )
    else:
        lines.append("| TODO | TODO | TODO | TODO | TODO |")
    lines.append("```")
    return "\n".join(lines)


def parse_key_values(items: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in items:
        match = re.match(r"([^:：]{1,80})[:：]\s*(.+)$", item)
        if not match:
            continue
        key = match.group(1).strip()
        value = match.group(2).strip()
        result[key] = value
    return result


def extract_people(groups: dict[str, list[str]]) -> list[PersonCandidate]:
    org_people = people_from_items(groups.get("Organization Cast", []), source_group="Organization Cast")
    heroine_names = {person.name for person in org_people if person.kind == "heroine"}
    relationship_people = people_from_items(groups.get("Relationships", []), source_group="Relationships", heroine_names=heroine_names)
    relationship_people = [canonicalize_person(person, org_people) for person in relationship_people]
    by_name: dict[str, PersonCandidate] = {}
    for person in [*org_people, *relationship_people]:
        existing = by_name.get(person.name)
        if existing is None:
            by_name[person.name] = person
            continue
        kind = "heroine" if "heroine" in {existing.kind, person.kind} else existing.kind
        summary = existing.summary if person.summary in existing.summary else f"{existing.summary} / {person.summary}"
        by_name[person.name] = PersonCandidate(name=person.name, kind=kind, summary=summary, source_group=existing.source_group)
    return list(by_name.values())


def canonicalize_person(person: PersonCandidate, known_people: list[PersonCandidate]) -> PersonCandidate:
    for known in known_people:
        if known.name != person.name and (known.name.endswith(person.name) or known.name.startswith(person.name)):
            kind = "heroine" if "heroine" in {known.kind, person.kind} else known.kind
            return PersonCandidate(
                name=known.name,
                kind=kind,
                summary=person.summary,
                source_group=person.source_group,
            )
    return person


def people_from_items(
    items: list[str],
    *,
    source_group: str,
    heroine_names: set[str] | None = None,
) -> list[PersonCandidate]:
    heroine_names = heroine_names or set()
    people: list[PersonCandidate] = []
    field_names = {
        "id",
        "title",
        "phase",
        "visible problem",
        "visible request",
        "short goal",
        "handles",
        "progress condition",
        "if ignored",
        "next visible change",
        "Main Question",
        "Reveal Ladder",
        "Pressure Direction",
        "Heroine Tie",
        "Heroine Crisis Role",
    }
    for item in items:
        match = re.match(r"([^:：]{1,30})[:：]\s*(.+)$", item)
        if not match:
            continue
        name = match.group(1).strip()
        summary = match.group(2).strip()
        if name in field_names or len(name) < 2:
            continue
        if any(token in name for token in (" ", "/", "`", "##")):
            continue
        kind = "heroine" if name in heroine_names or re.search(r"ヒロイン|heroine|AFFINITY", summary, re.IGNORECASE) else "npc"
        people.append(PersonCandidate(name=name, kind=kind, summary=summary, source_group=source_group))
    return people


def infer_npc_candidates(groups: dict[str, list[str]]) -> list[PersonCandidate]:
    text = "\n".join(item for items in groups.values() for item in items)
    names = unique(re.findall(r"[一-龯ぁ-んァ-ヶー]{2,6}(?:響|万里|紗月|棚橋)?", text))
    ignored = {"生活導線", "能力", "記録", "端末", "手続", "組織", "候補", "主人公"}
    candidates: list[PersonCandidate] = []
    for name in names:
        if name in ignored or len(candidates) >= 5:
            continue
        if re.search(rf"{re.escape(name)}", text):
            candidates.append(PersonCandidate(name=name, kind="npc", summary="inferred from playtest save candidates; review before applying", source_group="inferred"))
    return candidates


def format_items(items: list[str], *, empty: str) -> str:
    if not items:
        return empty
    return "\n".join(f"- {item}" for item in items)


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def safe_filename(name: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|`]+", "_", name.strip())
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned or "review_candidate"


def table_cell(value: str) -> str:
    return value.replace("|", "/")


def default_output_path(session_path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return session_path / "archive/logs" / f"save_candidates_{timestamp}.md"


def display_path(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    sys.exit(main())
