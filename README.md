# LIRIA

コンセプト整理: [CONCEPT.md](CONCEPT.md)

LIRIA は、恋愛・生活・事件を通して、プレイヤーのインナーと関係性が変化していく AI TRPG 型恋愛シミュレーションです。
このリポジトリは、そのセッションをローカルに開始・継続するための実行基盤であり、実プレイ済みセーブや個人ログを含めず、`templates/session/` の雛形からローカルに session を作成して使います。

## セットアップ

1. このリポジトリを clone
2. `Claude CLI` または `Codex CLI` を使える状態にする
3. まず `./liria` または `bash play.sh` を実行する
4. 表示された日本語メニューで `新規スタート` / `続きから` を選ぶ

新規開始時は Q&A で生活基盤 / 外見 / インナー / 能力 / 恋愛の好み / 初期関係 / 最初に揺れる日常を初期化します。
GMの基本原則、相談モード、入力意味論は `prompt/gm_policy.md` にあります。
AIプレイ検証系は、回帰確認用の `PI Player`、実プレイ風ログ生成用の `AI Persona Playtest`、複数persona上位ランナーの `AI Player Harness` を分けて扱います。使い分けは下の「AIプレイ検証」章を参照してください。
描写品質を支える Style Layer については `ARCHITECTURE.md` と `REQUIREMENTS.md` を参照してください。
漫画/作品/ジャンル/実ログから抽象化した物語構造ストックは `prompt/story_reference.md` にあり、各 session では `design/story_reference.md` / `design/story_spine.md` / `design/organization_cast.md` に変換して使います。これは固定作品リストではなく、ユーザーが挙げた作品名も例・方向性ヒントとして扱います。
既定の fast profile では `prompt/story_reference.md` 全文は読みません。代わりに `prompt/core_newgame.md` の `Initial Story Assembly` と `prompt/case_engine.md` の `Light Story Reference Pass` が、Q6後に最低限の selection signals、reference engine、story spine、organization cast、active case を初回シーン前へ接続します。
作品候補50本の研究棚は `references/story_media_stock.md` にあります。トークン効率のため毎回の起動 prompt には入れず、必要な時に 1〜3 本だけ抽象化して使います。

## 起動コマンド

通常プレイ:

- 日本語メニューで起動: `./liria`
- 日本語メニューで起動: `bash play.sh`
- シナリオ一覧: `bash play.sh list`
- session 一覧: `bash play.sh list-sessions`
- 初回プレイ: `bash play.sh new`
- セッション名指定で新規開始: `bash play.sh liria new session_002`
- 最新 session を再開: `bash play.sh resume`
- session 指定で再開: `bash play.sh liria resume session_002`
- prompt だけ確認: `bash play.sh liria new session_002 --prompt-only`
- Claude で再開: `bash play.sh resume -claude`
- Codex で再開: `bash play.sh resume -codex`
- 不要セッション削除: `./liria` → 「不要なセッションを削除する」

AIプレイ検証:

- 仮想プレイヤー smoke: `bash scripts/run_pi_player_smoke.sh`
- 仮想プレイヤー複数ターン smoke: `bash scripts/run_pi_player_smoke.sh --turns 8`
- 仮想プレイヤー複数ターン smoke cleanup付き: `bash scripts/run_pi_player_smoke.sh --turns 8 --cleanup`
- AI人格 実プレイ風ログ生成: `bash scripts/run_ai_persona_playtest.sh --turns 8`
- Kenji人格で長期試走: `bash scripts/run_ai_persona_playtest.sh session_kenji_ai_test_001 --turns 1000`
- 別人格を明示して試走: `bash scripts/run_ai_persona_playtest.sh session_ai_playtest_001 --turns 8 --persona /path/to/persona.yaml`
- 複数persona harness: `bash scripts/run_ai_player_harness.sh --config tests/ai_player_harness/sample.yaml --turns 8`
- 複数personaをCLIで指定: `bash scripts/run_ai_player_harness.sh --persona personas/kenji_style_player.yaml --persona personas/cautious_player.yaml --turns 8`
- 実プレイ生ログ分析: `bash scripts/analyze_play_log.sh path/to/raw_log.md`
- AI Persona Playtest の保存反映候補生成: `python3 scripts/extract_playtest_save_candidates.py session_story_wiring_test_001`

