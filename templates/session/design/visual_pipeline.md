# Visual Pipeline

> 画像生成はまだ実行しない。ここは Codex CLI の image gen skill に渡す前の運用方針と、公開 / 漫画化時の分離ルールを置く場所。

## Scope

- Visual Character Sheet 対象: 主人公、ヒロインのみ
- 対象外: モブ、名前付きNPC、cast NPC、重要NPC、上位存在
- 主人公の正本: `current/player.md` の `Visual Character Sheet`
- ヒロインの正本: `cast/heroine/[名前].md` の `Visual Character Sheet`

## Model Sheet Status

- `none`: 未作成
- `text-only`: 文章資料だけ作成済み
- `prompt-ready`: image gen skill に渡せる prompt anchor / model sheet prompt が整っている
- `image-generated`: 生成済みアセット参照が保存されている

## Image Gen Handoff

image gen skill に渡す直前に、正本の Visual Character Sheet から以下を組み立てる。

- `model sheet prompt`: front / side / back, same character, plain background, full body, consistent outfit
- `expression sheet prompt`
- `outfit variant prompt`
- `single panel prompt anchor`

## Guardrails

- メタ語を prompt に入れない
- ヒロインの自律性と現在の関係段階を壊さない
- 未確定の秘密や内面を絵で確定しすぎない
- 公開 / 集客用は成人向け表現を分離・制御する
- 三面図/turnaround は必須ではなく、必要になった段階で生成する
- 漫画化 / ヒロインPV / 1ページ化は `design/manga_pipeline.md` と `prompt/manga_export.md` の package 化ルールを通してから行う
