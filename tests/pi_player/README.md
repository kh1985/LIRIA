# PI Player Tests

## Purpose

PI Player テストは、LIRIA v1 の新規開始フローを自動で軽く検証するための手順である。
ここで確認するのは、本命プレイの面白さではなく、新規開始、Q&A、入力解釈、GM仕様、保存分配、漫画化自然文トリガーが成立するかどうかだ。

## Separation of Responsibilities

- `prompt/pi_player.md`:
  - 疑似プレイヤーとしての人格、原則、既定プロフィール、入力傾向を定義する
- `tests/pi_player/`:
  - その疑似プレイヤーを使って何をどう検証するかを定義する
- `scripts/run_pi_player_smoke.sh`:
  - 仮想プレイヤー人格を読み込み、実セッションを作って `new -> 1 turn save -> resume -> pre_compress` を一括確認する
  - `--turns N` による複数ターン試走と long-run report を扱う

## Not a Replacement for Real Play

PI Player は本命プレイの代替ではない。
人間プレイヤーのインナーや関係性の変化を評価するためではなく、本命プレイ前の破綻検知、回帰確認、最低限の起動確認のために使う。

## Real Play Raw Log Analyzer

実プレイ生ログ分析器は、PI Player smoke とは別物である。

```bash
bash scripts/analyze_play_log.sh path/to/raw_log.md
```

これは保存チェックではなく、実プレイ風ログを人間レビューしやすくするための補助である。
本命プレイの代替ではなく、実際のプレイログや試走ログから、LIRIA としての手触りや次回改善点を拾うために使う。

主なレビュー観点:

- LIRIAらしさ
- ヒロイン自律性
- 恋愛 / 生活 / 事件の絡み
- 能力 / 装備が便利すぎないか
- Anti-Meta Dialogue / Knowledge Boundary
- 保存候補
- 漫画化候補
- 次ターンへの引き

保存分配、resume、pre-compress の確認は PI Player smoke や各チェックコマンドの責務であり、実プレイ生ログ分析器はそれらを置き換えない。

## AI Persona Playtest

AI人格に実プレイ風ログを生成させる場合は、以下を使う。

```bash
bash scripts/run_ai_persona_playtest.sh --turns 8
```

既定では、リポジトリ内の Kenji 人格を使う。

```text
personas/kenji_style_player.yaml
```

これは `play.sh --prompt-only` で作ったLIRIA開始プロンプトと、人格YAMLを Codex CLI に渡して、`archive/logs/raw_*_ai_persona_playtest.md` を生成する。
生成後は既定で `analyze_play_log.sh` を実行し、`analysis_*_ai_persona_playtest.md` も作る。

安全方針:

- AI人格には保存ファイルを直接編集させない
- Codex CLI は read-only で実行する
- 生成物は専用 session の `archive/logs/` に置く
- 本命プレイの代替ではなく、実プレイ前の試走ログ生成として使う
- 実保存の整合確認は `check_session_integrity.sh` や `pre_compress_check.sh` が担当する

プロンプトだけ確認する場合:

```bash
bash scripts/run_ai_persona_playtest.sh --turns 8 --dry-run
```

Kenji人格で長期試走する場合:

```bash
bash scripts/run_ai_persona_playtest.sh session_kenji_ai_test_001 --turns 1000
```

別人格を使う場合:

```bash
bash scripts/run_ai_persona_playtest.sh session_ai_playtest_other --turns 8 --persona /path/to/persona.yaml
```

## Auto Smoke Runner

本命プレイ前の試運転は、以下で実行できる。

```bash
bash scripts/run_pi_player_smoke.sh
```

デフォルトでは、存在する場合に以下の人格YAMLを読む。

```text
/Users/kenjihachiya/Desktop/work/development/marketing/character/output/gal-sim-testers/01_ishikawa_ryota.yaml
```

別人格を使う場合:

```bash
bash scripts/run_pi_player_smoke.sh --persona /path/to/persona.yaml
```

セッション名を指定する場合:

```bash
bash scripts/run_pi_player_smoke.sh session_pi_auto_mycase
```

検証後に一時セッションを片付ける場合:

```bash
bash scripts/run_pi_player_smoke.sh --cleanup
```

複数ターン試走では、短い 1 turn smoke より少し長く GM 応答、保存分配、resume 後の継続性を確認する。

```bash
bash scripts/run_pi_player_smoke.sh --turns 8
```

一時セッションの cleanup も同時に行う場合:

```bash
bash scripts/run_pi_player_smoke.sh --turns 8 --cleanup
```

`--turns N` 実行では、単発成功だけでなく、ターンごとの入力、保存、resume、pre-compress 観点を long-run report として要約する。

このランナーは `play.sh` 本体を改造せず、専用の smoke session だけを作る。
既存の本命 session は上書きしない。

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
