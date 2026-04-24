# Manga Pipeline

> 画像生成はまだ実行しない。ここは自然文の漫画化依頼を manga export package / prompt package に変換する運用方針を置く場所。

## Scope

- Natural language trigger: 漫画化 / 1ページ漫画 / ヒロインPV / 三面図 / 立ち絵 / キャラシート
- Standard output: `exports/<session_name>/manga/<timestamp>_<type>_<slug>/`
- Standard package: `source.md`, `brief.md`, `character_refs.md`, `name.md`, `panel_prompts.md`, `image_gen_tasks.md`, `publish_notes.md`
- Standard stop point: package 作成と image gen tasks 分解まで
- Actual generation: プレイヤー確認後のみ
- Internal helper: GM/Codex は必要なら `bash scripts/create_manga_export.sh <session_name> <type> <slug>` で雛形を作ってよい。プレイヤーに覚えさせるコマンドではない

## Export Types

- `model-sheet`: 三面図 / 立ち絵 / キャラシート
- `heroine-teaser`: ヒロインPV / 告知カット
- `scene-card`: 名場面カード / 扉絵 / 1カット
- `one-page`: 1ページ漫画

## Candidate Sources

- 直近シーン
- ヒロイン初登場
- 関係が動いた瞬間
- 危機 / 保護 / 秘密の匂わせ

候補は `current/gm.md` の `Manga Export Candidates` に2-3個だけ持つ。
候補は相談メモであり、未確定情報を確定させる正本ではない。

## Package Checklist

- `source.md`: 切り出し元、読んだ正本、known / suspected / unknown、絵で確定してはいけない秘密
- `brief.md`: export type、用途、トーン、必須要素、避けること、成人向け表現の扱い
- `character_refs.md`: 主人公とヒロインの Visual Character Sheet、キャラID正本、generated asset references、prompt-ready 点検、current appearance delta
- `name.md`: internal name、display title、slug、spoiler-safe title、caption
- `panel_prompts.md`: コマ / カットごとの構図、表情、台詞、背景、negative prompt
- `image_gen_tasks.md`: image gen skill / tool へ渡す前のタスク分解。ここでは生成しない
- `publish_notes.md`: 公開可否、spoiler、成人向け表現の分離、公開しない情報

## Character Identity Rules

- 主人公のキャラID正本は `current/player.md`
- ヒロインのキャラID正本は `cast/heroine/[名前].md`
- 画像、立ち絵、model sheet、URL、seed は `generated asset references` として扱う
- 画像だけでキャラID、関係性、秘密、内面を確定しない
- 画像と正本が矛盾する場合、正本を優先し、画像は continuity issue として記録する

## Guardrails

- 作中時間を止め、通常シーンとして進めない
- いきなり画像生成しない
- プレイヤーにCLIコマンドを覚えさせない
- Visual Character Sheet は主人公とヒロインだけを `prompt-ready` 点検する
- メタ発言を絵や台詞に混ぜない
- 未確定秘密を絵で確定しすぎない
- ヒロインの自律性と現在の関係段階を壊さない
- 公開 / 集客用は成人向け表現を分離・制御する
- フル漫画化ではなく、まず PV / 名場面 / 1ページ / 三面図から始める
