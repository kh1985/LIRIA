# LIRIA

inner-trpg ベースのハーレム型ギャルゲー。AI GM が紡ぐ大人の冒険譚。

## コンセプト

エロティックな能力を持つ主人公が世界を旅し、悪を倒し、女を堕とし、ハーレムを築く。
TRPG の冒険とギャルゲーの恋愛が心理学で融合したテキストベース体験。

## セットアップ

1. このリポジトリを clone
2. Claude CLI または Codex CLI で起動する
3. 新規開始なら `bash play.sh new`、再開なら `bash play.sh resume`

## 正規の起動方法

会話で「続きからプレイしたい」とだけ言うのは正規ルートではない。
**必ず `play.sh` 経由で起動すること。**

基本コマンド:

- シナリオ一覧: `bash play.sh list`
- セッション一覧: `bash play.sh list-sessions`
- デフォルトシナリオで新規作成: `bash play.sh new`
- デフォルトシナリオで名前付き新規作成: `bash play.sh new liria <session_name>`
- シナリオ指定で名前付き新規作成: `bash play.sh liria new <session_name>`
- デフォルトシナリオを再開: `bash play.sh resume`
- シナリオと session を指定して再開: `bash play.sh liria resume <session_name>`
- Claude を明示: `bash play.sh resume -claude` または `ENGINE=claude bash play.sh resume`
- Codex を明示: `bash play.sh resume -codex` または `ENGINE=codex bash play.sh resume`

session 名を省略した場合、新規作成では launcher が未使用名を採番する。
再開では launcher が決めた既定 session、通常は最新 session を選び、選択した session 名を出力する。

このコピーには既存のセーブ資産を含めていない。`session_001` などの番号付き session は、新規生成や将来の移行例として扱う。

正規の再開では、session 配下の `current/`、必要な `cast/`、`design/`、`indexes/`、`archive/` を launcher と prompt が協調して読む。

## 長時間プレイ時の運用

このプロジェクトは「1セッションを丸一日伸ばし続ける」より、`セーブ -> bash play.sh resume` を繰り返す運用の方が安定する。

- 通常シーン10回ごとに、GM が `saves/<session_name>/current/*` の自動セーブと生ログ保存を入れる
- 大きな区切りや「今日はここまで」の時は、10シーン未満でも手動セーブする
- 反応が鈍くなったら `/compress` だけで粘らず、保存して再起動する
- `hotset.md` は再開1ターン目の cache であり、正本ではない。保存時は append ではなく上書き再生成する

補助コマンド:

- 生ログ保存: `bash scripts/save_rawlog.sh <session_name>`
- Codex ログを明示: `ENGINE=codex bash scripts/save_rawlog.sh <session_name>`
- Claude ログを明示: `ENGINE=claude bash scripts/save_rawlog.sh <session_name>`
- 圧縮前チェック: `bash scripts/pre_compress_check.sh <session_name>`
- session 整合チェック: `bash scripts/check_session_integrity.sh <session_name>`

## ダブルクリック起動

Finder からそのまま起動したい場合は、以下をダブルクリックする。

- [start_new_game.command](/Users/kenjihachiya/Desktop/work/development_gemini/LIRIA/start_new_game.command): `liria` の新規 session を開始
- [resume_game.command](/Users/kenjihachiya/Desktop/work/development_gemini/LIRIA/resume_game.command): `liria` の既存 session を再開
- [choose_scenario.command](/Users/kenjihachiya/Desktop/work/development_gemini/LIRIA/choose_scenario.command): シナリオ名と session を選んで起動

macOS では `.command` は Terminal で実行される。

## シナリオ追加

別シナリオを増やす時は、`scenarios/<scenario_id>/config.sh` を追加する。

最小構成:

