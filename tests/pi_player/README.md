# PI Player Tests

## Purpose

PI Player テストは、LIRIA v1 の新規開始フローを自動で軽く検証するための手順である。
ここで確認するのは、本命プレイの面白さではなく、新規開始、Q&A、入力解釈、GM仕様、保存分配、漫画化自然文トリガーが成立するかどうかだ。

## Separation of Responsibilities

- `prompt/pi_player.md`:
  - 疑似プレイヤーとしての人格、原則、既定プロフィール、入力傾向を定義する
- `tests/pi_player/`:
  - その疑似プレイヤーを使って何をどう検証するかを定義する

## Not a Replacement for Real Play

PI Player は本命プレイの代替ではない。
人間プレイヤーのインナーや関係性の変化を評価するためではなく、回帰確認と最低限の起動確認のために使う。

## Verification Scope

PI Player テストでは、主に以下を確認する。

- 新規開始フロー
- Q&A 保存分配
- GM仕様
- 入力解釈
- Q1.5 Appearance Profile / Visual Character Sheet の初期化
- Ability Constraint Profile と Equipment / Tools の保存粒度
- Heroine Crisis Role と Organization Doctrine Layer の保存
- Anti-Meta Dialogue / Knowledge Boundary / Anti-Leading
- Natural Language Manga Export と Manga Export Candidates
- `create_manga_export.sh` と `pre_compress_check.sh` の新項目
