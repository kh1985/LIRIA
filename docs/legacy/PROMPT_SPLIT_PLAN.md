# PROMPT_SPLIT_PLAN

## 目的

`GALGE.md` の肥大化を止める。

いきなり全面分割はせず、
**どの章をどこへ移すか** を先に固定する。

## 基本方針

- 毎回読むべきルールは薄く保つ
- 戦闘、恋愛、敵設計、保存再開は責務で分ける
- まずは `save_resume` `villain_engine` `romance` から実分割し、その後 `core` `runtime` `combat` まで切る
- 分割後も `play.sh` からの入口は 1 つにする

## 現在地

- `prompt/save_resume.md` は実装済み
- `prompt/villain_engine.md` は実装済み
- `prompt/romance.md` は実装済み
- `prompt/core.md` は実装済み
- `prompt/runtime.md` は実装済み
- `prompt/combat.md` は実装済み
- `play.sh` は複数 prompt 断片の連結に対応済み
- `GALGE.md` は core / runtime / combat / romance / save_resume / villain_engine の orchestrator として動作
- 次の判断対象は `prompt/style_bridge.md` を切るかどうか

## 目標ファイル

1. `prompt/core.md`
   - 最優先ルール
   - AI-GM の人格と禁止事項
   - 新規 / 再開の入口だけ

2. `prompt/runtime.md`
   - プレイ中の運用
   - 3本フック
   - 脅威クロック
   - コンテキスト管理

3. `prompt/combat.md`
   - 戦闘思想
   - 戦闘システム
   - 非戦闘判定
   - 成長と能力変化

4. `prompt/romance.md`
   - ヒロインシステム
   - 恋愛メカニクス
   - Relationship / Heroine Network
   - 感情演出原則

5. `prompt/save_resume.md`
   - 再開手順
   - セーブ手順
   - current / hotset / archive 運用
   - memory model との接続

6. `prompt/villain_engine.md`
   - 勢力浮上
   - 敵設計
   - ボス / 幹部 / 顕在化段階

7. `prompt/style_bridge.md`
   - 文体ルール
   - style/reference 連携
   - 文豪シーンテンプレート

## 読み込み順

最低順:

1. `prompt/core.md`
2. `prompt/runtime.md`
3. `prompt/combat.md`
4. `prompt/save_resume.md`

必要時追加:

5. `prompt/style_bridge.md`
6. `prompt/villain_engine.md`
7. `prompt/romance.md`

## 現行 `GALGE.md` からの移設先

| 現行章 | 移設先 |
|---|---|
| `## お前の正体` `## 絶対に守れ` | `prompt/core.md` |
| `## 新規ゲーム開始の手順` | `prompt/core.md` |
| `## プレイ再開の手順` | `prompt/save_resume.md` |
| `## プレイ中の運用ルール` | `prompt/runtime.md` |
| `## NPC運用ルール` | `prompt/romance.md` と `prompt/runtime.md` |
| `## ランダムイベントシステム` | `prompt/runtime.md` |
| `## 戦闘の設計思想` `## 戦闘システム` `## 非戦闘判定システム` | `prompt/combat.md` |
| `## 成長システム` `## 能力の成長と変化` | `prompt/combat.md` |
| `## 感情演出の設計原則` | `prompt/romance.md` |
| `## 文体ルール` `## 文豪シーンテンプレート` | `prompt/style_bridge.md` |
| `## 3本フック運用` `## 脅威クロック` | `prompt/runtime.md` |
| `## 勢力クロック` `## 勢力浮上システム` `## 敵のデザイン` | `prompt/villain_engine.md` |
| `## セーブ手順` | `prompt/save_resume.md` |
| `## ヒロインシステム` `## 恋愛メカニクス` `## ヒロイン心理成長システム` `## Relationship / Heroine Network` | `prompt/romance.md` |
| `## 依頼＆商売システム` `## 拠点システム` | `prompt/runtime.md` |
| `## characterシステム連携` | `prompt/core.md` または `prompt/style_bridge.md` |

## 実装済みの分割単位

現時点で主要 6 分割までは完了。

1. `prompt/core.md`
2. `prompt/runtime.md`
3. `prompt/combat.md`
4. `prompt/save_resume.md`
5. `prompt/villain_engine.md`
6. `prompt/romance.md`

残る選択肢:
- `prompt/style_bridge.md` を追加で切る
- style 関連は `GALGE.md` と `style/` に残す

## 移行手順

1. 現行 `GALGE.md` を正本のまま維持
2. 切り出し先ファイルを新規作成
3. `GALGE.md` 内に「この章の正本はここ」とコメントを置く
4. 内容を徐々に減らす
5. 最後に `GALGE.md` を orchestrator 化する

## 完了条件

- 各章の移設先が決まっている
- 主要 6 ファイルが実動する
- `GALGE.md` をいきなり壊さず移行できる
