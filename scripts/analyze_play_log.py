#!/usr/bin/env python3
"""Analyze a real or real-like LIRIA play log.

This is a deterministic review helper. It does not judge whether the story is
"good" by itself; it flags evidence that a human reviewer can inspect quickly.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Finding:
    label: str
    status: str
    evidence: list[str]
    note: str


def main() -> int:
    args = parse_args()
    log_path = args.log_path
    if not log_path.is_file():
        raise SystemExit(f"log file not found: {log_path}")

    text = log_path.read_text(encoding="utf-8", errors="replace")
    report = analyze_log(text, log_path=log_path, expected_turns=args.expected_turns)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"wrote analysis report: {display_path(args.output)}")
    else:
        print(report)

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Review a LIRIA play log for story quality, guardrail risks, save candidates, and manga candidates.",
    )
    parser.add_argument("log_path", type=Path, help="Raw play log file to analyze.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional markdown output path. Prints to stdout when omitted.",
    )
    parser.add_argument(
        "--expected-turns",
        type=int,
        help="Expected number of turns. Used to flag truncated AI persona logs.",
    )
    return parser.parse_args()


def analyze_log(text: str, *, log_path: Path, expected_turns: int | None = None) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    logical_lines = merge_label_lines(lines)
    non_empty = [line for line in logical_lines if line.strip()]
    player_lines = grep_lines(logical_lines, PLAYER_PATTERNS)
    turn_count = len(grep_lines(logical_lines, [r"^###\s*Turn\s+\d+"], limit=None))
    gm_lines = grep_lines(logical_lines, GM_PATTERNS)
    dialogue_lines = grep_lines(logical_lines, DIALOGUE_PATTERNS)
    quoted_dialogue = grep_lines(logical_lines, [r"「[^」]{2,}」"])
    findings = build_findings(logical_lines, expected_turns=expected_turns, turn_count=turn_count)
    save_candidates = collect_save_candidates(logical_lines)
    manga_candidates = collect_manga_candidates(logical_lines)
    risks = collect_risks(findings)

    score = sum(1 for finding in findings if finding.status == "ok")
    warn = sum(1 for finding in findings if finding.status == "warn")
    miss = sum(1 for finding in findings if finding.status == "missing")

    return "\n\n".join(
        [
            "# LIRIA Play Log Analysis",
            "## Summary",
            "\n".join(
                [
                    f"- log: {display_path(log_path)}",
                    f"- non-empty lines: {len(non_empty)}",
                    f"- estimated turns: {turn_count}",
                    f"- expected turns: {expected_turns if expected_turns is not None else 'not provided'}",
                    f"- estimated player inputs: {len(player_lines)}",
                    f"- estimated GM / narration lines: {len(gm_lines)}",
                    f"- estimated dialogue lines: {max(len(dialogue_lines), len(quoted_dialogue))}",
                    f"- result: {score} ok / {warn} warn / {miss} missing",
                ]
            ),
            "## Findings",
            format_findings(findings),
            "## Save Candidates",
            format_list(
                save_candidates,
                empty="保存候補は自動抽出できませんでした。current/gm.md, current/player.md, current/harem.md, current/case.md を人間レビューしてください。",
            ),
            "## Manga Candidates",
            format_list(
                manga_candidates,
                empty="漫画化候補は自動抽出できませんでした。感情の山、手元、小物、引きのコマを人間レビューしてください。",
            ),
            "## Risks To Review",
            format_list(risks, empty="明確な赤信号は自動抽出されませんでした。"),
            "## Next Review Prompt",
            "\n".join(
                [
                    "```text",
                    "この分析結果と生ログを前提に、LIRIAらしさ、ヒロイン自律性、恋愛・生活・事件の絡み、能力/装備の便利すぎ、Anti-Meta、Knowledge Boundary、保存候補、漫画化候補を人間レビューしてください。",
                    "```",
                ]
            ),
        ]
    ).strip() + "\n"


def build_findings(lines: list[str], *, expected_turns: int | None, turn_count: int) -> list[Finding]:
    return [
        check_turn_count(lines, expected_turns=expected_turns, turn_count=turn_count),
        check_absence(
            "旧inner-galge固有名詞リーク",
            lines,
            [r"怜|真凛|澪|月読堂"],
            "旧inner-galgeや人格例文の固有名詞が、新規LIRIA playtestへ混入していないか。",
        ),
        check_absence(
            "例文モチーフ再利用リスク",
            lines,
            [r"クリーニング|洗濯店|白い上着|預かり札|白い軽バン|蒼湾|青鈍"],
            "prompt例文や直近playtestに寄った職業・小物・導入が再利用されていないか。プレイヤーが明示した場合は人間レビューで許容してよい。",
        ),
        check_presence(
            "LIRIAらしさ",
            lines,
            [r"恋愛|生活|事件|依頼|日常|関係|インナー|本音|孤独|恐れ"],
            "恋愛・生活・事件・内面のどれかがログに出ているか。",
        ),
        check_presence(
            "プレイヤー入力の自然さ",
            lines,
            PLAYER_PATTERNS,
            "プレイヤーらしい行動/相談/内心が見えるか。",
        ),
        check_presence(
            "ヒロイン/NPCの自律性",
            lines,
            [r"断る|拒む|迷う|黙る|選ぶ|問い返す|睨む|距離|警戒|ためら|伏せ"],
            "相手が都合よく従うだけでなく、意思や警戒を持っているか。",
        ),
        check_presence(
            "恋愛・生活・事件の絡み",
            lines,
            [r"家賃|仕事|収入|職場|拠点|生活|依頼|事件|相談|信用|近所|帰宅|夜|朝"],
            "事件だけ、恋愛だけに分離せず、生活の制約や仕事と絡んでいるか。",
        ),
        check_absence(
            "恋愛の自動確定リスク",
            lines,
            [r"惚れた|恋に落ちた|攻略完了|陥落|好感度が上がった|身体を許した"],
            "好意や親密さがプレイヤー願望だけで確定していないか。",
        ),
        check_presence(
            "能力/装備の制約",
            lines,
            [r"代償|痕跡|疲労|誤解|目撃|リスク|残回数|cooldown|条件|使えない|壊れ"],
            "能力や道具が万能解決にならず、条件・代償・痕跡を持つか。",
        ),
        check_absence(
            "バトルRPG化リスク",
            lines,
            [r"レベルアップ|経験値|装備強化|攻撃力|防御力|魔王|討伐|周回|ドロップ報酬"],
            "危機が戦闘ゲームの報酬導線へ戻っていないか。",
        ),
        check_presence(
            "関係組織の筋",
            lines,
            [r"理念|目的|組織|NPO|会社|支援|相談窓口|contact surface|弱い継ぎ目|弱点|矛盾"],
            "敵/関係組織がただの悪役でなく、理念・接点・矛盾を持つか。",
        ),
        check_case_clarity(lines),
        check_absence(
            "Anti-Meta Dialogueリスク",
            lines,
            [r"「[^」]*(AFFINITY|フラグ|好感度|GM|システム(?!ズ)|知識境界|Manga Export)[^」]*」"],
            "NPC台詞にメタ語が混ざっていないか。",
        ),
        check_presence(
            "Knowledge Boundary",
            lines,
            [r"知らない|まだ言っていない|伏せる|本名|秘密|共有|聞こえない|内心|推測|説明しない|隠して|Unknown|Known|Suspected"],
            "誰が何を知っているかの境界が見えるか。",
        ),
        check_presence(
            "保存に残すべき変化",
            lines,
            [r"AFFINITY|bond|約束|秘密|フック|クロック|現在フェーズ|コンディション|後遺症|痕跡|Manga Export Candidates"],
            "再開やcompressに残すべき差分がログに現れているか。",
        ),
        check_presence(
            "次ターンへの引き",
            lines,
            [r"次|まだ|だが|しかし|その時|電話|通知|足音|視線|沈黙|返事はない|終わっていない"],
            "次に再開したくなる未解決の引きがあるか。",
        ),
        check_tool_log_leakage(lines),
        check_choice_scaffold(lines),
    ]


def check_presence(label: str, lines: list[str], patterns: list[str], note: str) -> Finding:
    evidence = grep_lines(lines, patterns, limit=3)
    status = "ok" if evidence else "missing"
    return Finding(label=label, status=status, evidence=evidence, note=note)


def check_absence(label: str, lines: list[str], patterns: list[str], note: str) -> Finding:
    evidence = grep_lines(lines, patterns, limit=3)
    status = "warn" if evidence else "ok"
    return Finding(label=label, status=status, evidence=evidence or ["赤信号なし"], note=note)


def check_turn_count(lines: list[str], *, expected_turns: int | None, turn_count: int) -> Finding:
    player_count = len(grep_lines(lines, PLAYER_PATTERNS, limit=None))
    evidence = [f"turns={turn_count}", f"player_inputs={player_count}"]
    if expected_turns is not None:
        evidence.insert(0, f"expected_turns={expected_turns}")
    if turn_count == 0:
        return Finding(
            label="ターン数",
            status="missing",
            evidence=evidence,
            note="`### Turn NNN` が見つからない。ログ形式が崩れている可能性がある。",
        )
    if expected_turns is not None and turn_count < expected_turns:
        return Finding(
            label="ターン数",
            status="warn",
            evidence=evidence,
            note="指定ターン数より実出力ターン数が少ない。AIが途中で要約終了したか、出力を短く切った可能性がある。",
        )
    if player_count and abs(player_count - turn_count) > 1:
        return Finding(
            label="ターン数",
            status="warn",
            evidence=evidence,
            note="Turn数とPlayer入力数が大きくズレている。ログ形式または抽出が崩れている可能性がある。",
        )
    return Finding(
        label="ターン数",
        status="ok",
        evidence=evidence,
        note="Turn見出しとPlayer入力数がおおむね対応している。",
    )


def check_tool_log_leakage(lines: list[str]) -> Finding:
    leakage = grep_lines(
        lines,
        [
            r"\bRan python\b",
            r"\bpython(?:3)?\s+-\s*<<",
            r"\bAUTOSAVE_DONE=\d\b",
            r"^diff --git\b",
            r"^@@\s+-\d",
            r"^\+\+\+\s+[ab]/",
            r"^---\s+[ab]/",
            r"^\*\*\* Begin Patch$",
            r"^\*\*\* End Patch$",
            r"^(?:\$|%)\s*(?:bash|python3?|git|sed|rg|cat|ls|mkdir|cp|mv|rm|chmod)\b",
            r"^(?:bash|python3?|git|sed|rg|cat|ls|mkdir|cp|mv|rm|chmod)\s+(?:scripts/|play\.sh|[-\w./]+)",
        ],
        limit=8,
    )
    if leakage:
        return Finding(
            label="ツールログ漏れ",
            status="warn",
            evidence=leakage,
            note="物語本文に `Ran python`、shell command、AUTOSAVE_DONE、diff/patch 出力などの実行ログが混ざっていないか。",
        )
    return Finding(
        label="ツールログ漏れ",
        status="ok",
        evidence=["赤信号なし"],
        note="ツール実行ログや差分出力らしい行は自動抽出されませんでした。",
    )


def check_choice_scaffold(lines: list[str]) -> Finding:
    numbered = grep_lines(lines, [r"^[0-9]+[.．]\s"], limit=12)
    handoffs = grep_lines(lines, [r"^→\s*どうする[？?]"], limit=5)
    if not numbered:
        if handoffs:
            return Finding(
                label="選択補助",
                status="warn",
                evidence=handoffs[:3],
                note="番号つき選択補助がない。通常会話や余韻なら問題ないが、初回導入、初登場、依頼、相談、危機、時間圧なら `1-3` 候補 + `4. 自由入力` が必要。",
            )
        return Finding(
            label="選択補助",
            status="ok",
            evidence=[],
            note="番号つき選択補助は未使用。自由入力中心なら問題なし。",
        )

    turn_count = len(grep_lines(lines, [r"^###\s*Turn\s+\d+"], limit=None))
    choice_blocks = collect_choice_blocks(lines)
    choice_four = grep_lines(lines, [r"^4\.\s*自由入力\s*$"], limit=3)
    five_or_more = grep_lines(lines, [r"^(?:0|5|6|7|8|9|[1-9]\d+)[.．]\s"], limit=3)
    risky = grep_lines(
        lines,
        [r"^[1-3][.．].*(好感度|惚れ|成功|解決|暴く|確定|親密になる|身体的親密)"],
        limit=3,
    )
    choice_block_count = len(grep_lines(lines, [r"^1[.．]\s"], limit=None))

    evidence = numbered[:3]
    warnings: list[str] = []
    malformed_blocks: list[str] = []
    for start_line, numbers, block_lines in choice_blocks:
        if numbers != [1, 2, 3, 4]:
            malformed_blocks.append(f"line {start_line}: choice numbers are {','.join(str(number) for number in numbers)}")
            evidence.extend(block_lines[:4])
            continue
        if not re.match(r"^4\.\s*自由入力\s*$", block_lines[-1]):
            malformed_blocks.append(f"line {start_line}: final choice must be exactly `4. 自由入力`")
            evidence.append(block_lines[-1])
    if numbered and not choice_blocks:
        warnings.append("1から始まる選択ブロックが見当たらない")
    if malformed_blocks:
        warnings.extend(malformed_blocks[:3])
    if five_or_more:
        warnings.append("5以上または0の選択肢番号が見つかった")
        evidence.extend(five_or_more)
    if not choice_four:
        warnings.append("`4. 自由入力` が見当たらない")
    if turn_count and choice_block_count >= max(3, int(turn_count * 0.7)):
        warnings.append("番号つき選択補助が多すぎる可能性")
    if risky:
        warnings.append("候補文が成功/好意/真相を保証している可能性")
        evidence.extend(risky)

    if warnings:
        return Finding(
            label="選択補助",
            status="warn",
            evidence=unique(evidence),
            note="; ".join(warnings),
        )

    return Finding(
        label="選択補助",
        status="ok",
        evidence=choice_four[:1] or evidence,
        note="選択補助は `1,2,3,4` のみ、末尾 `4. 自由入力` として使われている。",
    )


def collect_choice_blocks(lines: list[str]) -> list[tuple[int, list[int], list[str]]]:
    blocks: list[tuple[int, list[int], list[str]]] = []
    index = 0
    choice_line = re.compile(r"^([0-9]+)[.．]\s+")
    while index < len(lines):
        stripped = lines[index].strip()
        match = choice_line.match(stripped)
        if not match or int(match.group(1)) != 1:
            index += 1
            continue

        start_line = index + 1
        numbers: list[int] = []
        block_lines: list[str] = []
        while index < len(lines):
            stripped = lines[index].strip()
            match = choice_line.match(stripped)
            if not match:
                break
            numbers.append(int(match.group(1)))
            block_lines.append(trim(stripped))
            index += 1
        blocks.append((start_line, numbers, block_lines))
    return blocks


def check_case_clarity(lines: list[str]) -> Finding:
    concrete = grep_lines(
        lines,
        [
            r"名刺|社員証|鍵|机|引き出し|会議室|面談|記録|端末|紙|メモ|通知|着信|書類|店|駅|窓口|受け渡し|場所|スマホ",
            r"次に|今夜|明日|まず|先に|確認|見る|聞く|移す|戻る|追う|待つ",
        ],
        limit=6,
    )
    abstract_only = grep_lines(
        lines,
        [r"印|配置|残滓|順番|照合|違和感|謎|何か"],
        limit=6,
    )
    if concrete:
        status = "ok"
        note = "抽象的な謎だけでなく、次に触れる物 / 人 / 場所 / 記録がログに見えている。"
        evidence = concrete[:4]
    elif abstract_only:
        status = "warn"
        note = "抽象語は出ているが、次に触れる具体物や進行条件が薄い可能性がある。current/case.md の handles を確認する。"
        evidence = abstract_only[:4]
    else:
        status = "missing"
        note = "active case の足場になる具体物、人物、場所、記録が自動抽出できない。"
        evidence = []
    return Finding(label="Case clarity / 事件カード足場", status=status, evidence=evidence, note=note)


def grep_lines(lines: list[str], patterns: list[str], *, limit: int | None = None) -> list[str]:
    found: list[str] = []
    combined = re.compile("|".join(f"(?:{pattern})" for pattern in patterns), re.IGNORECASE)
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if combined.search(stripped):
            found.append(trim(stripped))
            if limit is not None and len(found) >= limit:
                break
    return found


def merge_label_lines(lines: list[str]) -> list[str]:
    merged: list[str] = []
    index = 0
    label_pattern = re.compile(r"^(Player|User|プレイヤー|GM|Assistant|Narrator|地の文|描写)[:：]\s*$")
    while index < len(lines):
        stripped = lines[index].strip()
        match = label_pattern.match(stripped)
        if match:
            next_index, next_text = next_nonempty(lines, index + 1)
            if next_index is not None and next_text:
                merged.append(f"{match.group(1)}: {next_text}")
                index = next_index + 1
            else:
                merged.append(stripped)
                index += 1
            continue
        merged.append(lines[index])
        index += 1
    return merged


def next_nonempty(lines: list[str], start: int) -> tuple[int | None, str]:
    for offset, line in enumerate(lines[start:], start=start):
        stripped = line.strip()
        if stripped:
            return offset, stripped
    return None, ""


def collect_save_candidates(lines: list[str]) -> list[str]:
    section_items = extract_section_items(lines, "Save Notes")
    if section_items:
        return section_items[:10]
    patterns = [
        r"約束|秘密|本名|能力|痕跡|後遺症|クロック|フック|コンディション|AFFINITY|bond|Manga Export Candidates",
        r"知らない|伏せる|共有|推測|疑い|確定していない",
    ]
    return unique(grep_lines(candidate_source_lines(lines), patterns, limit=10))


def collect_manga_candidates(lines: list[str]) -> list[str]:
    section_items = extract_section_items(lines, "Manga Candidates")
    if section_items:
        return section_items[:10]
    patterns = [
        r"手|指|スマホ|視線|目|沈黙|震え|涙|笑|背中|扉|窓|雨|夜|光|影|足音",
        r"漫画化|PV|三面図|コマ|見開き|カット|構図",
    ]
    return unique(grep_lines(candidate_source_lines(lines), patterns, limit=10))


def extract_section_items(lines: list[str], heading: str) -> list[str]:
    in_section = False
    items: list[str] = []
    heading_pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.IGNORECASE)
    for line in lines:
        stripped = line.strip()
        if heading_pattern.match(stripped):
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if not in_section or not stripped:
            continue
        if stripped.startswith(("-", "*")):
            stripped = stripped[1:].strip()
        if stripped:
            items.append(trim(stripped))
    return unique(items)


def candidate_source_lines(lines: list[str]) -> list[str]:
    result: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^(Player|User|プレイヤー)[:：]", stripped):
            continue
        if re.match(r"^[0-9]+[.．]\s", stripped):
            continue
        if stripped == "→ どうする？":
            continue
        if stripped.startswith("#"):
            continue
        result.append(stripped)
    return result


def collect_risks(findings: list[Finding]) -> list[str]:
    risks: list[str] = []
    for finding in findings:
        if finding.status == "missing":
            risks.append(f"{finding.label}: evidence missing. {finding.note}")
        elif finding.status == "warn":
            evidence = " / ".join(finding.evidence[:2])
            risks.append(f"{finding.label}: review evidence: {evidence}")
    return risks


def format_findings(findings: list[Finding]) -> str:
    blocks: list[str] = []
    mark = {"ok": "OK", "warn": "WARN", "missing": "MISSING"}
    for finding in findings:
        evidence = format_list(finding.evidence, empty="根拠行なし")
        blocks.append(
            "\n".join(
                [
                    f"### {mark[finding.status]}: {finding.label}",
                    "",
                    finding.note,
                    "",
                    evidence,
                ]
            )
        )
    return "\n\n".join(blocks)


def format_list(items: list[str], *, empty: str) -> str:
    if not items:
        return f"- {empty}"
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


def trim(text: str, *, max_len: int = 180) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


PLAYER_PATTERNS = [
    r"^(Player|User|プレイヤー|あなた|入力)[:：]",
    r"^>",
    r"^\(",
    r"^(gm|ＧＭ)(\s|$)",
    r"^(GM相談|ＧＭ相談)",
]

GM_PATTERNS = [
    r"^(GM|Assistant|Narrator|地の文|描写)[:：]",
    r"^###?\s*(GM|Turn|Scene|シーン)",
]

DIALOGUE_PATTERNS = [
    r"「[^」]+」",
    r"^[^:：]{1,20}[:：]「",
]


if __name__ == "__main__":
    raise SystemExit(main())
