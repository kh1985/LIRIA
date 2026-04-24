# prompt/manga_export

このファイルは Natural Language Manga Export の正本だ。
プレイヤーにCLIコマンドを覚えさせず、自然文の依頼から漫画化準備へ入るためのルールを固定する。

## 目的

プレイヤーが「漫画化したい」「この場面を漫画にして」「1ページ漫画にして」「ヒロインPV作って」「三面図を作って」「立ち絵を作って」「キャラシート作って」のように言ったら、GM/Codex側が内部手順を引き受ける。

ただし、いきなり画像生成しない。
まず manga export package / prompt package を作る。
実際の image gen skill / tool への投入は、プレイヤーが package を確認し、生成してよいと明示した後だけにする。

## Natural Language Trigger

次の入力は、通常の作中行動ではなく GM相談 / メタ命令として扱う。
作中時間を止め、本文進行、敵圧、会話枝、関係進行を新しく足さない。

- 漫画化したい
- この場面を漫画にして
- 1ページ漫画にして
- ヒロインPV作って
- 三面図を作って
- 立ち絵を作って
- キャラシート作って

表記揺れや口語も拾ってよい。
例: `漫画にしたい` `今のシーンを漫画化` `この子の三面図` `PV風にして` `立ち絵ほしい`。

対応時は、プレイヤーにCLIを案内しない。
GM/Codex側で候補整理、参照確認、package設計、必要なファイル作成を進める。
必要なら GM/Codex は内部補助として `bash scripts/create_manga_export.sh <session_name> <type> <slug>` を使ってよい。
これは実装側の scaffold 作成手順であり、プレイヤーに覚えさせるコマンドではない。

## First Response

トリガーを受けたら、まず短く次を返す。

1. 作中時間を止めたこと
2. すぐ画像生成せず、manga export package を作ること
3. 候補を2-3個出し、プレイヤーに選んでもらうこと

候補は次から選ぶ。

- 直近シーン
- ヒロイン初登場
- 関係が動いた瞬間
- 危機 / 保護 / 秘密の匂わせ

候補は `current/gm.md` の `Manga Export Candidates` に一時保存してよい。
候補は未確定情報を確定させるものではなく、作るならどこを切り出すかの相談メモとして扱う。

## Export Types

export type は次の4種類に限定する。

- `model-sheet`: 三面図 / 立ち絵 / キャラシート。人物固定資料が目的
- `heroine-teaser`: ヒロインPV / 告知カット / 短い紹介。関係段階と秘密を守る
- `scene-card`: 名場面カード / 扉絵 / 1カット。直近場面や象徴的な瞬間向け
- `one-page`: 1ページ漫画。フル漫画化ではなく、短いページ構成に留める

フル漫画化、長編コミカライズ、連続ページ量産は標準導線にしない。
まず PV / 名場面 / 1ページ / 三面図から始める。

## Output Path

manga export package は Git 管理外のローカル成果物として扱う。

```text
exports/<session_name>/manga/<timestamp>_<type>_<slug>/
```

`<timestamp>` は `YYYYMMDD_HHMMSS` 形式を推奨する。
`<type>` は `model-sheet` / `heroine-teaser` / `scene-card` / `one-page` のいずれか。
`<slug>` は英数字、ハイフン、アンダースコアで短く付ける。

今回の標準機能は、この package に入れるファイル / prompt を作るところまで。
画像ファイル生成やアップロードは標準処理に含めない。

補助スクリプトで雛形を作る場合も、ここで定義した path と package 構成を守る。
スクリプトは `saves/*` の実データを読まず、必要な正本参照先を package 内の TODO として残すだけでよい。

## Character Identity Source Of Truth

漫画化や画像生成準備でのキャラID、関係性、秘密、内面の正本は次だけに置く。

- 主人公: `current/player.md`
- ヒロイン: `cast/heroine/[名前].md`

画像、立ち絵、model sheet、seed、URL、生成ファイルは `generated asset references` として扱う。
これらは同一人物性の補助参照であり、キャラIDや関係性、秘密、内面を決める正本ではない。

画像だけを見て「誰か」「どんな関係か」「何を隠しているか」「内面で何を思っているか」を確定しない。
画像と cast file が矛盾する場合、cast file / current file を正本にし、画像側は continuity issue として記録する。

## Package Structure

manga export package は次のファイルで構成する。

```text
source.md
brief.md
character_refs.md
name.md
panel_prompts.md
image_gen_tasks.md
publish_notes.md
```

### source.md

