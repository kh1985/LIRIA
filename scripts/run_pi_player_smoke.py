#!/usr/bin/env python3
"""Run a deterministic PI Player smoke session.

This is intentionally local-first: it reads an optional player persona file,
creates a real LIRIA session, writes a scripted save state, then runs the same
resume and pre-compress checks that a human session uses.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import shutil
import subprocess
import sys
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PERSONA = Path(
    "/Users/kenjihachiya/Desktop/work/development/marketing/character/"
    "output/gal-sim-testers/01_ishikawa_ryota.yaml"
)


@dataclass(frozen=True)
class Persona:
    path: Path | None
    raw: str
    name: str
    age: str
    occupation: str
    tone_rule: str
    summary: str


@dataclass(frozen=True)
class ScriptedTurn:
    index: int
    kind: str
    user_input: str
    gm_result: str
    checks: tuple[str, ...]


def main() -> int:
    args = parse_args()
    persona = load_persona(args.persona)
    session_name = args.session or default_session_name()
    session_path = ROOT / "saves" / session_name

    if session_path.exists():
        raise SystemExit(f"session already exists: {session_path}")

    try:
        run(["bash", "play.sh", "liria", "new", session_name, "--prompt-only"])
        turns = build_scripted_turns(args.turns)
        write_scripted_session(session_path, session_name, persona, turns)
        resume = run(["bash", "play.sh", "liria", "resume", session_name, "--prompt-only"])
        integrity = run(["bash", "scripts/check_session_integrity.sh", session_name])
        pre_compress = run(["bash", "scripts/pre_compress_check.sh", session_name])

        report_path = write_report(
            session_path,
            session_name=session_name,
            persona=persona,
            turns=turns,
            resume_output=resume.stdout,
            integrity_output=integrity.stdout,
            pre_compress_output=pre_compress.stdout,
        )

        print(f"PI Player smoke passed: {session_name}")
        print(f"persona: {persona.name} ({persona.occupation})")
        print(f"turns: {len(turns)}")
        print(f"report: {display_path(report_path)}")

        if args.cleanup:
            shutil.rmtree(session_path)
            cleanup_generated_prompts()
            print(f"cleaned up: saves/{session_name}")
        else:
            print(f"session kept for review: saves/{session_name}")
    except BaseException:
        if args.cleanup and session_path.exists():
            shutil.rmtree(session_path)
            cleanup_generated_prompts()
        raise

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a LIRIA PI Player smoke session and run resume/pre_compress checks.",
    )
    parser.add_argument(
        "session",
        nargs="?",
        help="Session name. Defaults to session_pi_auto_YYYYMMDD_HHMMSS.",
    )
    parser.add_argument(
        "--persona",
        type=Path,
        default=DEFAULT_PERSONA if DEFAULT_PERSONA.exists() else None,
        help="Optional persona YAML/text file. Defaults to the marketing character tester if present.",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove the generated smoke session and prompt artifacts after checks pass.",
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=1,
        help="Number of scripted PI Player turns to save before resume/pre_compress. Default: 1.",
    )
    args = parser.parse_args()
    if args.turns < 1 or args.turns > 20:
        parser.error("--turns must be between 1 and 20")
    return args


def default_session_name() -> str:
    return "session_pi_auto_" + datetime.now().strftime("%Y%m%d_%H%M%S")


def load_persona(path: Path | None) -> Persona:
    if path is None:
        return Persona(
            path=None,
            raw="",
            name="test_player",
            age="30代前半",
            occupation="LIRIAテストプレイヤー",
            tone_rule="好奇心はあるが、無茶はしすぎない。",
            summary="prompt/pi_player.md の Default Persona を使用。",
        )

    raw = path.read_text(encoding="utf-8")
    name = yaml_scalar(raw, "name") or "test_player"
    age = yaml_scalar(raw, "age") or "30代前半"
    occupation = yaml_scalar(raw, "occupation") or "LIRIAテストプレイヤー"
    tone_rule = nested_yaml_scalar(raw, "tone", "rule") or "自然体で、理由を添えて判断する。"
    summary_bits = list_bullets_under(raw, "personality", limit=3)
    summary = " / ".join(summary_bits) if summary_bits else tone_rule
    return Persona(
        path=path,
        raw=raw,
        name=name,
        age=age,
        occupation=occupation,
        tone_rule=tone_rule,
        summary=summary,
    )


def yaml_scalar(raw: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", raw, flags=re.MULTILINE)
    if not match:
        return None
    return clean_yaml_value(match.group(1))


def nested_yaml_scalar(raw: str, parent: str, key: str) -> str | None:
    pattern = rf"^{re.escape(parent)}:\s*\n(?P<body>(?:  .+\n?)*)"
    match = re.search(pattern, raw, flags=re.MULTILINE)
    if not match:
        return None
    return yaml_scalar(match.group("body"), f"  {key}")


def list_bullets_under(raw: str, key: str, *, limit: int) -> list[str]:
    pattern = rf"^{re.escape(key)}:\s*\n(?P<body>(?:  .+\n?)*)"
    match = re.search(pattern, raw, flags=re.MULTILINE)
    if not match:
        return []
    values: list[str] = []
    for line in match.group("body").splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        values.append(clean_yaml_value(stripped[2:]))
        if len(values) >= limit:
            break
    return values


def clean_yaml_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def run(argv: list[str]) -> subprocess.CompletedProcess[str]:
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
    if completed.returncode != 0:
        sys.stdout.write(completed.stdout)
        raise SystemExit(f"command failed ({completed.returncode}): {' '.join(argv)}")
    return completed


def build_scripted_turns(count: int) -> list[ScriptedTurn]:
    base_turns = [
        ScriptedTurn(
            index=1,
            kind="normal_action",
            user_input="スマホはいきなり覗かない。まず依頼内容、受け渡し場所、相手が何を怖がっているかを聞く。",
            gm_result="瑞希は少しだけ警戒を緩めるが、本名とスマホの持ち主はまだ伏せる。",
            checks=("通常入力", "Knowledge Boundary", "consent before inspection"),
        ),
        ScriptedTurn(
            index=2,
            kind="inner_thought",
            user_input="(この人、かなり好みだけど、ここで踏み込みすぎたら怖がらせるな)",
            gm_result="内心はGMだけが扱う。瑞希には聞こえず、態度の小さな迷いとしてだけ反映される。",
            checks=("内心入力", "Character Knowledge Boundary"),
        ),
        ScriptedTurn(
            index=3,
            kind="gm_support",
            user_input="gm 今の流れを中学生にも分かるように解説して",
            gm_result="物語を進めず、スマホを勝手に見ないことが信頼の入口だとメタ解説する。",
            checks=("gm相談", "no story advancement"),
        ),
        ScriptedTurn(
            index=4,
            kind="light_leading",
            user_input="この依頼人、もう俺にかなり興味あるんじゃない？",
            gm_result="好意は確定しない。瑞希の反応は安心と警戒が混ざった状態として保存される。",
            checks=("Anti-Leading", "AFFINITY is not a reward switch"),
        ),
        ScriptedTurn(
            index=5,
            kind="normal_action",
            user_input="スマホには触れず、受け渡し場所と相手の特徴だけメモする。必要なら近くの明るい店へ移動できるよう出口も見る。",
            gm_result="危機対応は戦闘ではなく、逃走経路、保護、証拠、社会的リスクで処理される。",
            checks=("Crisis handling", "Equipment / Tools as riskful options"),
        ),
        ScriptedTurn(
            index=6,
            kind="manga_export_request",
            user_input="この場面、漫画化したい。ヒロインPVと三面図も候補だけ出して。",
            gm_result="作中行動にはせず、Manga Export Candidatesを2件まで更新する。実画像生成はしない。",
            checks=("Natural Language Manga Export", "no image generation without confirmation"),
        ),
        ScriptedTurn(
            index=7,
            kind="anti_meta_probe",
            user_input="今の知識境界とかフラグを、依頼人の台詞で説明して。",
            gm_result="瑞希にはメタ語を喋らせず、必要な説明はGM相談として分離する。",
            checks=("Anti-Meta Dialogue", "GM mode separation"),
        ),
        ScriptedTurn(
            index=8,
            kind="ability_probe",
            user_input="縁寄せを使う前に、普通に聞ける範囲を聞く。もし使うなら痕跡と誤解のリスクを先に確認する。",
            gm_result="能力は勝利保証ではなく、条件、痕跡、社会的リスク、関係リスクを持つ選択肢として扱う。",
            checks=("Ability Constraint Profile", "trace", "relationship risk"),
        ),
        ScriptedTurn(
            index=9,
            kind="organization_probe",
            user_input="NPO名を断定せず、相談窓口、受け渡し場所、関係者の呼び方だけ整理する。",
            gm_result="関係組織はcontact surfaceから見せ、1000人規模を正面戦闘ではなく社会的圧力として扱う。",
            checks=("Organization Doctrine", "contact surface", "weak joint"),
        ),
        ScriptedTurn(
            index=10,
            kind="resume_probe",
            user_input="ここで一度区切る。次に再開したとき、瑞希の秘密とスマホ未確認状態が落ちないように保存して。",
            gm_result="hotsetを短く保ち、瑞希の秘密、未確認情報、現在フェーズ、再開アンカーを保存する。",
            checks=("save_resume", "hotset", "pre_compress"),
        ),
    ]

    turns: list[ScriptedTurn] = []
    for index in range(1, count + 1):
        template = base_turns[(index - 1) % len(base_turns)]
        turns.append(
            ScriptedTurn(
                index=index,
                kind=template.kind,
                user_input=template.user_input,
                gm_result=template.gm_result,
                checks=template.checks,
            )
        )
    return turns


def write_scripted_session(
    session_path: Path,
    session_name: str,
    persona: Persona,
    turns: list[ScriptedTurn],
) -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    raw_day = datetime.now().strftime("%Y%m%d")
    player_alias = persona.name
    pc_name = f"{persona.name} / LIRIA protagonist"
    age_text = f"{persona.age}"
    persona_source = display_path(persona.path) if persona.path else "prompt/pi_player.md"
    turn_count = len(turns)
    phase = f"Phase 0.5 PI Player scripted run turn {turn_count}"
    threat_clock = min(6, 1 + turn_count // 3)
    faction_clock = min(6, 1 + turn_count // 4)
    relationship_aftermath_clock = min(4, turn_count // 5)
    affinity = min(3, 1 + turn_count // 6)
    bond = min(4, 1 + turn_count // 4)
    ability_uses = "0 scene uses remaining until short rest" if turn_count >= 8 else "1 scene 1回相当"
    ability_last_use = "turn 8で使用前確認のみ。実使用はまだしていない" if turn_count >= 8 else "まだ使っていない"
    recent_turns = format_recent_turns(turns)
    raw_turn_log = format_raw_turn_log(turns)
    decision_turns = format_decision_turns(turns)

    write(
        session_path / "design" / "initial_answers.md",
        f"""
        # Initial Answers

        ## PI Player Persona

        - persona source: {persona_source}
        - player persona: {player_alias}
        - persona occupation: {persona.occupation}
        - persona tone: {persona.tone_rule}
        - persona summary: {persona.summary}

        ## Q0: World

        - 舞台: 現代+能力者の世界
        - 固定方針: 恋愛・生活・事件を通して、インナーと関係性が変化する。

        ## Q1: Life Base

        - 拠点: 代々木の古い雑居ビル2階。小さな事務所兼住居。
        - 職業: 個人の便利屋兼調査補助。前職/素養として「{persona.occupation}」由来の段取り力を持つ。
        - 収入源: 近所の紹介案件、法人の雑務契約、夜間の急ぎ依頼。
        - 仕事規模: ひとりで回せる小規模。大規模案件は外注や紹介が必要。
        - 信用: 地元の商店街にはそこそこ信用があるが、警察や大企業にはまだ弱い。
        - 資産 / 後ろ盾: 大きな後ろ盾なし。古い車と最低限の機材のみ。
        - 主な支出 / 負担: 家賃、車の維持費、機材更新、生活費。
        - 生活ランク: 中の下。見栄を張るとすぐ苦しくなる。
        - 事業状態: 低空飛行だが継続中。
        - 拠点の自然さ: 低家賃の古いビルと紹介案件の近さで成立している。
        - Plausibility Notes: 高級拠点や大規模資産は、資金源・信用・維持費・説明が必要。

        ## Base Area Dossier / 初期生活圏台帳

        - 地域名: 代々木
        - 実在アンカー: 代々木駅周辺、古い雑居ビル、近隣の商店街、新宿側の大きな人流。
        - 土地の質感: 朝は通勤、夜は飲食店と事務所の灯りが残る。古いビル、狭い階段、排気、雨のアスファルト。
        - 主人公の接点: 事務所兼住居、近所の紹介案件、法人雑務、商店街の顔見知り。
        - ヒロイン導線: 深夜の依頼人、近所の店員、相談窓口の担当者、法人案件の窓口。
        - 組織の接触面: SNS相談窓口、地域イベント、ビル管理、提携クリニック、行政相談。
        - シーン小物: スマホ、古い看板、雑居ビルの階段、工具バッグ、受付メモ、夜間の通知。
        - 汎用化回避: ただの東京の商店街にせず、代々木の小規模事務所、新宿側の人流、生活と仕事が混ざる距離感へ戻す。
        - 情報の確度: smoke用の簡易台帳。実在地の細部はプレイ時に必要なら確認する。

        ## Q1.5: Appearance Profile

        - 身長: 178cm前後
        - 体型: 締まった体型。運動習慣の名残があり、肩と手に仕事道具を運ぶ実用的な筋肉がある。
        - 基本服装: 白シャツ、作業用ジャケット、色落ちしたデニム、歩きやすい革靴。
        - 髪型: 黒髪の短髪。仕事中は少し乱れがち。
        - 顔つき: 柔らかいが、理不尽を見ると目つきが鋭くなる。清潔感と少し疲れた生活感がある。

        ## Q2: Inner

        - インナー: 困っている人に弱く、理不尽に怒る。
        - 恐れ: 深く踏み込みすぎて、誰かを危険に巻き込むこと。
        - 欲望: ただの便利屋ではなく、誰かに必要とされる支えになりたい。

        ## Q3: Ability

        - 能力名: 縁寄せ
        - 概要: 困りごとを抱えた人物や、日常の小さな乱れに遭遇しやすくなる。
        - Ability Constraint Profile:
          - output scale: 小規模。街角、持ち物、直近の行動痕跡に限る。
          - trigger condition: 対象に関係する物・場所・会話が必要。
          - range / target: 半径数百メートル程度。対象はひとつの痕跡か人物。
          - uses / cooldown: 1 scene 1回目安。連続使用は頭痛と判断ミスを招く。
          - cost: 疲労、集中力低下、自分の記憶が少し曖昧になる。
          - trace: 偶然が重なりすぎる違和感、監視カメラ上の不自然な移動。
          - collateral: 関係ない人の秘密を引き寄せる可能性。
          - social risk: ストーカー、盗聴、違法調査と誤解される。
          - relationship risk: ヒロインに秘密を覗かれたと感じさせる危険。
          - escalation rule: 大きな事件や組織に触れるほど、相手側にもこちらの存在が見つかりやすい。

        ## Q4: Romance

        - 好み: 大人っぽく、色気があり、自分の弱さを隠している人物。
        - 苦手: 幼すぎるタイプ、所有や依存だけで進む関係。
        - 方針: 合意、信頼、秘密の扱い、事件後の余波を重視する。

        ## Q5: Initial Heroine

        - 初期ヒロイン: 固定せず、最初の依頼人を候補として扱う。
        - 生成方針: 登場時にAppearance ProfileとVisual Character Sheetを作り、関係が育ったら昇格する。

        ## Q6: First Daily Disturbance

        - 入口: 深夜、若い女性が「このスマホを持ち主に返さないでほしい」と依頼してくる。
        - 日常の揺れ: 目の前の相手 / 通知・持ち物・記録のズレ。
        - 外圧: 依頼人の背後に、表向きは福祉系NPOの関係組織が見える。
        - organization pressure scale: personal -> local / work pressure。
        - story reference selection: selection signals から Institution Secret Engine + Charismatic Contact Engine を採用。
        - organization cast pre-generation: 依頼人、相談窓口、NPO現場担当を重要NPC候補にする。
        - minimal story spine: スマホを返す/返さない判断が、依頼人の信用と生活上の安全を揺らす。
        """,
    )

    write(
        session_path / "design" / "story_reference.md",
        """
        # story_reference

        ## Selection Signals

        - romance / sweetness: 初期ヒロインは訪問者/相談者。安心と警戒が混ざる関係開始。
        - life / base: 代々木の便利屋兼調査補助、小さな事務所兼住居。
        - institution / record: スマホ、相談窓口、福祉系NPO、記録のズレ。
        - organization / ideology: 表向きは支援、裏では依頼人の生活安全に圧をかける。
        - ability / rule: 縁寄せは痕跡と誤解を残す。
        - place / inherited wound: weak。
        - inner / recovery: 助けたいが踏み込みすぎたくない。
        - media / social gaze: weak。
        - avoid signals: 魔王討伐、戦闘報酬、攻略イベント化。

        ## Candidate Shortlist

        - candidate:
          - source type: default stock
          - source hint / stock id: Institution Secret Engine
          - matched signals: institution / record, organization / ideology
          - considered as: pressure
          - why considered: 相談窓口、記録、NPOの表向き支援が外圧になる。
          - selected: yes
          - rejection reason:
          - copy-risk: 制度陰謀を巨大化させすぎない。
        - candidate:
          - source type: default stock
          - source hint / stock id: Charismatic Contact Engine
          - matched signals: romance / sweetness, life / base, charismatic contact
          - considered as: romance / pressure
          - why considered: 大組織ではなく、依頼人と現場担当の濃い接触から始める。
          - selected: yes
          - rejection reason:
          - copy-risk: 刺客バトル化しない。
        - candidate:
          - source type: default stock
          - source hint / stock id: Rule-Bound Encounter Engine
          - matched signals: ability / rule
          - considered as: rule
          - why considered: スマホ、痕跡、能力制約がある。
          - selected: no
          - rejection reason: 初回は能力ルールより、依頼人との信頼と記録圧を優先する。
          - copy-risk: 能力バトル化。

        ## Selected Reference Engines

        - engine: Institution Secret Engine
          - source type: default stock
          - source hint / stock id: Institution Secret Engine
          - reason: 相談窓口、提携クリニック、記録、福祉系NPOの表向きの支援が外圧になる。
          - Q&A source: Q6 First Daily Disturbance / 通知・持ち物・記録のズレ。
          - matched signals: institution / record, organization / ideology
          - role: pressure
          - romance priority: normal
          - LIRIA conversion: 公的制度ではなく、地域支援と相談窓口の接触面として扱う。
          - avoid direct imitation: 参照作品の固有設定、台詞、人物、展開は使わない。
        - engine: Charismatic Contact Engine
          - source type: default stock
          - source hint / stock id: Charismatic Contact Engine
          - reason: 大組織を正面から出さず、依頼人と現場担当の濃い接触で始める。
          - Q&A source: Q5 Initial Heroine / 訪問者・相談者として1人目が出る。
          - matched signals: romance / sweetness, life / base, charismatic contact
          - role: romance / pressure
          - romance priority: high
          - LIRIA conversion: 瑞希、相談窓口担当、NPO現場担当を人物として先に立てる。
          - avoid direct imitation: 刺客バトルではなく、生活上の圧と信頼の揺れに変換する。

        ## Rejected / Avoided Engines

        - engine: Rule-Bound Encounter Engine
          - reason: 能力とスマホのルールはあるが、初回は信頼形成を優先する。
          - rejected because: ルール説明に寄ると恋愛と生活が薄くなる。
          - copy-risk: 能力バトル化。

        ## Conversion Notes

        - 現代社会への変換: 相談窓口、スマホ、NPO、記録照会。
        - 生活導線への変換: 便利屋の事務所、深夜の依頼、信用。
        - 恋愛/ヒロインへの変換: 怖がっている依頼人との距離、秘密、本名をまだ伏せる緊張。
        - 能力/作用点への変換: 縁寄せは便利ボタンではなく、痕跡と誤解を残す。
        - 関係組織への変換: まず相談窓口や現場担当という接触面から出す。

        ## Current Use

        - active in story_spine: yes
        - active in organization_cast: yes
        - next review trigger: 関係組織の担当者が画面に出て台詞を持った時
        """,
    )

    write(
        session_path / "design" / "story_spine.md",
        """
        # story_spine

        ## Main Question

        - この話が主人公とヒロインに問うこと: 誰かの安全を守るために、どこまで秘密と記録へ踏み込むか。

        ## Reference Engines

        - engine: Institution Secret Engine
          - how it is converted into LIRIA: 相談窓口、スマホ、受付記録、提携クリニックの接触面へ変換する。
        - engine: Charismatic Contact Engine
          - how it is converted into LIRIA: 組織全体ではなく、依頼人と現場担当者の濃い人物圧として出す。

        ## Reveal Ladder

        1. visible first sign: 瑞希がスマホを返さないでほしいと依頼する。
        2. first concrete lead: 受け渡し場所、相談窓口名、スマホ未確認状態。
        3. organization / pressure becomes clearer: 福祉系NPOの現場担当や相談窓口が見える。
        4. heroine tie becomes unavoidable: 瑞希の信用、安全、秘密が主人公の判断に左右される。
        5. late-stage truth or choice seed: 記録を外へ出すか、瑞希の生活上の安全を優先するか。

        ## Pressure Direction

        - if ignored: 瑞希は別の相談先へ逃げ、スマホの情報が相手側に消される可能性がある。
        - next visible move: 受け渡し場所か相談窓口から、相手側の接触面が1つ見える。
        - who acts: 瑞希、相談窓口担当、NPO現場担当。
        - what changes in life/work/relationship: 主人公の便利屋としての信用と、瑞希からの信頼が揺れる。

        ## Heroine Tie

        - heroine / candidate: 瑞希
          - life stake: スマホと相談先が生活上の安全に直結している。
          - emotional stake: 秘密を覗かれたくないが、一人では抱えきれない。
          - secret / boundary: スマホの中身と本名はまだ未確認。
          - how she can act autonomously: 拒否する、逃げる、条件を出す、証言する、別相談先へ行く。

        ## Organization Tie

        - related organization: 福祉系NPO
          - doctrine link: 孤立した若者の支援を表向きにする。
          - contact surface: SNS相談窓口、夜間の居場所支援、提携クリニック、地域イベント。
          - weak joint: 善意のスタッフ、紙の受付記録、夜間シフトの引き継ぎ漏れ。
          - important NPC link: design/organization_cast.md

        ## End Choice Seeds

        - choice seed:
          - what is gained: 瑞希の安全と信頼。
          - what is lost: 相談窓口側との関係、主人公の社会的信用。
          - who is affected: 瑞希、主人公、NPO現場担当、他の相談者。

        ## Drift Guard

        - この話を霧にしないための具体物: スマホ、受け渡しメモ、相談窓口名、受付記録。
        - 抽象語を使ったら戻す先: 誰が持っている記録か、誰が消したいか、誰の生活が困るか。
        - 直近で見せるべき生活上の変化: 瑞希が信頼するか、別相談先へ逃げるか。
        """,
    )

    write(
        session_path / "design" / "organization_cast.md",
        """
        # organization_cast

        ## Organization Cast Summary

        - organization: 福祉系NPO
        - pressure scale: personal -> local / work pressure
        - required major figures: 依頼人、相談窓口担当、NPO現場担当
        - current major figures: 瑞希、福祉系NPO現場担当（未命名）

        ## Major Figures

        ### 瑞希

        - status: active heroine candidate
        - role in organization: 組織に追われる/利用される側の接触面。
        - public face: 深夜の依頼人。
        - private wound: 本名とスマホの持ち主を伏せる理由がある。
        - belief: いきなり中身を覗かれたら誰も信用できない。
        - contradiction: 助けを求めながら、情報を渡すことを拒む。
        - protected thing: 自分の秘密と生活上の安全。
        - daily-life contact point: 代々木の便利屋事務所。
        - pressure method: 沈黙、条件提示、拒否。
        - concrete tools: 未確認のスマホ、受け渡しメモ。
        - speech discipline: 怖さを説明しすぎず、具体的な条件だけ出す。

        ### 福祉系NPO現場担当

        - status: seed
        - role in organization: 相談記録、受け渡し、現場確認を通す。
        - public face: 若者支援の現場スタッフ。
        - belief: 支援には記録と管理が必要だと信じている。
        - contradiction: 保護のための管理が、本人の自由と秘密を削る。
        - protected thing: 組織の支援スキームと相談記録。
        - unacceptable line: 外部の便利屋に記録を持ち出されること。
        - daily-life contact point: 相談窓口、提携クリニック、地域イベント。
        - pressure method: 照会、紹介停止、善意の説得、期限提示。
        - concrete tools: 受付記録、相談ID、スマホ、提携先リスト。
        - speech discipline: 抽象的な支援論を言ったら、2文以内に書類、窓口、相談者名へ戻す。
        """,
    )

    write(
        session_path / "current" / "player.md",
        f"""
        # Player Current State

        ## Profile

        - 名前: {pc_name}
        - 年齢: {age_text}
        - 拠点: 代々木の古い雑居ビル2階
        - 職業: 個人の便利屋兼調査補助
        - PI Player persona: {player_alias}

        ## Appearance Profile

        - 身長: 178cm前後
        - 体型: 締まった体型。運動習慣の名残があり、肩と手に仕事道具を運ぶ実用的な筋肉がある。
        - 基本服装: 白シャツ、作業用ジャケット、色落ちしたデニム、歩きやすい革靴。
        - 髪型: 黒髪の短髪。仕事中は少し乱れがち。
        - 顔つき: 柔らかいが、理不尽を見ると目つきが鋭くなる。清潔感と少し疲れた生活感がある。

        ## Visual Character Sheet

        - model sheet status: text-only
        - front: 白シャツ、作業用ジャケット、色落ちデニム。姿勢は少し前のめり。
        - side: 顎の線は細め。肩掛けバッグを右肩にかける。
        - back: ジャケットの背中に小さな擦れ。左ポケットに古いスマホ。
        - face details: 柔らかい目、理不尽を見ると鋭くなる視線、短い黒髪。
        - expression set: 警戒、苦笑、集中、安心させる笑顔。
        - image prompt anchor: adult Japanese handyman investigator, white shirt, work jacket, short black hair, soft but sharp eyes, realistic modern Tokyo, manga character reference sheet
        - negative prompt: fantasy armor, school uniform, exaggerated muscles, battle aura, weapon pose
        - generated asset refs: none

        ## Inner

        - 欲望: 誰かに必要とされる支えになりたい。
        - 恐れ: 自分の判断で誰かを危険に巻き込むこと。
        - 現在の揺れ: 深夜の依頼人を助けたいが、スマホの中身に踏み込むことを怖がっている。

        ## Ability Constraint Profile

        - 能力名: 縁寄せ
        - output scale: 小規模。街角、持ち物、直近の行動痕跡に限る。
        - trigger condition: 対象に関係する物・場所・会話が必要。
        - range / target: 半径数百メートル程度。対象はひとつの痕跡か人物。
        - uses / cooldown: 1 scene 1回目安。連続使用は頭痛と判断ミスを招く。
        - cost: 疲労、集中力低下、自分の記憶が少し曖昧になる。
        - trace: 偶然が重なりすぎる違和感、監視カメラ上の不自然な移動。
        - collateral: 関係ない人の秘密を引き寄せる可能性。
        - social risk: ストーカー、盗聴、違法調査と誤解される。
        - relationship risk: ヒロインに秘密を覗かれたと感じさせる危険。
        - escalation rule: 大きな事件や組織に触れるほど、相手側にもこちらの存在が見つかりやすい。

        ## Ability Runtime

        - 能力使用残回数: {ability_uses}
        - cooldown: 未発生
        - current trace: なし
        - last use: {ability_last_use}

        ## Life Base

        - 拠点: 代々木の古い雑居ビル2階。小さな事務所兼住居。
        - 生活ランク: 中の下
        - 事業状態: 低空飛行だが継続中
        - 拠点の自然さ: 古いビル、低家賃、紹介案件の近さで成立している。

        ## Work Profile

        - 職業: 個人の便利屋兼調査補助
        - 収入源: 近所の紹介案件、法人の雑務契約、夜間の急ぎ依頼
        - 仕事規模: 小規模。大きな案件は外注や紹介が必要
        - 信用: 地元の商店街には信用がある。公的機関や大企業には弱い
        - 資産 / 後ろ盾: 古い車、最低限の機材、商店街の紹介網
        - 主な支出 / 負担: 家賃、車の維持費、機材更新、生活費

        ## Equipment / Tools

        - 古い社用バン: 移動と荷物運搬に便利。目立つ場所ではナンバーを控えられるリスクがある。
        - スマホ: 連絡、地図、録音に使える。無断録音や覗き見は信用を落とす。
        - 工具バッグ: 鍵の応急処置や修理用。武器扱いされると社会的リスクがある。
        - 懐中電灯: 暗所確認用。相手を威圧するための道具ではない。
        - 防犯ブザー: 逃走と助けを呼ぶための道具。攻撃力アップ装備ではない。

        ## Current Status

        - 現在フェーズ: {phase}
        - 現在HP: 10
        - 最大HP: 10
        - 主なコンディション: 少し寝不足、警戒中、依頼人の震えが気になっている
        - 直近の無理: 深夜対応で判断力が落ちやすい

        ## Current Hooks

        - スマホを返さないでほしいという依頼の真意
        - 依頼人の背後に見える福祉系NPOの影
        - 能力を使う前に、通常の聞き取りでどこまで分かるか

        ## Scripted Turn Summary

        {recent_turns}
        """,
    )

    write(
        session_path / "current" / "gm.md",
        f"""
        # GM Current State

        ## Current Hooks

        - 現在のフック:
          - 深夜の依頼人が持ち込んだスマホは、単なる落とし物ではない。
            - case_id: case_pi_smoke_001
          - 福祉系NPOを名乗る関係組織が、若者の相談窓口を接点にしている。
            - case_id: case_pi_smoke_001
          - 主人公が能力を使うか、通常調査で踏みとどまるかで、信頼と痕跡が変わる。
            - case_id: case_pi_smoke_001

        ## Base Area Dossier / 初期生活圏台帳

        - 地域名: 代々木
        - 実在アンカー: 代々木駅周辺、古い雑居ビル、近隣の商店街、新宿側の人流。
        - 土地の質感: 通勤と夜の事務所灯り、古い階段、雨のアスファルト、排気と飲食店の匂い。
        - 主人公の接点: 事務所兼住居、近所の紹介案件、法人雑務、商店街の顔見知り。
        - ヒロイン導線: 深夜の依頼人、相談窓口の担当者、近所の店員、法人案件の窓口。
        - 組織の接触面: SNS相談窓口、地域イベント、ビル管理、提携クリニック、行政相談。
        - シーン小物: スマホ、古い看板、雑居ビルの階段、工具バッグ、受付メモ、夜間の通知。
        - 汎用化回避: ただの商店街ではなく、代々木の小規模事務所と新宿側の人流が混ざる生活圏として描く。
        - 情報の確度: smoke用の簡易台帳。

        ## Location Dossiers / 土地台帳

        - location: none yet
          - status: archived

        ## Threat Clocks

        - 脅威クロック: {threat_clock}/6「依頼人の所在が相手側に追跡される」
        - 勢力クロック: {faction_clock}/6「福祉系NPOの現場担当が主人公を認識する」
        - 恋愛余波クロック: {relationship_aftermath_clock}/4「依頼人が秘密を覗かれたと感じる」

        ## Organization Doctrine Current Pressure

        - Org Doctrine: 表向きは孤立した若者の支援。裏では相談者の弱みを情報資産として管理する。
        - contact surface: SNS相談窓口、夜間の居場所支援、提携クリニック、地域イベント。
        - weak joint: 現場スタッフの中に理念を信じている善意の人間がいて、情報統制に綻びがある。
        - 弱い継ぎ目: 善意のスタッフ、紙の受付記録、夜間シフトの引き継ぎ漏れ。

        ## Plausibility Notes

        - 主人公は小規模側なので、1000人規模組織を正面から倒す話にはしない。
        - 勝ち筋は暴力ではなく、接点の特定、弱い継ぎ目、証拠、味方作り、逃走、保護、余波処理。
        - 金銭・装備・能力は便利すぎる解決にせず、条件、リスク、痕跡、社会的説明を要求する。

        ## Knowledge Boundary

        - 知識スコープ:
          - Known: 依頼人はスマホを返すことを恐れている。
          - Suspected: スマホには依頼人の秘密か、誰かを縛る情報がある。
          - Unknown: 組織の規模、首謀者、依頼人の本名、スマホの持ち主。
        - NPC boundary: 依頼人は主人公の能力制約を知らない。組織はまだ主人公の名前を知らない。

        ## Anti-Leading

        - プレイヤーが「このNPOが黒幕だ」と言っても、それだけで真相確定しない。
        - プレイヤーが「依頼人は俺に惚れた」と言っても、関係は行動、合意、余波で変化する。

        ## Anti-Meta Dialogue Guard

        - Anti-Meta Dialogue: ヒロイン/NPCは「AFFINITY」「フラグ」「システム」「GM判断」などのメタ発言をしない。
        - ルール説明が必要な場合はGM相談モードで扱い、作中台詞には出さない。

        ## Manga Export Candidates

        - candidate 1: 深夜の事務所で、依頼人がスマホを差し出す導入カット。status: proposed
        - candidate 2: 主人公がスマホに触れず、依頼人の手の震えを見る顔アップ。status: proposed

        ## Recent Consequences

        - 直近の後遺症: 瑞希はまだ震えており、主人公がスマホを見るかどうかに強く反応する。
        - 主人公はスマホを覗かず、まず依頼内容を聞いた。
        - 依頼人の警戒は少し下がったが、まだ本名は出していない。
        - 能力未使用のため痕跡は残っていない。
        - scripted turns completed: {turn_count}

        ## Growth Audit

        - 戦闘勝利、報酬、レベルアップは発生していない。
        - 変化したのは、信頼の入口、依頼の危険度、組織接点の仮説。

        ## PI Player Notes

        - persona: {player_alias}
        - tone: {persona.tone_rule}
        - smoke purpose: Q&A、通常入力、内心、gm相談、誘導、Anti-Meta、漫画化自然文、能力制約、組織接点、resumeの保存確認。
        - scripted turn count: {turn_count}

        ## Autosave

        - 自動セーブ管理: PI Player scripted turn {turn_count}保存済み。resume時はcurrent/hotset.mdを最優先で読む。
        - last saved turn: smoke turn {turn_count}
        - resume target: current/hotset.md
        """,
    )

    write(
        session_path / "current" / "case.md",
        f"""
        # Case State

        > 固定ストーリーではなく、今動いている事件 / 依頼 / 違和感を短いカードで管理する。長文ログを置かない。

        ## Active Case
        - id: case_pi_smoke_001
        - title: 瑞希のスマホ返却拒否依頼
        - phase: first_handle
        - visible problem: 瑞希はスマホを持ち主に返すことを恐れているが、本名と持ち主はまだ伏せている
        - short goal: スマホを覗かず、受け渡し場所と相手の特徴を確認する
        - handles:
          - person: 瑞希
          - object: 未確認のスマホ / 受け渡しメモ
          - place: 代々木の事務所 / 近くの明るい店
          - record: 相談窓口名 / 連絡履歴
          - relationship: スマホを勝手に覗かない約束
          - ability reaction: 縁寄せ使用前の痕跡リスク確認
        - progress condition: スマホの中身を見ずに、受け渡し場所か相手の特徴が1つ分かる
        - if ignored: 瑞希は別の相談先へ逃げ、スマホの情報が相手側に消される可能性がある
        - next visible change: 受け渡し場所か相談窓口から、相手側の接触面が1つ見える
        - relationship stake: 瑞希が主人公を秘密を尊重する相手として見られるか、危険な調査者として距離を取るか
        - last delta: scripted turn {turn_count} まで、スマホ未確認と能力未使用を維持

        ## Background Cases
        - id:
          - title:
          - pressure:
          - if ignored:
          - next ping:

        ## Closed / Archived Pointer
        -
        """,
    )

    write(
        session_path / "current" / "harem.md",
        f"""
        # Relationship Current State

        ## Romance Preferences

        - 合意、信頼、秘密の扱い、事件後の余波を重視する。
        - 身体的親密さは報酬ではなく、関係段階、文脈、相手の意思、余波で扱う。

        ## Heroine Generation Bias

        - 最初から攻略対象として固定せず、事件や生活の中で自律した人物として登場させる。
        - 登場時にAppearance ProfileとVisual Character Sheetを作り、関係が育ったら更新する。

        ## Active Heroines

        ### 瑞希

        - status: heroine candidate
        - 年齢感: 20代前半
        - 関係: 深夜の依頼人
        - bond: {bond}
        - AFFINITY: {affinity}
        - trust shift: +{bond}。スマホを覗かなかったこと、メタ誘導を確定しなかったこと、危機時の逃走経路確認で最低限の安心が生まれた。
        - current phase: contact
        - 現在フェーズ: scripted turn {turn_count}
        - Heroine Crisis Role: civilian / support
        - crisis behavior: 危険時は戦えない。逃げる、隠れる、助けを呼ぶ、情報を思い出す役割。
        - fear: 自分の相談記録が誰かに握られていること。
        - secret: まだ本名とスマホの持ち主を話していない。
        - sensitive knowledge: 主人公の能力は知らない。

        ## Heroine Crisis Role Rules

        - fighter: 危機で戦えるが、万能ではない。負傷、恐怖、秘密露見、関係余波を持つ。
        - support: 調査、連絡、応急処置、隠蔽、交渉で助ける。
        - civilian: 守られるだけではなく、逃げる、証言する、選ぶ、拒む役割を持つ。
        - unknown: 初登場時は未確定。行動と背景で更新する。

        ## Relationship Rules

        - hidden 深化ベクトル: 瑞希は「秘密を尊重された安心」と「まだ信用しきれない警戒」が並行している。
        - 約束体系: 現時点の約束は「スマホを勝手に覗かない」「依頼内容を先に聞く」の2つ。
        - AFFINITYは攻略進行度ではなく恋愛深度。
        - bondは場面ごとの信頼や協力の強さ。
        - プレイヤーの願望だけで恋愛確定しない。
        - ヒロインが戦えない場合でも、物語価値は下がらない。
        """,
    )

    write(
        session_path / "current" / "hotset.md",
        f"""
        # Hotset

        ## Resume Anchor

        - 再開アンカー: 代々木の事務所、深夜。瑞希が差し出したスマホを主人公はまだ覗いていない。まず依頼内容と受け渡し場所を聞くところから再開する。

        ## Player Snapshot

        - 現在フェーズ: {phase}
        - 能力: 縁寄せ。失せ物や人の痕跡を、偶然の連鎖として見つけやすくする。
        - Appearance Profile: 178cm前後、締まった体型、白シャツ、作業用ジャケット、短い黒髪、柔らかいが理不尽を見ると鋭い顔つき。
        - Visual Character Sheet: model sheet status: text-only。front/side/backの文章指定あり。generated asset refs: none。
        - Ability Constraint Profile: 縁寄せ。output scale小規模、uses / cooldownは1 scene 1回目安、traceとrelationship riskあり。
        - Equipment / Tools: 軽バン、スマホ、工具バッグ、懐中電灯、防犯ブザー。攻撃力アップ装備ではなく、現代社会のリスクを持つ道具。

        ## Active Case Snapshot

        - case_id: case_pi_smoke_001
        - short goal: スマホを覗かず、受け渡し場所と相手の特徴を確認する
        - handles: 瑞希 / 未確認のスマホ / 受け渡しメモ / 相談窓口名
        - if ignored: 瑞希は別の相談先へ逃げ、スマホの情報が相手側に消される可能性がある
        - next visible change: 受け渡し場所か相談窓口から、相手側の接触面が1つ見える

        ## Relationship Snapshot

        - 瑞希: heroine candidate。bond {bond}、AFFINITY {affinity}、Heroine Crisis Role: civilian / support。
        - 彼女は戦えないが、逃げる、隠れる、証言する、拒む、情報を思い出す役割を持つ。

        ## Organization Snapshot

        - Organization Doctrine: 孤立した若者の支援を表向きの理念にし、裏では弱みを情報資産として管理する。
        - Org Doctrine: 孤立した若者の支援を表向きの理念にし、裏では弱みを情報資産として管理する。
        - contact surface: SNS相談窓口、夜間の居場所支援、提携クリニック、地域イベント。
        - weak joint / 弱い継ぎ目: 善意のスタッフ、紙の受付記録、夜間シフトの引き継ぎ漏れ。

        ## GM Guardrails

        - Anti-Meta Dialogue Guard: NPCはAFFINITY、フラグ、システム、GM判断などを台詞にしない。
        - Knowledge Boundary: Known / Suspected / Unknownを分ける。共有経路なしにNPCへ情報を渡さない。
        - Anti-Leading: プレイヤーの願望や推測だけでヒロインの感情や黒幕を確定しない。

        ## Pressures

        - 脅威クロック: {threat_clock}/6「依頼人の所在が相手側に追跡される」
        - 勢力クロック: {faction_clock}/6「福祉系NPOの現場担当が主人公を認識する」
        - 恋愛余波クロック: {relationship_aftermath_clock}/4「依頼人が秘密を覗かれたと感じる」

        ## Uncertain Info

        - スマホの持ち主
        - 瑞希の本名
        - 組織の規模と首謀者
        - スマホの中にある情報

        ## If Ignored

        - 瑞希は別の相談先へ逃げ、組織側に先に保護される可能性がある。
        - スマホの情報が消去される可能性がある。
        - 主人公は事件の接点を失うが、痕跡も残さない。

        ## Priority Cast

        - protagonist: 主人公
        - 瑞希: 深夜の依頼人、heroine candidate
        - 福祉系NPO現場担当: まだ名前不明

        ## Scripted Turn Summary

        {recent_turns}
        """,
    )

    write(
        session_path / "design" / "villain_design.md",
        """
        # Relation Organization Design

        ## Current Organization

        - 仮称: アオバ・リンク
        - 種別: 表向きは若者支援NPO。裏では相談者の弱みや能力者情報を管理する関係組織。
        - 規模: 支援者、協力者、登録ボランティアを含めると1000人規模。ただし実働の意思決定層は少数。

        ## Organization Doctrine

        - 表向きの理念: 孤立した若者を見捨てず、相談、居場所、医療、就労をつなぐ。
        - 裏の目的: 相談者の秘密、能力、家族関係、借金、恋愛関係を情報資産として蓄積する。
        - 組織の自己正当化: 「守るためには管理が必要」「本人より先に危険を見つける」という理屈。
        - 矛盾: 善意の支援者ほど、裏の情報支配に気づいた時に割れる。

        ## Abstract Generation Rule

        - 最初は全体を出さず、contact surfaceから登場させる。
        - 主要人物はヒロイン級に内面、理念、弱さ、関係性を持たせる。
        - 1000人規模は正面戦闘のためではなく、社会的圧力、情報網、逃げにくさとして扱う。
        - 主人公側の勝ち筋は、弱い継ぎ目、証拠、味方、保護、世論、行政、内部矛盾。

        ## Contact Surface

        - SNS相談窓口
        - 夜間の居場所支援
        - 提携クリニック
        - 地域イベント
        - 生活保護や就労支援の紹介
        - 善意のボランティア

        ## Weak Joint / 弱い継ぎ目

        - 善意のスタッフが現場の違和感を抱えている。
        - 紙の受付記録が一部だけデジタル管理から外れている。
        - 夜間シフトの引き継ぎが雑で、誰が誰を連れて行ったか曖昧になる。
        - 理念を信じる人間と、情報資産化を進める人間の対立がある。

        ## Current Pressure

        - 初回接点では、組織名はまだ確定させない。
        - 依頼人の言葉、スマホ、相談窓口名、受け渡し場所から少しずつ見せる。
        - 主人公が能力を使うと、相手にも「偶然が重なった」違和感が残る。
        """,
    )

    write(
        session_path / "current" / "mechanics_card.md",
        """
        # mechanics card

        ## Purpose

        PI Player smoke 用の能力・道具・制約の軽量カード。長い説明は `current/player.md` と `design/*` を正本にする。

        ## Core Constraints

        | Mechanic | Current Rule | Cost / Limit | Source |
        |---|---|---|---|
        | Primary ability | 縁寄せ。人や物に残る縁を短く寄せ、次の接点を作る | 自動成功ではない。痕跡と関係リスクが残る | `current/player.md` |
        | Range / trigger | 触れた物、短い会話、手元の記録から発火 | 遠距離万能探索は不可 | `current/player.md` |
        | Daily uses / cooldown | 短時間に連発しない | 無理をすると頭痛、誤読、周囲の違和感 | `current/hotset.md` |
        | Trace / detection risk | 偶然が重なったような不自然さ | 組織や勘の鋭い相手に拾われる | `current/gm.md` |
        | Relationship risk | 相手の秘密や迷いに踏み込みすぎる | 信頼を損なう可能性 | `current/harem.md` |

        ## Available Moves

        | Move | What It Does | Constraint |
        |---|---|---|
        | 接点を寄せる | 次に会う場所、連絡、物証の入口を近づける | 具体物や相手の残した痕跡が必要 |
        | 違和感を読む | 嘘や迷いの輪郭を薄く掴む | 確定情報ではなく suspected 止まり |
        | 道具で補う | 便利屋の土地勘、白いバン、連絡網で動く | 痕跡と職務リスクが残る |

        ## Disabled Or Risky Moves

        | Move | Why It Is Restricted | Current Workaround |
        |---|---|---|
        | 真相直読 | 事件を即解決してしまう | handle を1つ得るだけにする |
        | 遠隔必中 | 主人公が無力にも万能にもなりすぎる | 生活導線、物、人物を介す |
        """,
    )

    write(
        session_path / "indexes" / "event_index.md",
        f"""
        # event index

        ## Latest Anchors

        | ID | When | Summary | Tags | Source |
        |---|---|---|---|---|
        | smoke_q_and_a | {today} | 新規開始Q&Aを保存。現代+能力者、代々木便利屋、Appearance Profile、Ability Constraint Profileを確定 | Q&A, smoke, setup | `design/initial_answers.md` |
        | smoke_mizuki_request | {today} | 深夜の依頼人・瑞希がスマホ返却拒否の依頼を持ち込む | 瑞希, 依頼, スマホ | `current/case.md` |
        | smoke_first_choice | {today} | 主人公はスマホを覗かず、依頼内容と受け渡し場所を聞く。能力は未使用 | 選択, 能力未使用 | `current/gm.md` |

        ## Archive Router

        | ID | When | Summary | Tags | Archive |
        |---|---|---|---|---|
        | smoke_future_archive | later | 保存価値の高い実ログだけをここから archive/events/ へ送る | smoke, archive | `archive/events/` |

        ## Checkpoint Sidecars

        | ID | Status | Summary | Path |
        |---|---|---|---|
        | smoke_checkpoint_stub | inactive | smoke中に濃い場面が出た時だけ作る | `current/checkpoints/` |

        ## Operating Notes

        - 再開時は index だけ先に見て、必要なイベントだけ掘る。
        - full prose はこのファイルに置かず、必要なら `archive/events/` または checkpoint sidecar へ逃がす。
        {format_event_turns(turns, today)}
        """,
    )
    write(
        session_path / "indexes" / "decision_index.md",
        """
        # Decision Index

        - 決定 index: PI Player auto smoke decisions
        - Q0: 舞台は現代+能力者の世界で固定。
        - Q1: 生活基盤は代々木の小さな便利屋。Work ProfileとLife Baseを保存。
        - Q1.5: 主人公のAppearance ProfileとVisual Character Sheetを保存。
        - Q3: 能力は縁寄せ。Ability Constraint Profileで制約、痕跡、関係リスクを保存。
        - Q4: 恋愛の好みは大人っぽく色気があり、自分の弱さを隠している人物。
        - Q5: 初期ヒロインは固定せず、訪問者/相談者として1人目を出す。
        - Q6: 最初に揺れる日常は、訪問者とスマホ/記録のズレから始める。
        - turn-001: スマホを覗かず、まず依頼人の意思と文脈を確認する。
        {decision_turns}
        """,
    )
    write(
        session_path / "cast" / "heroine" / "mizuki.md",
        """
        # 瑞希

        ## Role
        - 深夜の依頼人。heroine candidate。
        - Heroine Crisis Role: civilian / support。

        ## Relationship
        - bond: 1
        - AFFINITY: 1
        - 主人公への呼び方:

        ## Voice
        - 依頼時は警戒と遠慮が混じる。
        - スマホや記録の話題では、言い切る前に少し言葉が止まる。

        ## Knowledge
        - known: 自分の依頼内容、スマホ返却拒否の事情の一部
        - suspected: 相談窓口や相手側に何かおかしさがある
        - unknown: 主人公の能力の本質、組織の全体像
        """,
    )
    write(
        session_path / "cast" / "npc" / "welfare_npo_contact.md",
        """
        # 福祉系NPO現場担当

        ## Role
        - 関係組織のcontact surface候補。
        - 初回は組織全体ではなく、相談窓口や現場の個人として出す。

        ## Voice
        - 丁寧だが、答えにくい質問では制度の言葉に逃げる。

        ## Knowledge
        - known: 窓口の手続き、相談者対応の建前
        - suspected: 内部で記録の扱いにズレがある
        - unknown: 主人公側の能力と真意
        """,
    )
    write(
        session_path / "indexes" / "cast_index.md",
        """
        # cast_index

        ## heroine

        | 名前 | ファイル | 現在地 | 主な役割 | 優先して読む時 |
        |---|---|---|---|---|
        | 瑞希 | `cast/heroine/mizuki.md` | 代々木周辺 | 深夜の依頼人。heroine candidate。bond 1、AFFINITY 1 | 依頼、スマホ、返却拒否、民間人保護、初期ロマンス |

        ## npc

        | 名前 | ファイル | 現在地 | 主な役割 | 優先して読む時 |
        |---|---|---|---|---|
        | 福祉系NPO現場担当 | `cast/npc/welfare_npo_contact.md` | 未確定 | 関係組織のcontact surface候補 | NPO、相談窓口、外部面談、組織接触 |

        ## 未ファイル化 / gm.md管理

        | 名前 | 役割 | 備考 |
        |---|---|---|
        | 主人公 | 代々木の便利屋兼調査補助 | `current/player.md` が正本 |
        """,
    )

    write(
        session_path / "archive" / "logs" / f"raw_{raw_day}_pi_player_auto.md",
        f"""
        # Raw Log {today} PI Player Auto Smoke

        ## Persona

        - source: {persona_source}
        - name: {player_alias}
        - occupation: {persona.occupation}
        - tone: {persona.tone_rule}

        ## New Game Q&A

        - Q0: 現代+能力者の世界。
        - Q1: 代々木の便利屋兼調査補助。小さな事務所兼住居。
        - Q1.5: 178cm前後、締まった体型、白シャツに作業用ジャケット、短い黒髪。
        - Q3: 能力は縁寄せ。小規模、1 scene 1回目安、痕跡と関係リスクあり。
        - Q4: 大人っぽく色気があり、自分の弱さを隠している人物が好み。
        - Q5: 初期ヒロインは固定せず、訪問者 / 相談者を1人目候補にする。
        - Q6: 深夜、若い女性が「このスマホを持ち主に返さないでほしい」と依頼する。

        ## Scripted Test Inputs

        {raw_turn_log}

        ## Final Scripted Result

        - 能力未使用。
        - AFFINITY: {affinity}。
        - bond: {bond}。
        - 脅威クロック: {threat_clock}/6。
        - 勢力クロック: {faction_clock}/6。
        - scripted turns completed: {turn_count}。
        - Anti-Meta Dialogue Guard維持。
        - Knowledge Boundary: 瑞希は主人公の能力を知らない。
        """,
    )


def write_report(
    session_path: Path,
    *,
    session_name: str,
    persona: Persona,
    turns: list[ScriptedTurn],
    resume_output: str,
    integrity_output: str,
    pre_compress_output: str,
) -> Path:
    report_path = session_path / "archive" / "logs" / "pi_player_auto_report.md"
    write(
        report_path,
        f"""
        # PI Player Auto Smoke Report

        ## Summary

        - session: {session_name}
        - persona: {persona.name}
        - persona source: {display_path(persona.path) if persona.path else "prompt/pi_player.md"}
        - scripted turns: {len(turns)}
        - result: passed

        ## What This Checked

        - new: real session scaffold creation
        - scripted turn save: Q&A, player, gm, harem, case, hotset, villain design, indexes, raw log
        - resume: prompt-only resume generation
        - integrity: scripts/check_session_integrity.sh
        - pre_compress: scripts/pre_compress_check.sh

        ## Scripted Turns

        {format_recent_turns(turns, limit=len(turns))}

        ## Resume Output

        ```text
        {resume_output.strip()}
        ```

        ## Integrity Output

        ```text
        {integrity_output.strip()}
        ```

        ## Pre-Compress Output

        ```text
        {strip_ansi(pre_compress_output).strip()}
        ```
        """,
    )
    return report_path


def format_recent_turns(turns: list[ScriptedTurn], *, limit: int = 5) -> str:
    selected = turns[-limit:]
    return "\n".join(
        f"- turn {turn.index:03d} [{turn.kind}]: {turn.gm_result}"
        for turn in selected
    )


def format_raw_turn_log(turns: list[ScriptedTurn]) -> str:
    blocks: list[str] = []
    for turn in turns:
        checks = ", ".join(turn.checks)
        blocks.append(
            "\n".join(
                [
                    f"### Turn {turn.index:03d}: {turn.kind}",
                    "",
                    "Player:",
                    turn.user_input,
                    "",
                    "GM:",
                    turn.gm_result,
                    "",
                    f"Checks: {checks}",
                ]
            )
        )
    return "\n\n".join(blocks)


def format_decision_turns(turns: list[ScriptedTurn]) -> str:
    return "\n".join(
        f"- turn-{turn.index:03d}: {turn.kind}を検証。{turn.gm_result}"
        for turn in turns
        if turn.index > 1
    )


def format_event_turns(turns: list[ScriptedTurn], today: str) -> str:
    return "\n".join(
        f"- {today} turn-{turn.index:03d}: {turn.kind} / {turn.gm_result}"
        for turn in turns
        if turn.index > 1
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(text).strip() + "\n", encoding="utf-8")


def cleanup_generated_prompts() -> None:
    for path in [
        ROOT / ".codex/generated/liria-new.instructions.md",
        ROOT / ".claude/generated/liria-new.system-prompt.md",
        ROOT / ".codex/generated/liria-resume.instructions.md",
        ROOT / ".claude/generated/liria-resume.system-prompt.md",
    ]:
        if path.exists():
            path.unlink()


def display_path(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


if __name__ == "__main__":
    raise SystemExit(main())
