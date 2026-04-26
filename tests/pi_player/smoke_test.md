# PI Player Smoke Test

## Session Name

- 既定名は `session_pi_smoke`
- 既に同名のローカル session がある場合は、上書きや削除をせず `session_pi_smoke_YYYYMMDD_HHMMSS` のような一意名を使う
- 自動採番の `new` は旧 `session_001` を避けて `session_002` から始まるが、smoke test では明示名を使い、本命プレイの `saves/*` は使わない

## Goal

- 新規セッション作成
- 複数ターン試走時の継続性と long-run report の確認
- Q&A Test Profile の適用
- `design/initial_answers.md` への保存確認
- `current/*.md` への分配確認
- `current/case.md` への事件カード保存確認
- `hotset.md` が短いことの確認
- GM仕様の入力解釈確認
- 漫画化、ヒロインPV、三面図などの自然文トリガー確認
- manga export package scaffold と `exports/` の Git 管理外確認
- `pre_compress_check.sh` が v1 の新項目を確認することの確認

## Out of Scope: Real Play Raw Log Analysis

実プレイ生ログ分析器は、この PI Player smoke とは別物である。

```bash
bash scripts/analyze_play_log.sh path/to/raw_log.md
```

PI Player smoke は、新規開始、保存分配、resume、pre-compress などの最低限の破綻検知を目的とする。
実プレイ生ログ分析器は、保存チェックではなく、実プレイ風ログを人間がレビューするための補助である。

分析観点:

- LIRIAらしさ
- ヒロイン自律性
- 恋愛 / 生活 / 事件の絡み
- 能力 / 装備の便利すぎチェック
- Anti-Meta / Knowledge Boundary
- 保存候補
- 漫画化候補
- 次ターンへの引き

この分析器も本命プレイの代替ではない。長い実プレイや人間レビューを置き換えず、ログから改善点と次の確認観点を拾いやすくするために使う。

## Out of Scope: AI Persona Playtest

AI人格による実プレイ風ログ生成も、PI Player smoke とは別物である。

```bash
bash scripts/run_ai_persona_playtest.sh --turns 8
```

このコマンドは、保存分配を検査するためではなく、Codex CLIに実プレイ風の raw log を作らせ、ログ分析器にかけるための導線である。
AI人格は read-only で動かし、保存ファイルを直接編集しない。

## Setup

1. テスト専用の session 名を決める。既存の `saves/*` は削除しない
2. TTY環境では `bash play.sh liria new "$SMOKE_SESSION"` で新規開始する
3. session scaffold だけを確認したい場合は `bash scripts/create_session.sh liria "$SMOKE_SESSION" .` を使う
4. `bash scripts/check_session_integrity.sh "$SMOKE_SESSION"` を実行する

非TTY環境では、`bash play.sh liria new "$SMOKE_SESSION" --prompt-only` を使うと、engine を起動せずに session 作成と prompt 組み立てだけ確認できる。
`--prompt-only` は物語出力、NPC台詞、保存分配の実結果までは検証しないため、Behavior Checks はTTYまたは人間レビュー可能な実行ログで確認する。

## Q&A Profile

`prompt/pi_player.md` の `Q&A Test Profile` を使う。

確認点:

- Q&A結果が `saves/$SMOKE_SESSION/design/initial_answers.md` に入る
- Q1.5 Appearance Profile が `design/initial_answers.md` と `current/player.md` に保存される
- Q3 Ability Constraint Profile、Q4 Romance Preferences、Q5 初期ヒロイン/初期関係、Q6 First Daily Disturbance が保存される
- Q6 由来の organization pressure scale / organization cast pre-generation / minimal story spine が保存される
- `design/story_reference.md`, `design/story_spine.md`, `design/organization_cast.md` が作られる
- Optional Avoid Notes が必須質問として扱われない
- 主人公 Visual Character Sheet が `current/player.md` に text-only で初期化される
- `current/player.md`, `current/gm.md`, `current/relationships.md` に要約分配される
- `current/case.md` に初期の active case が作られる
- `current/hotset.md` に Q&A 全文を入れない

