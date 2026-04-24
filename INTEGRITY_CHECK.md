# INTEGRITY_CHECK

## 目的

セーブ後や大きな改修後に、どのファイルが正で、どこがズレているかを手で追えるようにする。

main path は session 配下の `current/*`、`cast/*`、`design/*`、`indexes/*`、`archive/*`。
session 直下 mirror や repo ルート cast は legacy read-only fallback として別扱いにする。

## いつ使うか

- プレイ中に手動セーブした直後
- `GALGE.md` や save 構造を大きく触った直後
- `bash play.sh resume <scenario> <session_name>` の前に不安がある時
- legacy layout から session-scoped layout へ移行した直後
- 複数 session を並行運用し始めた時

## チェック順

### 1. session scaffold

見る場所:

- `saves/<session_name>/session.json`
- `saves/<session_name>/current/`
- `saves/<session_name>/cast/heroine/`
- `saves/<session_name>/cast/npc/`
- `saves/<session_name>/design/`
- `saves/<session_name>/indexes/`
- `saves/<session_name>/archive/`
- `exports/<session_name>/manga/`（package を作った場合だけ。Git管理外）

確認:

- 新規 session が session 配下だけで self-contained になっている
- 別 session の cast や current へ書き込んでいない
- `session.json` が scenario と session 名を示している
- `archive/` は `chapters/` `events/` `logs/` に分かれている

### 2. current layer

見るファイル:

- `saves/<session_name>/current/player.md`
- `saves/<session_name>/current/gm.md`
- `saves/<session_name>/current/harem.md`
- `saves/<session_name>/current/hotset.md`

確認:

- `player.md` と `gm.md` の現在フェーズ / 日付が一致している
- `hotset.md` の現在フェーズ / 再開アンカーが `gm.md` と矛盾していない
- `hotset.md` に複数時点の再開アンカーが混在していない
- `player.md` の HP / 残回数 / コンディションが今の場面に合っている
- `player.md` に `Appearance Profile` があり、身長、体型、基本服装、髪型、顔つき、雰囲気が再開時に読める
- `player.md` に主人公の `Visual Character Sheet` があり、`model sheet status`、`image prompt anchor`、`negative prompt / avoid` が読める
- `player.md` に `Ability Constraint Profile` があり、output scale、trigger condition、range / target、uses / cooldown、cost、trace、collateral、social risk、relationship risk、escalation rule が落ちていない
- `player.md` に `Work Profile` と `Life Base` があり、仕事、収入、生活ランク、拠点自然性が current から読める
- `player.md` の `Equipment / Tools` が、攻撃力/防御力ではなく、行動選択肢、リスク、痕跡、関係リスクとして整理されている
- `gm.md` の進行中フックが 1-3 本に収まっている
- active な脅威クロックが 2 以上あるなら、`gm.md` か `hotset.md` に直接圧候補が最低 1 本ある
- `gm.md` に脅威クロック、勢力クロック、直近の後遺症、直近の転機候補、直近のリアルタイム発見がある
- `gm.md` に `知識スコープ台帳` があり、`known / suspected / unknown` が hidden proper noun ごとに整理されている
- `gm.md` に `Knowledge Boundary / Anti-Leading` があり、NPC/ヒロインが未発見情報へ不自然に誘導しない境界がある
- `gm.md` に `Anti-Meta Dialogue` のガードがあり、GM、シナリオ、フラグ、イベント、好感度、判定を台詞へ出さない運用になっている
- `gm.md` に `Manga Export Candidates` があり、漫画化 / ヒロインPV / 三面図 / 立ち絵 / キャラシートの候補を2-3個まで保持できる
- packaged / generated の Manga Export Candidate は package path と status を持ち、長い prompt 本文を current に抱え込んでいない
- `gm.md` の勢力クロックやフックが、`Organization Doctrine Layer` の接触面や外圧と矛盾していない
- `gm.md` に `プレイヤー観測メモ（軽量）` があり、5 行以内で保たれている
- `harem.md` の関係フックと、各ヒロインの現在地が今のフェーズに合っている
- `harem.md` に `Heroine Crisis Role` があり、frontline / support / civilian / wildcard と危機時の行動傾向が読める
- `harem.md` のヒロイン知識スコープが `gm.md` と矛盾していない
- `player.md` の秘密管理と `gm.md` の知識スコープ台帳の shared / hidden の境界が矛盾していない
- 日数だけが進んだ章で、cast file の年齢ラベルが不用意に増えていない
- AFFINITY 5 ヒロインに hidden 深化ベクトル欄があり、直近 scene で少しずつ更新されている
- active な hidden ヒロイン間ベクトルは、今動いているペアだけに絞られている