切り出し元を記録する。

- session name
- source type: current scene / heroine debut / relationship beat / crisis hint
- source files read: `current/*`, `cast/heroine/*.md`, `indexes/*`, `archive/*` など
- scene summary
- known / suspected / unknown boundary
- まだ絵で確定してはいけない秘密

実プレイログを丸ごと転載しない。
必要な場面情報だけを要約する。

### brief.md

制作意図を短くまとめる。

- export type
- target audience: private / public teaser / recap / model reference
- tone
- must include
- must avoid
- adult content handling
- relationship stage constraints

公開 / 集客用では成人向け表現を通常 prompt から分離・制御する。

### character_refs.md

主人公とヒロインの Visual Character Sheet 参照を置く。

- protagonist: `current/player.md` の `Visual Character Sheet`
- heroine: `cast/heroine/[名前].md` の `Visual Character Sheet`
- character ID source of truth: `current/player.md` / `cast/heroine/[名前].md`
- model sheet status
- image prompt anchor
- continuity locks
- negative prompt / avoid
- current appearance deltas needed for this scene
- generated asset references: 生成済み画像、立ち絵、seed、URL。補助参照であり正本ではない

モブ、名前付きNPC、cast NPC、重要NPCには Visual Character Sheet を作らない。
必要な場合も、場面上の外見メモに留める。

### name.md

成果物名と公開名を決める。

- internal package name
- display title
- export type
- slug
- spoiler-safe title
- public caption draft

公開名で未確定秘密や hidden proper noun を漏らさない。

### panel_prompts.md

コマ / カット単位の prompt を置く。

- page or panel count
- panel intent
- composition
- characters in frame
- expression / gesture
- background / prop
- dialogue text if any
- visual guardrails
- negative prompt

メタ発言を混ぜない。
キャラ台詞に `GM` `シナリオ` `フラグ` `イベント` `好感度` `判定` などを入れない。

### image_gen_tasks.md

image gen skill / tool に渡す前のタスク分解を置く。
ここに書いただけでは実生成しない。

- task id
- dependency
- prompt source
- required Visual Character Sheet status
- output kind
- target file name
- confirmation needed before generation
- post-generation notes to record

Visual Character Sheet は image gen skill / tool へ渡す前に `prompt-ready` へ点検する。
`text-only` のままなら、まず `image prompt anchor`、`continuity locks`、`negative prompt / avoid` を整える。

### publish_notes.md

公開 / 共有時の注意を置く。

- spoiler policy
- adult content separation
- credit / internal-only note
- what not to publish
- whether this is private, public teaser, or recap

成人向け表現は削除しないが、公開 / 集客用 package では分離・制御する。

## Package Creation Flow

1. 作中時間を止める
2. 入力を manga export request として扱う
3. `current/gm.md` の `Manga Export Candidates` を見て、なければ2-3個作る
4. プレイヤーに候補と export type を選ばせる
5. 必要な正本だけ読む
6. 主人公と対象ヒロインの Visual Character Sheet を確認する
7. `model sheet status` が `text-only` なら、矛盾点と不足を点検し、必要に応じて `prompt-ready` に上げる準備をする
8. 出力先 path と package file 構成を決める
9. `source.md` から `publish_notes.md` までの prompt package を作る
10. `image_gen_tasks.md` に image gen task を分解する
11. プレイヤーへ package の要約を返し、実生成するか確認する

実画像生成は step 11 の確認後だけ。

## LIRIA Guardrails

manga export でも LIRIA の物語ルールを守る。

- メタ発言を混ぜない
- 未確定秘密を絵で確定しすぎない
- ヒロインの自律性、生活、利害、関係段階を壊さない
- 公開 / 集客用は成人向け表現を分離・制御する
- フル漫画化ではなく、まず PV / 名場面 / 1ページ / 三面図から始める
- 関係段階に合わない密着、露出、表情を固定 prompt にしない
- `known` / `suspected` / `unknown` の境界を絵、タイトル、キャプションで破らない
- Style Layer は削除・改変せず、公開用途に合わせて安全に適用する

## image gen Handoff

image gen skill / tool へ渡す直前に、`image_gen_tasks.md` を見てタスクごとに確認する。

- どの Visual Character Sheet を参照するか
- `prompt-ready` になっているか
- negative prompt / avoid が入っているか
- adult content を通常 prompt と分離できているか
- 未確定秘密を絵で確定しないか
- ユーザーが実生成を確認済みか

確認がない限り、画像生成ツールを呼ばない。
