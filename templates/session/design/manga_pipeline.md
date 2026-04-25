# Manga Pipeline

> 通常は package / prompt package 化まで。プレイヤーが「漫画を出して」「画像も生成して」と明示した時だけ、生成確認済みの裏ジョブとして扱う。

## Scope

- Natural language trigger: 漫画化 / 1ページ漫画 / ヒロインPV / 三面図 / 立ち絵 / キャラシート
- Standard output: `exports/<session_name>/manga/<YYYYMMDD>/<HHMMSS>_<type>_<slug>/`
- Standard package: `source.md`, `brief.md`, `character_refs.md`, `name.md`, `panel_prompts.md`, `lettering.md`, `image_gen_tasks.md`, `job_status.md`, `publish_notes.md`
- Standard stop point: 相談型は package 作成と image gen tasks 分解まで
- Actual generation: 相談型はプレイヤー確認後のみ。実生成明示型は発話を確認として扱い、追加確認で止めない
- Internal helper: GM/Codex は必要なら `bash scripts/create_manga_export.sh <session_name> <type> <slug>` で雛形を作ってよい。プレイヤーに覚えさせるコマンドではない

## Trigger Modes

- consultation: `漫画化したい` `この場面を漫画にして` など。候補提示と package 作成で止め、生成確認を待つ
- one-pass generation: `漫画を出して` `画像も生成して` `このシーンを出して` `裏で生成して` など。package 作成後、image gen skill / tool へ投入できるなら投入する

one-pass generation では物語を止めない。
GM本文にコマンドログや長い進捗を出さず、短く `裏で生成中` とだけ伝え、直前の場面へ戻る。

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
- `lettering.md`: 正確なセリフ、キャプション、吹き出し位置。画像AIには空吹き出しを作らせ、文字は後工程で載せる
- `image_gen_tasks.md`: image gen skill / tool へ渡す前のタスク分解。相談型ではここでは生成しない
- `job_status.md`: consultation / one-pass generation、approval、queued / generating / generated / failed、出力ファイル、生成参照、短い次報告
- `publish_notes.md`: 公開可否、spoiler、成人向け表現の分離、公開しない情報

## Character Identity Rules

- 主人公のキャラID正本は `current/player.md`
- ヒロインのキャラID正本は `cast/heroine/[名前].md`
- 画像、立ち絵、model sheet、URL、seed は `generated asset references` として扱う
- 画像だけでキャラID、関係性、秘密、内面を確定しない
- 画像と正本が矛盾する場合、正本を優先し、画像は continuity issue として記録する
- `GM-only Body Profile` の正確な身長、3サイズ、体重、カップ数は公開用 prompt に入れない。private / model reference で必要な時だけ内部参照し、公開用では visible height と体型印象に変換する

## Guardrails

- consultation では作中時間を止め、通常シーンとして進めない
- one-pass generation では漫画タスクだけを裏で処理し、物語の受け渡しは止めない
- consultation ではいきなり画像生成しない
- プレイヤーにCLIコマンドを覚えさせない
- Visual Character Sheet は主人公とヒロインだけを `prompt-ready` 点検する
- メタ発言を絵や台詞に混ぜない
- 1ページ漫画は、空吹き出しの下絵で終わらせず、`lettering.md` を使って文字入り版まで作る
- 未確定秘密を絵で確定しすぎない
- ヒロインの自律性と現在の関係段階を壊さない
- 公開 / 集客用は成人向け表現を分離・制御する
- フル漫画化ではなく、まず PV / 名場面 / 1ページ / 三面図から始める