補足:

- コマンドを覚えたくない場合は、基本的に `./liria` だけでよいです。
- `./liria` / `bash play.sh` は、Codex CLI があれば Codex を優先して起動します。
- `new` で session 名を省略すると、旧 `session_001` を避けるため空の `saves/` でも `session_002` から未使用番号を自動採番します。
- `resume` で session 名を省略すると、ローカル `saves/` 配下の最新 session を再開します。
- エンジン未指定時は Codex CLI を優先して起動し、Codex がない場合だけ Claude CLI に fallback します。
- 非TTY環境やCIでは `--prompt-only` を使うと、session 作成と prompt 組み立てだけを確認できます。
- 実セッションは `saves/session_002/` のようなディレクトリに作られますが、Git 管理対象外です。
- GitHub 公開用に追跡するのは `templates/session/` の雛形だけです。

## AIプレイ検証

AIプレイ検証は、人間の本命プレイを置き換える仕組みではなく、GMの破綻、保存、恋愛、事件、漫画化導線、知識境界、選択肢の出し方を早めに見つけるためのQA補助です。

| 仕組み | 位置づけ | 主な確認対象 |
|---|---|---|
| PI Player | `prompt/pi_player.md` と `scripts/run_pi_player_smoke.sh` を使う回帰テスト用の疑似プレイヤー。本命プレイヤー代替ではなく、体験価値よりシステム動作確認を重視する。 | 新規開始、Q&A、入力解釈、GM仕様、保存分配、漫画化自然文トリガー |
| AI Persona Playtest | `scripts/run_ai_persona_playtest.py` / `.sh` で AI人格に実プレイ風の raw log を生成させる安全寄りの試走。完全な双方向プレイではない。 | ヒロイン自律性、恋愛/生活/事件の絡み、能力や装備の便利すぎ、Anti-Meta / Knowledge Boundary、保存候補、漫画化候補 |
| AI Player Harness | `scripts/run_ai_player_harness.py` / `.sh` で複数personaを順番に AI Persona Playtest へ渡す最小上位ランナー。完全自律GM/Playerループではなく、persona別ログとsummary reportを集める。 | personaごとの差、GM破綻、ヒロイン自律性、恋愛/生活/事件の絡み、Knowledge Boundary違反、漫画化候補 |

`run_ai_persona_playtest.sh` は、`play.sh --prompt-only` でLIRIAの開始プロンプトを作り、AI人格ファイルと一緒に Codex CLI へ渡して `saves/<session>/archive/logs/raw_*_ai_persona_playtest.md` を生成します。既定では `personas/kenji_style_player.yaml` を使い、生成後に `analyze_play_log.sh` へ渡します。まずプロンプトだけ確認したい場合は `--dry-run`、分析を省く場合は `--no-analyze` を使います。

AI Persona Playtest 後に保存反映候補だけをレビューしたい場合は、`python3 scripts/extract_playtest_save_candidates.py <session>` を使います。既定では最新の `analysis_*_ai_persona_playtest.md` を入口にし、同じ timestamp の raw log があれば `Save Notes` で補完して、`archive/logs/save_candidates_*.md` へ proposal を出します。これは `current/`、`design/`、`cast/`、`indexes/` を直接更新しないため、人間レビュー後に必要な差分だけ手動適用します。

`run_ai_player_harness.sh` は、複数personaを受け取り、personaごとに `session_ai_harness_...` 形式のsession名を自動生成して `run_ai_persona_playtest.py` を呼びます。結果は `saves/_harness_reports/ai_player_harness_YYYYMMDD_HHMMSS.md` にまとまり、persona名、session名、turns、raw log path、analysis path、exit status、失敗したpersona、次に人間が見るべきログを確認できます。config例は `tests/ai_player_harness/sample.yaml` にあります。
`personas/romance_first_player.yaml` は恋愛寄りプレイヤーで、ヒロイン即落ち、好意確定、身体的親密さや同意境界の破綻を検出するために使います。
`--dry-run` でも session scaffold、playtest prompt、harness report は生成されます。sandbox環境では、`play.sh --prompt-only` が使う `.codex/generated` への書き込み権限が必要になる場合があります。

