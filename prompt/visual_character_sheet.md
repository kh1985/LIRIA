# prompt/visual_character_sheet

このファイルは、漫画化・画像生成用の Visual Character Sheet の正本だ。
目的はフル漫画化ではなく、主人公とヒロインのキャラクター設定資料を安定して作ること。
実際の画像生成はここでは行わず、Codex CLI の image gen skill に渡せる prompt anchor / model sheet prompt を保存する。

## 対象

Visual Character Sheet を作る対象は次だけ。

1. 主人公
2. session 配下の `cast/heroine/[名前].md` に昇格したヒロイン

作らない対象:

- モブ
- 名前付きNPC
- cast NPC
- 重要NPC
- 上位存在 / scene lead NPC

重要NPCが漫画化に必要になっても、今回のルールでは Visual Character Sheet を作らない。
まず主人公とヒロインだけを固定資料化する。

## Appearance Profile との違い

`Appearance Profile` は現在状態の見た目だ。
服装変更、疲労、怪我、髪型の乱れ、生活や事件による差分を扱う。

`Visual Character Sheet` は画像/漫画生成用の固定資料だ。
同じ人物として再生成するための外見ロック、色、服装の基準、表情、仕草、prompt anchor を扱う。

重複させすぎるな。
`Appearance Profile` から画像生成に必要な安定要素だけを抽出し、現在差分は `Appearance Profile` 側に残す。

## 作成タイミング

### 主人公

新規開始時に `current/player.md` の `Appearance Profile` から text-only の Visual Character Sheet を作る。
この時点で画像は生成しない。
三面図/turnaround は必須ではなく、image gen skill を使う段階で必要なら生成する。

### ヒロイン

ヒロイン初登場時に重い Visual Character Sheet を作らない。
ただし、初登場本文の外見描写は短く済ませない。
頭のてっぺんから爪先まで、髪、顔、体型、服装、足元、匂い、仕草を12〜20行で描写し、必要なら `appearance:` に仮置きする。

敵幹部、関係組織の主要人物、ルート鍵NPCも同じく、初登場本文では全身のキャラIDが立つ描写を行う。
ただし Visual Character Sheet を作る対象は主人公とヒロインだけであり、主要NPCや敵には作らない。

次のどれかが起きた時に、text-only Visual Character Sheet を作る。

1. session 配下の `cast/heroine/[名前].md` に昇格した時
2. 漫画化 / 画像生成 / ヒロインPV化の対象になった時
3. 再登場見込みがあり、外見・服装・顔つき・仕草を固定したい時

ヒロインの Visual Character Sheet は `cast/heroine/[名前].md` に置く。
モブ、名前付きNPC、cast NPC、重要NPCには作らない。

## model sheet status

Visual Character Sheet は `model sheet status` を必ず持つ。

- `none`: 未作成。対象外、またはまだ必要ない
- `text-only`: 文章資料だけ作成済み。画像生成はまだしない
- `prompt-ready`: image gen skill に渡せる prompt anchor と各種 prompt が整っている
- `image-generated`: 画像生成済み。参照アセットが `generated asset references` にある

通常の新規主人公とヒロイン昇格直後は `text-only` から始める。
`prompt-ready` に上げるのは、画像生成や漫画化の直前に、矛盾や未確定情報を点検してからにする。
`image-generated` へ上げるのは、実際に画像を生成し、参照先を保存した後だけ。

## キャラIDと generated asset references

Visual Character Sheet は外見固定の補助資料であり、キャラIDそのものの正本ではない。
キャラID、関係性、秘密、内面の正本は次に置く。

- 主人公: `current/player.md`
- ヒロイン: `cast/heroine/[名前].md`

`generated asset references` には、生成済み画像、立ち絵、model sheet、URL、seed、生成メモを置く。
これらは同一人物性を保つための補助参照であり、画像だけでキャラID、関係性、秘密、内面を確定しない。
画像と正本が矛盾する場合、正本を優先し、画像側は continuity issue として記録する。

## Visual Character Sheet 項目

以下の項目を同じ順番で持たせる。

```md
## Visual Character Sheet
- model sheet status: none | text-only | prompt-ready | image-generated
- front view notes:
- side view notes:
- back view notes:
- height / body type:
- hairstyle:
- face impression:
- default outfit:
- color palette:
- signature gestures:
- expression set:
- continuity locks:
- image prompt anchor:
- negative prompt / avoid:
- generated asset references:
```