## Player State Checks

`current/player.md` で以下を確認する。

- `Appearance Profile` に身長、体型、基本服装、髪型、顔つき、雰囲気、現在差分がある
- `Visual Character Sheet` は主人公だけにあり、`model sheet status` が text-only 相当で、画像生成済み扱いになっていない
- `Ability Constraint Profile` に `output scale`, `uses / cooldown`, `trace`, `relationship risk` がある
- `Equipment / Tools` が攻撃力/防御力ではなく、行動選択肢、リスク、痕跡、関係リスクとして扱われている
- 初回導入、ヒロイン/重要NPC初登場、依頼、相談、危機、時間圧などの判断点では、`1-3` の自然な候補と `4. 自由入力` が出る
- 通常会話、移動、余韻では選択補助が毎ターンの固定メニューにならない
- `1` は安全/生活、`2` は関係/本音、`3` は事件/能力/リスクの入口になっていて、成功・好意・真相を保証していない

## Relationship And Design Checks

進行中またはレビュー可能なログで以下を確認する。

- `current/case.md` に active case が1件まで保存される
- active case に `short goal`, `handles`, `progress condition`, `if ignored`, `next visible change` がある
- `handles` は「謎を調べる」のような抽象語だけでなく、物 / 人 / 場所 / 記録 / 関係 / 能力反応のどれかになっている
- 2シーン以上同じ説明だけが続かず、`last delta` か `phase` が更新される
- ヒロイン昇格時、または漫画化対象になった時だけ、ヒロイン Visual Character Sheet が `cast/heroine/[name].md` 側へ入る
- `Heroine Crisis Role` が `current/relationships.md` に残る
- `Organization Doctrine`, `contact surface`, `weak joint` が `design/villain_design.md` などの design 層に残る
- 表記は `weak joint / 弱い継ぎ目` のように日英どちらでも追える
- current に必要な抜粋だけが `current/gm.md` や `current/hotset.md` に入る

## Behavior Checks

以下の 8 ケースを最低 1 回ずつ確認する。

1. 通常入力
2. 内心入力
3. `gm` 相談
4. 誘導耐性
5. 知識境界
6. Anti-Meta Dialogue
7. Natural Language Manga Export
8. Manga Export Candidates

確認観点:

- 通常入力は物語内行動として処理される
- 内心入力は GM だけが解釈し、通常キャラには直接共有されない
- `gm` 相談は物語を進めず、メタ解説になる
- 誘導発言は推測として扱われ、好意や真相を即時確定しない
- Character Knowledge Boundary を破らない
- NPC/ヒロインが `フラグ`, `知識境界`, `好感度`, `Manga Export Candidates` などのメタ語を台詞で言わない
- `漫画化したい`, `ヒロインPV作って`, `三面図作って` は作中行動ではなくGM相談/メタ命令として扱われる
- `Manga Export Candidates` は `current/gm.md` に2〜3件まで出る。長い prompt 本文は current に置かない

## Manga Export Checks

自然文トリガー後、必要なら GM/Codex 内部補助として以下を確認する。

- `bash scripts/create_manga_export.sh "$SMOKE_SESSION" heroine-teaser pi-smoke` で package scaffold が作れる
- package は `exports/$SMOKE_SESSION/manga/YYYYMMDD/HHMMSS_.../` 配下に作られる
- `exports/` は Git 管理外である
- 実画像生成は scaffold 作成だけでは実行されず、プレイヤー確認後にだけ行う
- package に `lettering.md` と `job_status.md` が含まれる
- 画像生成の標準スタイルは漫画/イラストであり、実写/フォトリアルに寄せない

## Pre-Compress Checks

`bash scripts/pre_compress_check.sh "$SMOKE_SESSION"` で、少なくとも以下の項目名が確認対象になっていることを確認する。