### 3. cast layer

見るファイル:

- `saves/<session_name>/cast/heroine/*.md`
- `saves/<session_name>/cast/npc/*.md`
- `saves/<session_name>/indexes/cast_index.md`

確認:

- `current/hotset.md` の優先 cast が同じ session 配下に存在する
- `bond` `AFFINITY` が `current/harem.md` と矛盾していない
- `tone` `Layer 5` `context` が現在の関係に巻き戻っていない
- 呼称や距離感が current 側の状態と食い違っていない
- ヒロインの `Visual Character Sheet` が、必要になった人物だけにあり、`model sheet status` が `none` / `text-only` / `prompt-ready` / `image-generated` のどれかになっている
- `prompt-ready` または `image-generated` のヒロインに `image prompt anchor`、`continuity locks`、`negative prompt / avoid` がある
- モブ、名前付きNPC、cast NPC、重要NPCに Visual Character Sheet を作っていない
- 主役級の再登場 NPC に `cast/npc/*.md` がある
- 上位存在 / scene lead NPC が bond 0 のままでも `cast/npc/*.md` で管理されている
- 現在の標準服や社会的立場の変化が、古い初期設定に巻き戻っていない
- `最終更新` の記述が古くてもよいが、現在の真実と矛盾していない
- 台詞事故が起きやすい hidden proper noun は、誰が `known` か current から引ける
- hidden 深化ベクトルが全部同じ値で並んでいない
- hidden ヒロイン間ベクトルが全ペア総当たりで膨れていない

### 4. design layer

見るファイル:

- `saves/<session_name>/design/villain_design.md`
- `saves/<session_name>/design/visual_pipeline.md`
- `saves/<session_name>/design/manga_pipeline.md`

確認:

- `gm.md` の勢力名が `villain_design.md` の定義と一致している
- `villain_design.md` に `Organization Doctrine Layer` があり、組織理念、目的、規模、主要人物、contact surface、弱い継ぎ目、内部矛盾、外部レバレッジが残っている
- `manga_pipeline.md` に export type、package 構成、image gen tasks 分解、実生成前のユーザー確認が残っている
- `manga_pipeline.md` と `visual_pipeline.md` が、Visual Character Sheet を主人公とヒロインだけに限定している
- 顕在化中の勢力が、存在しないボスや幹部を参照していない
- `gm.md` の勢力クロックが空欄ではなく、current の脅威クロックへ落ちている
- current にある接触面や外圧が、design 側の長期設計から切り離された即興設定になっていない
- design は長期設計であり、直近の一時 echo を抱え込みすぎていない

### 5. archive / index layer

見るファイル:

- `saves/<session_name>/indexes/*`
- `saves/<session_name>/archive/*`

確認:

- index に書いた参照先ファイルが実在する
- `hotset.md` や `gm.md` から archive を引く条件が書かれているなら、その参照先が存在する
- archive に送ったイベントが current 側へ重複して残りすぎていない
- 生ログは `archive/logs/` に入り、current に長文ログとして残っていない

### 6. manga export package

見る場所:

- `exports/<session_name>/manga/<timestamp>_<type>_<slug>/`

確認:

- package を作った場合だけ存在する。未作成ならなくてよい
- Git管理外のローカル成果物であり、`saves/*` や実プレイログの代替ではない
- `source.md`、`brief.md`、`character_refs.md`、`name.md`、`panel_prompts.md`、`image_gen_tasks.md`、`publish_notes.md` が揃っている
- `image_gen_tasks.md` はタスク分解であり、実生成済み扱いにしていない
- Visual Character Sheet は主人公とヒロインだけを参照し、NPC用の Visual Character Sheet を新設していない
- `character_refs.md` がキャラID正本として `current/player.md` と `cast/heroine/[名前].md` を指している
- 画像、立ち絵、model sheet、seed、URL は `generated asset references` の補助参照であり、キャラID正本扱いしていない
- `known / suspected / unknown`、未確定秘密、成人向け表現の公開分離方針が package 内に残っている

