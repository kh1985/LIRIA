#!/usr/bin/env python3
"""Let an AI persona produce a real-play-like LIRIA raw log.

This runner is intentionally safer than a full autonomous player. It creates a
real session scaffold, reuses the LIRIA launch prompt, asks Codex CLI to produce
a play log only, then optionally analyzes that log. The model must not edit save
files; save/resume checks remain separate.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
LOCAL_DEFAULT_PERSONA = ROOT / "personas" / "kenji_style_player.yaml"
MAX_TURNS = 1000
NEW_SYSTEM_PROMPT_FILES = [
    "LIRIA.md",
    "prompt/core.md",
    "prompt/gm_policy.md",
    "prompt/core_newgame.md",
    "prompt/case_engine.md",
    "prompt/runtime.md",
    "prompt/combat.md",
    "prompt/villain_engine.md",
    "prompt/romance.md",
    "prompt/save_resume.md",
]
RESUME_SYSTEM_PROMPT_FILES = [
    "LIRIA.md",
    "prompt/core.md",
    "prompt/gm_policy.md",
    "prompt/case_engine.md",
    "prompt/runtime.md",
    "prompt/combat.md",
    "prompt/villain_engine.md",
    "prompt/romance.md",
    "prompt/save_resume.md",
]


def main() -> int:
    args = parse_args()
    session_name = args.session or default_session_name()
    session_path = ROOT / "saves" / session_name
    session_mode = resolve_session_mode(session_path)
    prompt_mode = "new" if session_mode == "new-retry" else session_mode

    prepare_session(session_name=session_name, session_path=session_path, session_mode=session_mode)

    persona_text = read_optional(args.persona)
    liria_prompt = read_liria_prompt(prompt_mode)
    play_prompt = build_play_prompt(
        session_name=session_name,
        session_path=session_path,
        liria_prompt=liria_prompt,
        persona_path=args.persona,
        persona_text=persona_text,
        turns=args.turns,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = session_path / "archive/logs" / f"raw_{timestamp}_ai_persona_playtest.md"
    prompt_path = session_path / "archive/logs" / f"prompt_{timestamp}_ai_persona_playtest.md"
    analysis_path = session_path / "archive/logs" / f"analysis_{timestamp}_ai_persona_playtest.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(play_prompt, encoding="utf-8")

    try:
        if args.dry_run:
            print(f"dry-run prompt: {display_path(prompt_path)}")
            print(f"session kept for review: saves/{session_name}")
            return 0

        timeout_seconds = args.timeout_seconds or default_timeout_seconds(args.turns)
        run_codex(
            play_prompt,
            log_path=log_path,
            model=args.model,
            timeout_seconds=timeout_seconds,
        )
        print(f"AI persona play log: {display_path(log_path)}")

        if args.analyze:
            run(
                [
                    "bash",
                    "scripts/analyze_play_log.sh",
                    str(log_path),
                    "-o",
                    str(analysis_path),
                    "--expected-turns",
                    str(args.turns),
                ]
            )
            print(f"analysis report: {display_path(analysis_path)}")
    finally:
        cleanup_generated_prompts()

    print(f"session kept for review: saves/{session_name}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a real-play-like LIRIA raw log with an AI persona via Codex CLI.",
    )
    parser.add_argument(
        "session",
        nargs="?",
        help="Session name. Defaults to session_ai_playtest_YYYYMMDD_HHMMSS.",
    )
    parser.add_argument(
        "--persona",
        type=Path,
        default=LOCAL_DEFAULT_PERSONA,
        help="Persona YAML/text file. Defaults to personas/kenji_style_player.yaml.",
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=8,
        help=f"Number of play turns to generate. Must be between 1 and {MAX_TURNS}. Default: 8.",
    )
    parser.add_argument("--model", help="Optional Codex model override.")
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        help="Codex exec timeout. Defaults to max(300, turns * 60).",
    )
    parser.add_argument("--no-analyze", dest="analyze", action="store_false", help="Skip analyze_play_log after generation.")
    parser.add_argument("--dry-run", action="store_true", help="Create the session and prompt, but do not call Codex.")
    parser.set_defaults(analyze=True)
    args = parser.parse_args()
    if args.turns < 1 or args.turns > MAX_TURNS:
        parser.error(f"--turns must be between 1 and {MAX_TURNS}")
    if args.timeout_seconds is not None and args.timeout_seconds < 60:
        parser.error("--timeout-seconds must be at least 60")
    if args.persona is not None:
        args.persona = resolve_persona_path(args.persona)
    return args


def default_session_name() -> str:
    return "session_ai_playtest_" + datetime.now().strftime("%Y%m%d_%H%M%S")


def resolve_persona_path(path: Path) -> Path:
    if path.is_absolute() or path.exists():
        return path
    repo_relative = ROOT / path
    if repo_relative.exists():
        return repo_relative
    return path


def read_optional(path: Path | None) -> str:
    if path is None:
        return "名前: test_player\n方針: 好奇心はあるが、無茶はしすぎない。"
    return path.read_text(encoding="utf-8")


def resolve_session_mode(session_path: Path) -> str:
    if not session_path.exists():
        return "new"
    if has_completed_ai_persona_log(session_path):
        print(f"session exists; resuming completed playtest scaffold: {display_path(session_path)}")
        return "resume"
    print(f"session exists without a completed AI play log; retrying as new-game playtest: {display_path(session_path)}")
    return "new-retry"


def has_completed_ai_persona_log(session_path: Path) -> bool:
    logs_dir = session_path / "archive/logs"
    if not logs_dir.exists():
        return False
    for log_path in sorted(logs_dir.glob("raw_*_ai_persona_playtest.md")):
        text = log_path.read_text(encoding="utf-8", errors="replace")
        if "## Play Log" in text and "## Save Notes" in text and "## Manga Candidates" in text:
            return True
    return False


def prepare_session(*, session_name: str, session_path: Path, session_mode: str) -> None:
    if session_mode in {"new", "resume"}:
        run(["bash", "play.sh", "liria", session_mode, session_name, "--prompt-only"])
        return

    if session_mode != "new-retry":
        raise SystemExit(f"unknown session mode: {session_mode}")

    relationships_path = session_path / "current/relationships.md"
    if not relationships_path.exists() and (session_path / "current/harem.md").exists():
        relationships_path = session_path / "current/harem.md"

    required_paths = [
        session_path / "session.json",
        session_path / "current/player.md",
        session_path / "current/gm.md",
        relationships_path,
        session_path / "current/hotset.md",
        session_path / "design/initial_answers.md",
    ]
    missing = [display_path(path) for path in required_paths if not path.exists()]
    if missing:
        raise SystemExit("existing session is not a valid scaffold:\n- " + "\n- ".join(missing))

    case_path = session_path / "current/case.md"
    if not case_path.exists():
        template = ROOT / "templates/session/current/case.md"
        if template.exists():
            case_path.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")


def read_liria_prompt(prompt_mode: str) -> str:
    generated_prompt = ROOT / f".codex/generated/liria-{prompt_mode}.instructions.md"
    if generated_prompt.exists():
        return generated_prompt.read_text(encoding="utf-8")

    if prompt_mode == "new":
        prompt_files = NEW_SYSTEM_PROMPT_FILES
    elif prompt_mode == "resume":
        prompt_files = RESUME_SYSTEM_PROMPT_FILES
    else:
        raise SystemExit(f"unknown prompt mode: {prompt_mode}")

    return "\n\n".join((ROOT / path).read_text(encoding="utf-8") for path in prompt_files)


def default_timeout_seconds(turns: int) -> int:
    return max(300, turns * 60)


def build_play_prompt(
    *,
    session_name: str,
    session_path: Path,
    liria_prompt: str,
    persona_path: Path | None,
    persona_text: str,
    turns: int,
) -> str:
    persona_source = str(persona_path) if persona_path else "prompt/pi_player.md default persona"
    return "\n".join(
        [
            "# Task",
            "",
            "あなたは LIRIA の実プレイ風ログ生成担当です。",
            "以下の LIRIA system prompt と AIプレイヤー人格を前提に、プレイヤーが実際に遊んだような生ログを生成してください。",
            "",
            "重要:",
            "- ファイル編集、保存ファイル更新、コマンド実行はしない。",
            "- 出力は raw play log の Markdown だけにする。",
            "- scripted smoke のように同じ検査パターンを繰り返さない。",
            "- AIプレイヤー人格やprompt内の例文に出てくる固有名詞、旧セッションの人物名、旧拠点名を、現在sessionの正本として流用しない。",
            "- prompt内の例文は構造説明であり、職業、小物、導入パターン、事件構造をそのまま現在sessionの正本として流用しない。",
            "- 最初のきっかけは、Q1-Q6 / Q1.5 / Optional Avoid Notes に相当する `生活導線 + 初期圧 + 小物や信号 + 社会の窓口 + ヒロイン/NPCの利害` から新しく合成する。",
            "- Q6の答えから内部的に organization pressure scale / organization cast pre-generation / minimal story spine を作り、重要NPCや関係組織を薄い霧にしない。",
            "- 開始地点や遠出先には、短い Base Area Dossier / Location Dossier を内部で作り、地域名、実在アンカー、土地の質感、主人公の接点、シーン小物、汎用化回避を本文に反映する。",
            "- 直近ログや例文に寄った `クリーニング店` `白い上着` `預かり札` `白い軽バン` `失踪だけで始まる導入` は、プレイヤーが明示しない限り避ける。",
            "- `怜` `真凛` `澪` `月読堂` は旧inner-galge由来または例文由来の名前として扱い、新規playtestでは使わない。必要ならLIRIA v1用に新規キャラ名と新規拠点名を作る。",
            "- 1ターンごとに Player 入力と GM 応答を書く。",
            "- GM応答には、地の文、ヒロイン/NPCの自律反応、生活感、事件の外圧を入れる。",
            "- Save Notes には active case の `visible problem / short goal / handles / progress condition / if ignored / next visible change` が分かる短い要約を入れる。",
            "- 謎を増やす時は、既存の手がかり、人物、場所、記録、関係のどれに繋がるかを本文で分かるようにする。",
            "- 敵幹部、関係組織の主要人物、ルート鍵NPC、scene lead NPCを出す時は、内部的に Major Figure Dossier を作る。role、public face、belief、contradiction、wants this scene、knows/suspects/unknown、can/cannot、speech rule を持たせる。",
            "- 重要NPCに抽象語を喋らせる場合は、2文以内に具体物、人物、手続きへ戻す。プレイヤーが `意味が分からない` と感じる霧の会話にしない。",
            "- ヒロイン候補、敵幹部、関係組織の主要人物、ルート鍵NPCの初登場では、頭から爪先まで全身を詳細に描写する。",
            "- 全身描写には髪、顔、体型、首筋、鎖骨、胸元、腰、脚、服装、足元、匂い、仕草、視線が引っかかる外見フックを入れる。",
            "- 成人ヒロイン候補は、下品な採寸ではなく、服の張り方、首筋、鎖骨、腰、脚、歩き方などで恋愛ゲームとしての身体的魅力を出す。",
            "- 正確な身長、3サイズ、体重、カップ数は本文に出さない。身長は目測/相対で描き、必要ならGM-only裏設定として扱い、(gm)相談で聞かれた時だけメタ回答する。",
            "- 好意、真相、黒幕、身体的親密さをプレイヤー願望だけで確定しない。",
            "- 能力や装備は便利すぎる解決にせず、条件、痕跡、誤解、関係リスクを残す。",
            "- NPC/ヒロインの台詞に AFFINITY、フラグ、GM、システム、知識境界などのメタ語を入れない。",
            "- 初回導入、ヒロイン候補/重要NPC/敵幹部の初登場、依頼、相談、危機、時間圧、複数分岐では、GM応答の末尾に必ず `1-3` の自然な候補と `4. 自由入力` を出す。1は安全/生活、2は関係/本音、3は事件/能力/リスク。通常会話、移動、余韻では毎ターン固定メニュー化しない。",
            "- 漫画化や画像生成の出力は、ユーザーが明示しない限り Japanese manga / anime-style illustration にする。実写、フォトリアル、映画スチル、3D render へ寄せない。",
            "- 漫画化したくなる手元、視線、沈黙、距離、背景、小物を自然に混ぜる。",
            "- 最後に Save Notes と Manga Candidates を短く付ける。",
            "",
            f"session: {session_name}",
            f"session_path: {display_path(session_path)}",
            f"turns: {turns}",
            f"persona_source: {persona_source}",
            "",
            "# Output Format",
            "",
            "```md",
            f"# Raw Log: {session_name} AI Persona Playtest",
            "",
            "## Persona Summary",
            "",
            "## Play Log",
            "",
            "### Turn 001",
            "",
            "Player:",
            "...",
            "",
            "GM:",
            "...",
            "",
            "## Save Notes",
            "",
            "## Manga Candidates",
            "```",
            "",
            "# AI Player Persona",
            "",
            persona_text.strip(),
            "",
            "# LIRIA Prompt",
            "",
            liria_prompt,
        ]
    )


def run_codex(
    prompt: str,
    *,
    log_path: Path,
    model: str | None,
    timeout_seconds: int,
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    argv = [
        "codex",
        "exec",
        "-C",
        str(ROOT),
        "-s",
        "read-only",
        "--output-last-message",
        str(log_path),
        "-",
    ]
    if model:
        argv[2:2] = ["--model", model]

    try:
        completed = subprocess.run(
            argv,
            cwd=ROOT,
            input=prompt,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        if exc.stdout:
            sys.stdout.write(exc.stdout if isinstance(exc.stdout, str) else exc.stdout.decode("utf-8", errors="replace"))
        raise SystemExit(
            f"codex exec timed out after {timeout_seconds} seconds. "
            "Retry with a larger --timeout-seconds value or fewer --turns."
        ) from exc

    if completed.returncode != 0:
        sys.stdout.write(completed.stdout)
        raise SystemExit(f"codex exec failed ({completed.returncode})")
    if not log_path.exists() or not log_path.read_text(encoding="utf-8", errors="replace").strip():
        log_path.write_text(completed.stdout, encoding="utf-8")


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


def cleanup_generated_prompts() -> None:
    for path in [
        ROOT / ".codex/generated/liria-new.instructions.md",
        ROOT / ".codex/generated/liria-resume.instructions.md",
        ROOT / ".claude/generated/liria-new.system-prompt.md",
        ROOT / ".claude/generated/liria-resume.system-prompt.md",
    ]:
        if path.exists():
            path.unlink()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
