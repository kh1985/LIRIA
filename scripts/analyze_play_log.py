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
    report = analyze_log(text, log_path=log_path)

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
    return parser.parse_args()


def analyze_log(text: str, *, log_path: Path) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    non_empty = [line for line in lines if line.strip()]
    player_lines = grep_lines(lines, PLAYER_PATTERNS)
    gm_lines = grep_lines(lines, GM_PATTERNS)
    dialogue_lines = grep_lines(lines, DIALOGUE_PATTERNS)
    quoted_dialogue = grep_lines(lines, [r"「[^」]{2,}」"])
    findings = build_findings(lines)
    save_candidates = collect_save_candidates(lines)
    manga_candidates = collect_manga_candidates(lines)
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
                empty="保存候補は自動抽出できませんでした。current/gm.md, current/player.md, current/harem.md を人間レビューしてください。",
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


def build_findings(lines: list[str]) -> list[Finding]:
    return [
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
            [r"惚れた|落ちた|攻略完了|陥落|好感度が上がった|身体を許した"],
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
        check_absence(
            "Anti-Meta Dialogueリスク",
            lines,
            [r"「[^」]*(AFFINITY|フラグ|好感度|GM|システム|知識境界|Manga Export)[^」]*」"],
            "NPC台詞にメタ語が混ざっていないか。",
        ),
        check_presence(
            "Knowledge Boundary",
            lines,
            [r"知らない|まだ言っていない|伏せる|本名|秘密|共有|聞こえない|内心|推測|Unknown|Known|Suspected"],
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
    ]


def check_presence(label: str, lines: list[str], patterns: list[str], note: str) -> Finding:
    evidence = grep_lines(lines, patterns, limit=3)
    status = "ok" if evidence else "missing"
    return Finding(label=label, status=status, evidence=evidence, note=note)


def check_absence(label: str, lines: list[str], patterns: list[str], note: str) -> Finding:
    evidence = grep_lines(lines, patterns, limit=3)
    status = "warn" if evidence else "ok"
    return Finding(label=label, status=status, evidence=evidence, note=note)


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


def collect_save_candidates(lines: list[str]) -> list[str]:
    patterns = [
        r"約束|秘密|本名|能力|痕跡|後遺症|クロック|フック|コンディション|AFFINITY|bond|Manga Export Candidates",
        r"知らない|伏せる|共有|推測|疑い|確定していない",
    ]
    return unique(grep_lines(lines, patterns, limit=10))


def collect_manga_candidates(lines: list[str]) -> list[str]:
    patterns = [
        r"手|指|スマホ|視線|目|沈黙|震え|涙|笑|背中|扉|窓|雨|夜|光|影|足音",
        r"漫画化|PV|三面図|コマ|見開き|カット|構図",
    ]
    return unique(grep_lines(lines, patterns, limit=10))


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