書き方:

- `front view notes`: 正面から見たシルエット、顔、服の基準
- `side view notes`: 横顔、姿勢、髪や服の奥行き、身体の薄さ/厚み
- `back view notes`: 後ろ髪、背面シルエット、上着や小物の見え方
- `height / body type`: 数値よりも相対感、骨格、重心、体の印象
- `hairstyle`: 色、長さ、前髪、分け目、結い方、乱れやすさ
- `face impression`: 目つき、眉、口元、年齢感、第一印象
- `default outfit`: 基準服。現在差分ではなく再生成の基準
- `color palette`: 髪、目、肌、服、差し色。曖昧な場合は自然言語でよい
- `signature gestures`: 立ち方、手癖、視線、笑い方、距離感
- `expression set`: neutral / smile / angry / embarrassed / worried など
- `continuity locks`: 変えてはいけない外見要素、隠すべき秘密、未確定に残す要素
- `image prompt anchor`: 単独パネルやモデルシートで毎回使う安定 anchor
- `negative prompt / avoid`: 別人化、年齢ズレ、過剰な露出、世界観違い、未確定秘密の可視化など
- `generated asset references`: 生成済み画像、ファイル名、URL、seed、生成メモ。未生成なら空でよい

## image gen skill 用の出力形式

画像生成を実行する直前に、Visual Character Sheet から以下を text prompt として出せるようにする。
ここでも実際の画像生成はしない。

### model sheet prompt

用途: 三面図/turnaround 相当の設定画を作る時。
三面図/turnaround は必須ではない。必要になった時だけ image gen skill に渡す。

形式:

```text
model sheet prompt:
front / side / back, same character, plain background, full body, consistent outfit.
[character identity anchor]
[height / body type]
[hairstyle]
[face impression]
[default outfit]
[color palette]
[signature gestures]
continuity locks: [continuity locks]
avoid: [negative prompt / avoid]
```

### expression sheet prompt

用途: 表情差分を固定する時。

```text
expression sheet prompt:
same character, plain background, head and upper body, consistent hairstyle and outfit.
expressions: neutral, slight smile, guarded, angry, embarrassed, worried.
[image prompt anchor]
face impression: [face impression]
avoid: [negative prompt / avoid]
```

### outfit variant prompt

用途: 基準服を壊さず、場面用の服装差分を作る時。

```text
outfit variant prompt:
same character, full body, plain background, outfit variant for [scene / season / job].
keep identity: [image prompt anchor]
base outfit logic: [default outfit]
new outfit notes: [variant notes]
continuity locks: [continuity locks]
avoid: [negative prompt / avoid]
```

### single panel prompt anchor

用途: 漫画1コマ、扉絵、PVカットのキャラ固定 anchor。

```text
single panel prompt anchor:
[image prompt anchor]
keep consistent: hairstyle, face impression, body type, default color palette, signature gestures.
do not reveal unconfirmed secrets or inner state visually.
avoid: [negative prompt / avoid]
```

## 画像生成時のLIRIAルール

image gen skill に渡す prompt でも、LIRIA の物語ルールを守る。

- `GM` `シナリオ` `フラグ` `イベント` `好感度` `判定` などのメタ語を絵の説明に入れない
- ヒロインの自律性、生活、利害、関係段階を壊さない
- 未確定の秘密、能力の本質、隠れた内面を絵で確定しすぎない
- 公開 / 集客用の画像では、成人向け表現を分離・制御する
- 関係段階に合わない密着、露出、表情を prompt anchor に固定しない
- 同じヒロインを、別人のような髪色、年齢感、体型、顔つきにしない
- 主人公やヒロインの current な怪我・疲労・服装差分は、必要な時だけ `Appearance Profile` や scene notes から追加する

## prompt-ready へ上げる前の点検

`model sheet status` を `prompt-ready` にする前に確認する。

- 対象が主人公またはヒロインである
- `image prompt anchor` が1段落で読める
- `continuity locks` に変えてはいけない外見要素がある
- `negative prompt / avoid` に別人化、過剰な露出、未確定秘密の可視化禁止がある
- ヒロインの場合、`cast/heroine/[名前].md` の tone、Layer 5、forbidden、現在関係と矛盾していない
- 公開 / PV / 集客向けの場合、成人向け表現を通常 prompt から分離できる
