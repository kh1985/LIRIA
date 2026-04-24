# LIRIA

LIRIA は、AI GM 前提の長編セッションを新規開始できる汎用エンジン / スターターキットです。
このリポジトリ本体には実プレイ済みセーブや個人ログを含めず、`templates/session/` の雛形からローカルに session を作成して使います。

## セットアップ

1. このリポジトリを clone
2. `Claude CLI` または `Codex CLI` を使える状態にする
3. 新規開始は `bash play.sh new`
4. 続きから再開は `bash play.sh resume`

## 起動コマンド

- シナリオ一覧: `bash play.sh list`
- session 一覧: `bash play.sh list-sessions`
- 初回プレイ: `bash play.sh new`
- セッション名指定で新規開始: `bash play.sh liria new session_002`
- 最新 session を再開: `bash play.sh resume`
- session 指定で再開: `bash play.sh liria resume session_002`
- Claude で再開: `bash play.sh resume -claude`
- Codex で再開: `bash play.sh resume -codex`

補足:

- `new` で session 名を省略すると、`session_###` 形式の未使用番号を自動採番します。
- `resume` で session 名を省略すると、ローカル `saves/` 配下の最新 session を再開します。
- 実セッションは `saves/<session_name>/` に作られますが、Git 管理対象外です。
- GitHub 公開用に追跡するのは `templates/session/` の雛形だけです。

## セッション構成

新規 session は `templates/session/` から作成され、`saves/<session_name>/` に次の構成を持ちます。

```text
saves/
└── <session_name>/
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
    │   └── villain_design.md
    ├── indexes/
    │   ├── cast_index.md
    │   ├── decision_index.md
    │   └── event_index.md
    └── archive/
        ├── chapters/
        ├── events/
        └── logs/
```

`current/*` が現在状態、`cast/*` が session ごとの人物設定、`design/*` が長期設計、`indexes/*` が索引、`archive/*` が履歴です。`hotset.md` は再開用の軽量 cache であり、正本ではありません。

## テンプレートとローカルデータ

- 追跡対象: `play.sh`, `prompt/`, `style/`, `scenarios/`, `templates/session/`
- ローカル専用: `saves/*`, `logs/`, `rawlogs/`, `tmp/`, `*.local.md`

`scripts/create_session.sh` は `templates/session/` をコピーして新規 session を作ります。テンプレートには個人プレイログを混ぜず、空の汎用雛形だけを置きます。

## 補助コマンド

- 生ログ保存: `bash scripts/save_rawlog.sh <session_name>`
- 事前チェック: `bash scripts/pre_compress_check.sh <session_name>`
- session 整合確認: `bash scripts/check_session_integrity.sh <session_name>`

## 関連ドキュメント

- `GALGE.md`: prompt orchestrator
- `prompt/`: 分割 prompt layer
- `ARCHITECTURE.md`: 実行構成と session layout
- `MEMORY_MODEL.md`: 記憶モデル
- `INTEGRITY_CHECK.md`: save / resume の整合確認
- `VALIDATION.md`: 回帰確認観点
- `TODO.md`: 開発ロードマップ
- `templates/session/`: 新規 session 用 scaffold