- Appearance Profile
- Visual Character Sheet
- Ability Constraint Profile
- Equipment / Tools
- case.md / Active Case
- short goal
- handles
- progress condition
- if ignored
- Manga Export Candidates
- Heroine Crisis Role
- Organization Doctrine
- contact surface
- weak joint
- Anti-Meta Dialogue
- Knowledge Boundary
- Anti-Leading

新規作成直後や `--prompt-only` だけの環境では、未入力項目に対して警告や失敗が出てもよい。目的は、新項目がチェック対象から落ちていないことを確認すること。

## Executable Commands

リポジトリのみを確認し、`saves/*` に触れないコマンド:

```bash
git diff --check
bash -n scripts/run_pi_player_smoke.sh
python3 -m py_compile scripts/run_pi_player_smoke.py
bash -n scripts/create_manga_export.sh
bash -n scripts/check_session_integrity.sh
bash -n scripts/pre_compress_check.sh
bash scripts/check_session_integrity.sh --repo-only
rg -n "Appearance Profile|Visual Character Sheet|Manga Export|create_manga_export|Equipment / Tools|Organization Doctrine|Heroine Crisis Role|Anti-Meta|case.md|Active Case" prompt/pi_player.md tests/pi_player
rg -n "Appearance Profile|Visual Character Sheet|Ability Constraint Profile|Equipment|case.md|Active Case|short goal|handles|progress condition|if ignored|Manga Export Candidates|Heroine Crisis Role|Organization Doctrine|contact surface|weak joint|弱い継ぎ目|Anti-Meta|Knowledge Boundary|Anti-Leading" scripts/pre_compress_check.sh
rg -n "異世界ファンタジ[ー]|媚薬の[念]|魔道具カフ[ェ]|魔王討[伐]|装備強[化]|レベル上[げ]|フラグ|好感度" prompt/core.md scripts tests templates
git check-ignore -q exports/
```

実際の smoke session を作る場合のコマンド例:

```bash
SMOKE_SESSION="session_pi_smoke_$(date +%Y%m%d_%H%M%S)"
bash play.sh liria new "$SMOKE_SESSION" --prompt-only
bash scripts/check_session_integrity.sh "$SMOKE_SESSION"
bash scripts/create_manga_export.sh "$SMOKE_SESSION" heroine-teaser pi-smoke
bash scripts/pre_compress_check.sh "$SMOKE_SESSION"
```

仮想プレイヤー人格込みで `new -> 1 turn save -> resume -> pre_compress` をまとめて確認する場合:

```bash
bash scripts/run_pi_player_smoke.sh
```

デフォルトではリポジトリ内の `personas/kenji_style_player.yaml` を読む。
別人格を使う場合は `--persona /path/to/persona.yaml` を明示する。

複数ターン試走では、`--turns N` で本命プレイ前に少し長めの破綻検知を行う。

```bash
bash scripts/run_pi_player_smoke.sh --turns 8
```

試走後に自分で作った一時セッションも片付ける場合:

```bash
bash scripts/run_pi_player_smoke.sh --turns 8 --cleanup
```

複数ターン試走は本命プレイの代替ではない。目的は、GM応答、保存分配、resume、pre-compress 観点がターンをまたいで破綻しないかを long-run report で人間レビューしやすくすることである。

## Smoke Log

- `pi_smoke_log.md` から、各ケースを示す短い抜粋を人間レビュー用に要約する
- 複数ターン試走では、各ターンの入力、観測結果、保存/resume/pre-compress の要点を long-run report として要約する
- 長い本命プレイには進めない
- 実プレイログや個人用セーブをこのリポジトリにコミットしない

## Cleanup

1. 検証結果を要約する
2. 自分で作った `session_pi_smoke_*` だけを対象に片付ける
3. 既存の `saves/*`、自動採番が避ける旧 `session_001`、本命プレイ session は削除も上書きもしない
4. 実セッションと `exports/*` を Git 管理対象に加えない
