# prompt/manga_export

このファイルは Natural Language Manga Export の正本だ。
プレイヤーにCLIコマンドを覚えさせず、自然文の依頼から漫画化準備へ入るためのルールを固定する。

## 目的

プレイヤーが「漫画化したい」「この場面を漫画にして」「1ページ漫画にして」「ヒロインPV作って」「三面図を作って」「立ち絵を作って」「キャラシート作って」のように言ったら、GM/Codex側が内部手順を引き受ける。

通常の相談では、いきなり画像生成しない。
まず manga export package / prompt package を作り、プレイヤーが確認してから実生成する。

ただし、プレイヤーが `漫画を出して` `画像も生成して` `このシーンを出して` `生成までやって` のように実生成まで明示した場合は、その発話を生成確認として扱う。
この場合は、package 作成、prompt 点検、image gen skill / tool への投入までを一連の内部手順として実行してよい。
物語は待たせない。生成ジョブは裏で進め、GM本文は直前の場面へ戻る。

## Natural Language Trigger

次の入力は、通常の作中行動ではなく GM相談 / メタ命令として扱う。
漫画化タスク自体では、本文進行、敵圧、会話枝、関係進行を新しく足さない。

**相談型 trigger:**
- 漫画化したい
- この場面を漫画にして
- 1ページ漫画にして
- ヒロインPV作って
- 三面図を作って
- 立ち絵を作って
- キャラシート作って

**実生成明示型 trigger:**
- 漫画を出して
- 画像も生成して
- このシーンを出して
- 生成までやって
- 裏で生成して
- バックエンドで生成して
- 物語は止めずに漫画も出して

表記揺れや口語も拾ってよい。
例: `漫画にしたい` `今のシーンを漫画化` `この子の三面図` `PV風にして` `立ち絵ほしい` `この場面を出して`。

対応時は、プレイヤーにCLIを案内しない。
GM/Codex側で候補整理、参照確認、package設計、必要なファイル作成を進める。
必要なら GM/Codex は内部補助として `bash scripts/create_manga_export.sh <session_name> <type> <slug>` を使ってよい。
これは実装側の scaffold 作成手順であり、プレイヤーに覚えさせるコマンドではない。

## First Response

相談型 trigger を受けたら、まず短く次を返す。

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

実生成明示型 trigger を受けたら、確認待ちの候補提示で止めない。

1. 直近シーンから最も自然な export type を1つ選ぶ
2. 判断できない場合だけ、候補を聞く
3. package を作る
4. `current/gm.md` の `Manga Export Candidates` に `status: queued` または `status: generating` と package path を残す
5. image gen skill / tool へ渡せる状態なら実生成を開始する
6. GM本文では、コマンドログや長い package 要約を出さず、短く「裏で進める」とだけ伝える
7. 直前の作中場面へ戻り、必要なら `1-3` 候補 + `4. 自由入力` でプレイヤーに渡す

実生成明示型でも、未確定秘密、関係段階、成人向け表現の公開分離、キャラID正本は守る。
画像生成が使えない環境では、`status: queued` として package と `image_gen_tasks.md` まで作り、本文は止めない。

## Export Types

export type は次の4種類に限定する。

- `model-sheet`: 三面図 / 立ち絵 / キャラシート。人物固定資料が目的
- `heroine-teaser`: ヒロインPV / 告知カット / 短い紹介。関係段階と秘密を守る
- `scene-card`: 名場面カード / 扉絵 / 1カット。直近場面や象徴的な瞬間向け
- `one-page`: 1ページ漫画。フル漫画化ではなく、短いページ構成に留める

フル漫画化、長編コミカライズ、連続ページ量産は標準導線にしない。
まず PV / 名場面 / 1ページ / 三面図から始める。

## Default Visual Style

manga export の画像生成は、ユーザーが明示しない限り**漫画 / イラスト**として出す。
実写、映画スチル、フォトリアル、3D、リアル人物写真へ寄せるな。

標準の visual mode:

```text
Japanese manga / anime-style illustration, expressive line art, controlled screentone or cel shading, cinematic composition, not photorealistic.
```

標準の negative visual prompt:

```text
photorealistic, live-action, real photo, cinematic still, 3D render, uncanny realism, watermark, garbled text
```

西新宿、代々木、佐渡など実在の土地を使う場合も、背景の質感だけを参照し、最終出力は漫画絵に変換する。
実写で出すのは、プレイヤーが `実写で` `写真風で` `フォトリアルで` と明示した時だけ。

## Background Generation Policy

実生成明示型では、漫画生成をプレイ進行の裏ジョブとして扱う。

- コマンドログ、長い package 要約、`Waiting for...` のような進捗表示をGM本文に出さない
- GM本文では `裏でscene-cardを作っておく` 程度の短い一文に留める
- 生成待ちでプレイヤーの選択を止めない
- 直前の場面を再掲し、必要なら `1-3` 候補 + `4. 自由入力` を出して続行する
- 生成完了後は、次のGM相談タイミングか自然な区切りで `生成できた / 失敗した / packageだけ残した` を短く伝える
- 生成物の長い説明、prompt全文、内部コマンドは `exports/...` 側に置き、本文へ混ぜない

例:

```text
裏でこの場面の scene-card を出しておく。作中は止めない。

女は四つ折りの紙を握ったまま、こちらの返事を待っている。

→ どうする？

1. まず紙の内容だけ見せてもらう
2. 名前と事情を聞いて、落ち着ける場所へ移る
3. 周囲の視線や尾行の有無を先に見る
4. 自由入力
```

## Output Path

manga export package は Git 管理外のローカル成果物として扱う。

```text
exports/<session_name>/manga/<YYYYMMDD>/<HHMMSS>_<type>_<slug>/
```

`<YYYYMMDD>` は日付ディレクトリ、`<HHMMSS>` は同日内の時刻を使う。
`<type>` は `model-sheet` / `heroine-teaser` / `scene-card` / `one-page` のいずれか。
`<slug>` は英数字、ハイフン、アンダースコアで短く付ける。

相談型の標準機能は、この package に入れるファイル / prompt を作るところまで。
実生成明示型では、package 作成後に image gen skill / tool へ投入し、生成済みファイルや参照先を `generated asset references` と `job_status.md` に残してよい。

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
lettering.md
image_gen_tasks.md
job_status.md
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

`GM-only Body Profile` の正確な身長、3サイズ、体重、カップ数は通常の公開用 prompt に入れない。
private / model reference で必要な場合だけ内部参照し、public teaser や recap では `visible height` と体型印象に変換する。

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

### lettering.md

写植 / セリフ / キャプションの正本を置く。

漫画生成では、画像AIに長い日本語を直接描かせると文字化けしやすい。
そのため、原則として画像生成では空吹き出し / 空キャプション枠を作り、正確な日本語は `lettering.md` に分離して後工程で載せる。

- reading direction: Japanese right-to-left / top-to-bottom
- font mood: 手書き寄り / 明朝寄り / ゴシック寄り / モノローグ寄り
- balloon style: 通常 / 小声 / 叫び / 内心 / ナレーション
- panel number
- speaker
- exact text
- placement hint
- priority: must-have / optional / cut if crowded

`lettering.md` の exact text は、画像生成 prompt にそのまま任せるのではなく、写植レイヤー / 画像編集 / 手動レタリングの正本として扱う。

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

`one-page` では task を原則2段階に分ける。

1. `art-base`: 空吹き出し / 空キャプション枠つきの漫画ページを生成する
2. `lettering`: `lettering.md` の exact text を後工程で載せる

最終成果物は、空吹き出しの `art-base` ではなく、文字入りの `lettered` 版とする。

Visual Character Sheet は image gen skill / tool へ渡す前に `prompt-ready` へ点検する。
`text-only` のままなら、まず `image prompt anchor`、`continuity locks`、`negative prompt / avoid` を整える。

### job_status.md

漫画生成ジョブの現在状態を置く。
相談型では `not requested` または `packaged`、実生成明示型では `queued` / `generating` / `generated` / `failed` を使う。

- mode: consultation / one-pass generation
- user approval: not requested / pending / granted by explicit generation request
- story blocking: forbidden
- package status: packaged / incomplete
- art-base status: not started / queued / generating / generated / failed
- lettering status: not needed / not started / queued / generated / failed
- output files:
  - TODO
- generated asset references:
  - TODO path / URL / seed / model / prompt version
- continuity issues:
  - TODO
- next user-facing update:
  - TODO short status only, no command logs

GM本文では `job_status.md` の長文を読ませない。
プレイヤーに返すのは `裏で生成中`、`生成できた`、`失敗したのでpackageだけ残した` 程度の短い状態に留める。

### publish_notes.md

公開 / 共有時の注意を置く。

- spoiler policy
- adult content separation
- credit / internal-only note
- what not to publish
- whether this is private, public teaser, or recap

成人向け表現は削除しないが、公開 / 集客用 package では分離・制御する。

## Package Creation Flow

1. 相談型なら作中時間を止める。実生成明示型なら漫画タスクだけをメタ処理し、物語本文は止めない
2. 入力を manga export request として扱う
3. `current/gm.md` の `Manga Export Candidates` を見て、なければ2-3個作る
4. 相談型ならプレイヤーに候補と export type を選ばせる。実生成明示型なら直近シーンから最も自然な type を1つ選ぶ
5. 必要な正本だけ読む
6. 主人公と対象ヒロインの Visual Character Sheet を確認する
7. `model sheet status` が `text-only` なら、矛盾点と不足を点検し、必要に応じて `prompt-ready` に上げる準備をする
8. 出力先 path と package file 構成を決める
9. `source.md` から `publish_notes.md` までの prompt package を作る
10. `image_gen_tasks.md` に image gen task を分解する
11. `job_status.md` を更新する
12. 相談型ではプレイヤーへ package の要約を返し、実生成するか確認する
13. 実生成明示型では、追加確認なしで image gen skill / tool へ投入できるなら投入し、GM本文は短い状態報告だけで物語へ戻す

実画像生成は、相談型では step 12 の確認後だけ。
実生成明示型では、最初の発話を確認として扱う。

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

相談型では、確認がない限り画像生成ツールを呼ばない。
実生成明示型では、ユーザーの「出して / 生成して / 裏で生成して」を確認として扱い、追加の確認待ちで物語を止めない。
ただし、画像生成ツールが使えない、成人向け公開範囲が曖昧、キャラID正本が不足している、未確定秘密を絵で確定しそうな場合は `job_status.md` を `queued` または `failed` にし、本文は止めずに短く理由だけ残す。
