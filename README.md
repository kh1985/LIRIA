# LIRIA

コンセプト整理: [CONCEPT.md](CONCEPT.md)

LIRIA は、恋愛・生活・事件を通して、プレイヤーのインナーと関係性が変化していく AI TRPG 型恋愛シミュレーションです。
このリポジトリは、そのセッションをローカルに開始・継続するための実行基盤であり、実プレイ済みセーブや個人ログを含めず、`templates/session/` の雛形からローカルに session を作成して使います。

## セットアップ

1. このリポジトリを clone
2. `Claude CLI` または `Codex CLI` を使える状態にする
3. 新規開始は `bash play.sh new`
4. 続きから再開は `bash play.sh resume`

新規開始時は Q&A でインナー / 生活基盤 / 恋愛の好み / 能力 / 事件入口 / 初期関係を初期化します。
GMの基本原則、相談モード、入力意味論は `prompt/gm_policy.md` にあります。
検証用の疑似プレイヤー仕様は `prompt/pi_player.md` にあり、PI Player は本命プレイの代替ではありません。
PI Player を使った新規開始 / 保存分配 / GM仕様 / 漫画化自然文トリガーのスモークテスト手順は `tests/pi_player/` を参照してください。
仮想プレイヤー人格込みの自動 smoke は `bash scripts/run_pi_player_smoke.sh` で実行できます。
複数ターン試走と long-run report は `bash scripts/run_pi_player_smoke.sh --turns 8`、一時セッションの片付け込みなら `bash scripts/run_pi_player_smoke.sh --turns 8 --cleanup` で実行できます。
実プレイ風の生ログを人間レビューしやすくする補助分析は `bash scripts/analyze_play_log.sh path/to/raw_log.md` で実行できます。これは保存チェックや PI Player smoke ではなく、LIRIAらしさ、ヒロイン自律性、恋愛/生活/事件の絡み、能力/装備の便利すぎ、Anti-Meta/Knowledge Boundary、保存候補、漫画化候補、次ターンへの引きを見るためのレビュー補助です。
AI人格に実プレイ風ログを生成させる試走は `bash scripts/run_ai_persona_playtest.sh --turns 8` で実行できます。これは実セッションの保存ファイルをAIに直接編集させず、Codex CLIにread-onlyで生ログを作らせてから分析する安全寄りの導線です。
描写品質を支える Style Layer については `ARCHITECTURE.md` と `REQUIREMENTS.md` を参照してください。

## 起動コマンド

- シナリオ一覧: `bash play.sh list`
- session 一覧: `bash play.sh list-sessions`
- 初回プレイ: `bash play.sh new`
- セッション名指定で新規開始: `bash play.sh liria new session_002`
- 最新 session を再開: `bash play.sh resume`
- session 指定で再開: `bash play.sh liria resume session_002`
- prompt だけ確認: `bash play.sh liria new session_002 --prompt-only`
- 仮想プレイヤー smoke: `bash scripts/run_pi_player_smoke.sh`
- 仮想プレイヤー複数ターン smoke: `bash scripts/run_pi_player_smoke.sh --turns 8`
- 仮想プレイヤー複数ターン smoke cleanup付き: `bash scripts/run_pi_player_smoke.sh --turns 8 --cleanup`
- 実プレイ生ログ分析: `bash scripts/analyze_play_log.sh path/to/raw_log.md`
- AI人格 実プレイ風ログ生成: `bash scripts/run_ai_persona_playtest.sh --turns 8`
- Claude で再開: `bash play.sh resume -claude`
- Codex で再開: `bash play.sh resume -codex`

補足:

- `new` で session 名を省略すると、旧 `session_001` を避けるため空の `saves/` でも `session_002` から未使用番号を自動採番します。
- `resume` で session 名を省略すると、ローカル `saves/` 配下の最新 session を再開します。
- エンジン未指定時は Codex CLI を優先して起動し、Codex がない場合だけ Claude CLI に fallback します。
- 非TTY環境やCIでは `--prompt-only` を使うと、session 作成と prompt 組み立てだけを確認できます。
- 実セッションは `saves/session_002/` のようなディレクトリに作られますが、Git 管理対象外です。
- GitHub 公開用に追跡するのは `templates/session/` の雛形だけです。