AI Persona Playtest の制限:

- これは完全自律プレイヤーではなく、実プレイ風 raw log の生成補助です。
- Codex CLI は read-only で実行され、AIに save ファイルを直接編集させません。
- raw log 生成後の保存反映、session更新、pre_compress、integrity check は別処理です。保存反映候補のレビューには `extract_playtest_save_candidates.py` を使います。
- 本命プレイの面白さを最終判定する仕組みではなく、破綻検知と人間レビューの補助です。
- `analyze_play_log.sh` は保存可否の判定ではなく、LIRIAらしさや検証観点を見返しやすくするためのレビュー補助です。
- AI Player Harness も save/resume/pre_compress/check_session_integrity 連携はまだ行わず、下位の AI Persona Playtest をまとめて実行するだけです。

## セッション構成

新規 session は `templates/session/` から作成され、`saves/session_002/` のような構成を持ちます。

```text
saves/
└── session_002/
    ├── session.json
    ├── README.md
    ├── current/
    │   ├── player.md
    │   ├── gm.md
    │   ├── relationships.md
    │   ├── case.md
    │   ├── hotset.md
    │   ├── mechanics_card.md
    │   └── checkpoints/
    ├── cast/
    │   ├── heroine/
    │   └── npc/
    ├── design/
    │   ├── initial_answers.md
    │   ├── story_reference.md
    │   ├── story_spine.md
    │   ├── organization_cast.md
    │   ├── villain_design.md
    │   ├── visual_pipeline.md
    │   └── manga_pipeline.md
    ├── indexes/
    │   ├── cast_index.md
    │   ├── decision_index.md
    │   └── event_index.md
    └── archive/
        ├── chapters/
        ├── checkpoints/
        ├── events/
        └── logs/
```

`current/*` が現在状態、`current/case.md` が進行中の事件/依頼/違和感の短い設計図、`current/mechanics_card.md` が能力・道具・制約の軽量カード、`cast/*` が session ごとの人物設定、`design/*` が長期設計と画像生成/漫画化連携方針、`indexes/*` が索引、`archive/*` が履歴です。`design/story_reference.md` は採用した抽象 engine、`design/story_spine.md` は固定プロットではない薄い背骨、`design/organization_cast.md` は組織や外圧の主要人物候補、`current/case.md` は今触れる人・物・場所・記録・期限の足場を持ちます。`hotset.md` は再開用の軽量 cache であり、正本ではありません。

## テンプレートとローカルデータ

- 追跡対象: `play.sh`, `prompt/`, `style/`, `scenarios/`, `templates/session/`
- ローカル専用: `saves/*`, `exports/*`, `logs/`, `rawlogs/`, `tmp/`, `*.local.md`

`scripts/create_session.sh` は `templates/session/` をコピーして新規 session を作ります。テンプレートには個人プレイログを混ぜず、空の汎用雛形だけを置きます。

## 補助コマンド

- 通常起動は軽量 prompt profile: `bash play.sh resume`
- 全専門prompt込みで起動: `LIRIA_PROMPT_PROFILE=full bash play.sh resume`
- 10シーン到達時の自動カウント/生ログ保存: `bash scripts/autosave_turn.sh session_002`
- 生ログ保存: `bash scripts/save_rawlog.sh session_002`
- 通常プレイ newgame の保存反映候補生成: `python3 scripts/extract_newgame_state_candidates.py session_002`
- 通常プレイ newgame の空テンプレだけ安全反映: `python3 scripts/extract_newgame_state_candidates.py session_002 --apply-safe`
- 事前チェック: `bash scripts/pre_compress_check.sh session_002`
- session 整合確認: `bash scripts/check_session_integrity.sh session_002`
- repo 技術整合性チェック: `bash scripts/check_repo_integrity.sh`
- prompt/session 軽量化監査: `python scripts/liria_prompt_auditor.py --session saves/session_002`
- GM/Codex 内部用 manga export 雛形作成: `bash scripts/create_manga_export.sh session_002 heroine-teaser mizuki-smile`