```bash
SCENARIO_ID="my-scenario"
SCENARIO_NAME="my-scenario"
SCENARIO_ROOT="."
SYSTEM_PROMPT_FILES=(
  "MY_SCENARIO.md"
)

build_new_prompt() {
  local session_name="$1"
  local session_path="saves/${session_name}"
  cat <<EOF
MY_SCENARIO.md のルールで開始して。新しいゲームを ${session_path} に保存する。
current / cast / design / indexes / archive はこの session 配下だけを使う。
EOF
}

build_resume_prompt() {
  local session_name="$1"
  local session_path="saves/${session_name}"
  cat <<EOF
MY_SCENARIO.md のルールで再開して。${session_path} を読み込んで再開して。
EOF
}
```

追加後は `bash play.sh list` に出る。

## セーブレイアウト

新規 session は self-contained にする。cast も save も session 配下に置き、同じ scenario の別 session を汚染しない。

```text
saves/
└── session_XXX/
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

正本:

- `current/gm.md`: 現在フェーズ、現在フック、脅威クロック、勢力クロック、知識スコープ、自動セーブ管理
- `current/player.md`: プレイヤー現在状態、HP、残回数、所持、プレイヤー視点の現在地
- `current/harem.md`: 関係値、AFFINITY / bond、active な関係フック、hidden 深化ベクトル
- `current/hotset.md`: 再開用の derived cache。正本ではない
- `cast/heroine/*.md`: session 単位のヒロイン voice / fixed memory / personality / role
- `cast/npc/*.md`: session 単位の NPC voice / fixed memory / personality / role
- `design/*`: 長期設計
- `indexes/*`: archive を引くための軽量目次
- `archive/*`: 過去ログ、章、イベント

### Legacy read-only fallback

古い session には session 直下の `player.md` `gm.md` `harem.md` `villain_design.md` や repo ルートの cast ディレクトリが残る場合がある。
これらは legacy 読み取り fallback であり、通常の保存先や新規 session の正本ではない。

main path は常に `saves/<session_name>/current/*`、`saves/<session_name>/cast/*`、`saves/<session_name>/design/*`、`saves/<session_name>/indexes/*`、`saves/<session_name>/archive/*`。
互換のために legacy を読む場合でも、書き込みは session 配下へ集約する。

## 外部依存

以下はプレイ体験を向上させるが、なくても動作する。

- [character](https://github.com/kh1985/character): ヒロイン自動生成システム。なければ GM が内部で直接設計する
- Web 検索: 文体参照ファイル `style/reference.md` の動的生成に使用。CLI が Web 検索をサポートしていない場合、`style/defaults/` のみで運用する

## CLI 権限

プレイ中に GM が以下のツールを使う場合がある。

- ファイル読み書き: session 配下の save / cast / archive の生成・更新
- Bash 実行: character システム呼び出し、ログ保存、整合チェック
- Web 検索: 文体参照の生成

## ファイル

- `GALGE.md`: prompt orchestrator。分割済み prompt layer への入口
- `prompt/`: 分割済み prompt layer
- `CORE.md`: 保守用の短縮リファレンス。live session state は置かない
- `ARCHITECTURE.md`: 構成 / 目標 layout / ファイル関係図
- `MEMORY_MODEL.md`: 記憶分類と圧縮 / 再昇格ルール
- `INTEGRITY_CHECK.md`: セーブ後 / 再開前の手動整合チェック
- `VALIDATION.md`: 長編・複数 session 前提の回帰確認観点
- `TODO.md`: 実装ロードマップ
- `style/`: 文体参照ファイル群
- `templates/session/`: 新規 session scaffold
- `saves/`: session 単位のプレイ資産。既存資産は tracked の場合があるため、`.gitignore` 対象と決めつけない

## ベースシステム

- [inner-trpg](https://github.com/kh1985/inner-trpg) - 能力・戦闘・成長システム
- [character](https://github.com/kh1985/character) - キャラクター自動生成（任意）

## ステータス

開発中。prompt layer 分割、session-scoped save / cast、multi-session launcher へ移行中。