## セッション構成

新規 session は `templates/session/` から作成され、`saves/session_002/` のような構成を持ちます。

```text
saves/
└── session_002/
    ├── session.json
    ├── current/
    │   ├── player.md
    │   ├── gm.md
    │   ├── harem.md
    │   └── hotset.md
    ├── cast/
    │   ├── heroine/
    │   └── npc/
    ├── design/
    │   ├── villain_design.md
    │   ├── visual_pipeline.md
    │   └── manga_pipeline.md
    ├── indexes/
    │   ├── cast_index.md
    │   ├── decision_index.md
    │   └── event_index.md
    └── archive/
        ├── chapters/
        ├── events/
        └── logs/
```

`current/*` が現在状態、`cast/*` が session ごとの人物設定、`design/*` が長期設計と画像生成/漫画化連携方針、`indexes/*` が索引、`archive/*` が履歴です。`hotset.md` は再開用の軽量 cache であり、正本ではありません。

## テンプレートとローカルデータ

- 追跡対象: `play.sh`, `prompt/`, `style/`, `scenarios/`, `templates/session/`
- ローカル専用: `saves/*`, `exports/*`, `logs/`, `rawlogs/`, `tmp/`, `*.local.md`

`scripts/create_session.sh` は `templates/session/` をコピーして新規 session を作ります。テンプレートには個人プレイログを混ぜず、空の汎用雛形だけを置きます。

## 補助コマンド

- 生ログ保存: `bash scripts/save_rawlog.sh session_002`
- 実プレイ生ログ分析: `bash scripts/analyze_play_log.sh path/to/raw_log.md`
- AI人格 実プレイ風ログ生成: `bash scripts/run_ai_persona_playtest.sh session_ai_playtest_001 --turns 8`
- 事前チェック: `bash scripts/pre_compress_check.sh session_002`
- session 整合確認: `bash scripts/check_session_integrity.sh session_002`
- GM/Codex 内部用 manga export 雛形作成: `bash scripts/create_manga_export.sh session_002 heroine-teaser mizuki-smile`

`analyze_play_log.sh` は、実プレイ風ログを保存可否で判定するためではなく、本命プレイ後または試走ログの品質を人間が見返しやすくするためのレビュー補助です。保存分配や resume の整合確認は `pre_compress_check.sh` や `check_session_integrity.sh` が担当します。

`run_ai_persona_playtest.sh` は、`play.sh --prompt-only` でLIRIAの開始プロンプトを作り、AI人格ファイルと一緒に Codex CLI へ渡して実プレイ風の `raw_*.md` を生成します。デフォルトでは生成ログを `analyze_play_log.sh` にかけます。まずプロンプトだけ確認したい場合は `--dry-run` を使います。

漫画化、ヒロインPV、三面図、立ち絵、キャラシートの自然文依頼では、プレイヤーに CLI を覚えさせず、GM/Codex 側が必要に応じて内部補助スクリプトを使います。生成される `exports/<session>/manga/*` は Git 管理外の prompt package であり、実画像生成はプレイヤー確認後だけ行います。

## 関連ドキュメント

- `GALGE.md`: prompt orchestrator
- `prompt/`: 分割 prompt layer
- `prompt/gm_policy.md`: GMの基本原則、相談モード、入力意味論
- `ARCHITECTURE.md`: 実行構成と session layout
- `MEMORY_MODEL.md`: 記憶モデル
- `INTEGRITY_CHECK.md`: save / resume の整合確認
- `VALIDATION.md`: 回帰確認観点
- `TODO.md`: 開発ロードマップ
- `templates/session/`: 新規 session 用 scaffold