### 通常プレイ newgame の復旧

通常プレイで Q&A と初回シーンが終わったのに `design/initial_answers.md`、`design/story_reference.md`、`design/story_spine.md`、`design/organization_cast.md`、`current/case.md`、`current/player.md`、`current/relationships.md`、`current/hotset.md` が空テンプレのままなら、ログから候補を復元します。

1. 生ログを保存する: `bash scripts/save_rawlog.sh session_002`
2. proposal を作る: `python3 scripts/extract_newgame_state_candidates.py session_002`
3. proposal の `Proposed Updates` を確認する
4. 空テンプレだけ反映する: `python3 scripts/extract_newgame_state_candidates.py session_002 --apply-safe`
5. 整合確認する: `bash scripts/check_session_integrity.sh session_002`

`--apply-safe` は、対象ファイルが空テンプレまたは未初期化に見える場合だけ書き込みます。書き込み前には `archive/checkpoints/pre_newgame_apply_YYYYMMDD_HHMMSS/` にバックアップを作り、既に人間が編集した内容があるファイルはスキップします。`cast/heroine/*.md` と `cast/npc/*.md` は自動作成せず、必要なら proposal を見て別途昇格します。

### Prompt profile

既定の `fast` profile は、通常プレイに必要な core / GM policy / case / runtime / combat / villain / romance / save-resume を読みます。Visual Character Sheet、Manga Export、Story Reference の専門 prompt は起動時には読まず、画像生成・漫画化・物語参照の相談や実行が必要になった時だけ on-demand で扱います。新規開始では Q6 後に `Initial Story Assembly` が走り、その中の `Light Story Reference Pass` が `prompt/story_reference.md` の軽量版として最低限の story_reference / story_spine / organization_cast / current case を初期化します。

`LIRIA_PROMPT_PROFILE=full` は、上記の専門 prompt も起動時から読み込む検証・設計用 profile です。`prompt/story_reference.md` 全文は full profile や専門相談で使う正本であり、fast の軽量 pass と分裂させません。重い sidecar である `design/story_reference.md`, `design/story_spine.md`, `design/organization_cast.md`, `design/visual_pipeline.md`, `design/manga_pipeline.md` はどちらの profile でも正本ですが、通常の save/resume では `current/hotset.md`, `current/case.md`, `indexes/cast_index.md`, `indexes/decision_index.md` を優先します。`current/mechanics_card.md`, `indexes/event_index.md`, checkpoints は、能力処理・continuity照合・圧縮前点検など必要な場面だけ開く運用にします。

AIプレイ検証系の役割境界とコマンド例は、上の「AIプレイ検証」章にまとめています。

漫画化、ヒロインPV、三面図、立ち絵、キャラシートの自然文依頼では、プレイヤーに CLI を覚えさせず、GM/Codex 側が必要に応じて内部補助スクリプトを使います。生成される `exports/<session>/manga/YYYYMMDD/*` は Git 管理外の prompt package です。相談型は実画像生成前に確認し、`漫画を出して` などの実生成明示型は裏ジョブとして進めます。

## 関連ドキュメント

- `LIRIA.md`: prompt orchestrator
- `prompt/`: 分割 prompt layer
- `prompt/gm_policy.md`: GMの基本原則、相談モード、入力意味論
- `ARCHITECTURE.md`: 実行構成と session layout
- `docs/architecture/MEMORY_MODEL.md`: 記憶モデル
- `docs/validation/INTEGRITY_CHECK.md`: save / resume の整合確認
- `docs/validation/VALIDATION.md`: 回帰確認観点
- `TODO.md`: 開発ロードマップ
- `templates/session/`: 新規 session 用 scaffold