## Legacy read-only fallback

古い session でだけ確認する場所:

- `saves/<session_name>/player.md`
- `saves/<session_name>/gm.md`
- `saves/<session_name>/harem.md`
- `saves/<session_name>/villain_design.md`
- repo ルートの cast ディレクトリ

扱い:

- main path ではない
- stale の可能性がある
- 読んでもよいが、書き戻さない
- 新規 session では作らない
- legacy にしかない情報は session 配下へ移してから使う

mirror が stale でも、それを理由に `current/*` を巻き戻さない。

## 判定

### hard error

すぐ直す。

- フェーズや日付がズレている
- `AFFINITY` や `bond` が正本間で矛盾している
- hotset が別の章や別 session を指している
- hotset に複数の再開アンカーが残っている
- `unknown` や `suspected` のキャラが hidden proper noun を既知みたいに喋る
- NPC/ヒロインが GM、シナリオ、フラグ、イベント、好感度、判定などを作中台詞として喋る
- `player.md` と `gm.md` で秘密共有範囲が食い違っている
- `player.md` から `Appearance Profile` または `Ability Constraint Profile` が消えている
- 主人公の `Visual Character Sheet` が消えている、または `model sheet status` が不正
- `prompt-ready` / `image-generated` のヒロインから `image prompt anchor` または `negative prompt / avoid` が消えている
- manga export package から `image_gen_tasks.md` が消えている、またはユーザー確認前に実生成済み扱いになっている
- manga export package が画像だけを根拠にキャラID、関係性、秘密、内面を確定している
- 能力の output scale、uses / cooldown、trace、relationship risk が current から読めない
- `Work Profile` または `Life Base` が current から読めず、仕事/生活の自然な接点が復元できない
- 誕生日イベントや年単位スキップもないのに、年齢ラベルだけが更新されている
- AFFINITY 5 ヒロインの hidden 深化ベクトルが存在しない、または全員ゼロのまま
- 主役級の再登場 NPC に session-scoped cast file がない
- 存在しない勢力やイベントを参照している
- 別 session の cast を読んでいる、または書いている

### soft drift

次のセーブで直す。

- `最終更新` 文が古い
- cast ファイルに古い `echo` が残っている
- archive 送り済みなのに current 側の要約がやや長い
- `hotset.md` が正本扱いされそうな文面になっている
- Equipment が攻撃力/防御力だけの装備スロットになっている
- Visual Character Sheet と `Appearance Profile` が重複しすぎて、現在差分と固定資料の境界が曖昧になっている
- Organization Doctrine の詳細が current に長く入りすぎ、design と重複している
- `Heroine Crisis Role` が古い危機状況のまま更新されていない

### acceptable stale

すぐ直さなくてよい。

- legacy mirror が残っているが main path に混ざっていない
- archive 本文が未バックフィルだが、index と current で運用は回る
- 既存の個人プレイ資産が repo 外で保管されていても、本体の main path に混ざらない

## 最低限の確認コマンド

```bash
bash scripts/check_session_integrity.sh <session_name>
```

```bash
rg -n "現在フェーズ|Appearance Profile|Visual Character Sheet|model sheet status|image prompt anchor|Ability Constraint Profile|Work Profile|Life Base|Equipment|Organization Doctrine|Heroine Crisis Role|Anti-Meta|Knowledge Boundary|AFFINITY|bond|直近の後遺症|勢力クロック|転機候補|リアルタイム発見|プレイヤー観測メモ" \
  saves/<session_name>/current \
  saves/<session_name>/cast \
  saves/<session_name>/design
```

```bash
find saves/<session_name> -maxdepth 3 -type d | sort
```

既存の個人プレイ資産を確認する場合だけ、退避先の `<session_name>` を指定する。
