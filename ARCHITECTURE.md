# ARCHITECTURE

## 目的

`LIRIA` の実行構成、source of truth、session layout、legacy 互換の境界を一枚で見渡すための設計図。

関連文書:

- `docs/architecture/MEMORY_MODEL.md`: 記憶の分類と圧縮ルール
- `docs/validation/INTEGRITY_CHECK.md`: save / resume 周りの整合チェック
- `docs/validation/VALIDATION.md`: 長編・複数 session 前提の回帰確認
- `TODO.md`: 移行ロードマップ

## 基本方針

- 新規 session は self-contained にする
- `current` は今すぐ必要な状態だけ持つ
- `cast` は session ごとのキャラ長期設定を持つ
- `design` は長期設計を持つ
- `indexes` は archive を引くための軽量目次を持つ
- `archive` は履歴とログを持つ
- `hotset` は再開用の derived cache であり、正本ではない
- session 直下 mirror と repo ルート cast は main path から外す

## レイヤ構成

| レイヤ | 役割 | 主ファイル |
|---|---|---|
| Launcher Layer | CLI 起動、scenario 選択、session 作成 / 再開 | `play.sh`, `scenarios/*/config.sh`, `*.command` |
| Prompt Layer | GM の実行ルール | `GALGE.md`, `prompt/*.md` |
| Style Layer | 文体ルールと参考作品エンジン | `style/rules.md`, `style/reference.md`, `style/defaults/*` |
| Story Reference Layer | 漫画/作品/ジャンル/実ログから抽出した抽象的な物語エンジン。固定作品リストではない | `prompt/story_reference.md`, `saves/session_XXX/design/story_reference.md` |
| Story Design Layer | 物語が霧にならないための最小背骨と組織キャスト設計 | `saves/session_XXX/design/story_spine.md`, `saves/session_XXX/design/organization_cast.md`, `saves/session_XXX/design/villain_design.md` |
| Save Layer | 現在状態の保存 | `saves/session_XXX/current/*` |
| Cast Layer | session 単位のキャラ個別設定 | `saves/session_XXX/cast/heroine/*.md`, `saves/session_XXX/cast/npc/*.md` |
| Design Layer | 世界や敵の補助設計 | `saves/session_XXX/design/*` |
| Index Layer | archive 参照用の軽量索引 | `saves/session_XXX/indexes/*` |
| Archive Layer | 章、イベント、生ログ | `saves/session_XXX/archive/*` |
| Export Layer | Git 管理外の漫画化 prompt package | `exports/session_XXX/manga/*` |

## Style Layer

Style Layer は、`style/rules.md`、`style/reference.md`、`style/defaults/*` から成る描写品質レイヤである。

- Style Layer は adult 専用ではない
- 日常、生活、恋愛、事件、危機、コメディ、シリアス、親密シーンを含む全体の文体、温度感、描写密度、会話の間、余韻、視点を支える
- `prompt/runtime.md`、`prompt/romance.md`、`prompt/combat.md`、`prompt/villain_engine.md` は必要に応じて Style Layer を参照する
- 参照は本文模倣ではなく、構造、温度、リズム、余白、視点、描写密度の抽出として扱う
- 参照は常に LIRIA のキャラ、舞台、関係性へ変換して使う
- Style Layer は描写品質を支えるレイヤであり、旧ハーレム攻略ロジックや旧ゲーム目的とは分離して保護する

旧要件整理で見直すべきなのは、`女を堕とす`、`ハーレム攻略主目的`、`攻略報酬`、`AFFINITY到達ボーナス`、`単一ボス討伐標準`、`装備スロット`、`G通貨 / 拠点投資` のような旧目的語と旧システム前提である。Style Layer 自体は削除対象にしない。

## Story Design Draft

現時点の設計案。まだ重い一本道シナリオは採用しない。

LIRIA は自由入力 TRPG 感を重視するため、結末固定のシナリオ表ではなく、以下の 2 つを薄く持つ。

1. Story Reference Layer
2. Organization Cast Pre-Generation
3. Minimal Story Spine

### Story Reference Layer

漫画や作品のストックは `prompt/story_reference.md` に抽象エンジンとして持つ。
固有名詞、台詞、キャラ、展開を再現するためではなく、物語の動き方だけを抜く。
ユーザーが会話中に挙げた作品名は例・方向性ヒントであり、固定参照元として正本化しない。

session ごとに採用したエンジンだけを `design/story_reference.md` に保存し、そこから `story_spine.md` と `organization_cast.md` へ変換する。
50作品の候補棚は `references/story_media_stock.md` に置くが、これは起動 prompt へ常時読み込まない。必要な時だけ 1〜3 本を抽象化する。

### Organization Cast Pre-Generation

関係組織を生成する時点で、主要人物を 3〜5 人ほど裏で作る。

目的は、敵や関係者が出た時に `gm.md` の抽象メモだけで喋らせず、最初から「組織の顔」として扱うこと。
名前や所属が未確定でも、`配置確認の男`、`現場調整役` のような仮 ID で `cast/npc/*.md` に置いてよい。

役割例:

- 現場確認担当
- 交渉担当
- 内部矛盾を抱える担当
- 組織理念を信じ切っている担当
- ヒロイン生活圏に食い込む担当

主要人物は、以下を最低限持つ。

- role in organization
- public face
- belief
- contradiction
- protected thing
- unacceptable line
- pressure method
- concrete tools
- knows / suspects / unknown
- relationship hook with protagonist
- relationship hook with heroine/NPC
- speech discipline

### Minimal Story Spine

session ごとに、薄い物語の背骨を持つ。
これはプレイヤーを一本道へ乗せるものではなく、GM が「この事件は何の話か」を見失わないための内部設計である。

必須項目:

- Main Question: この物語が問うこと
- Reveal Ladder: 真相が見える段階
- Pressure Direction: 組織が放置時に何を進めるか
- Heroine Tie: ヒロインがどこで揺れるか
- End Choice Seeds: 終盤で選びうる天秤

例:

```text
Main Question:
人は何を戻せば本人に戻るのか？

Reveal Ladder:
1. 上司の異常
2. 社員証・鍵・席で本人性を測る担当者
3. 会社内に同じ処理を受けた人がいる
4. 主人公の能力が、組織にとって利用価値を持つ
5. 梓の生活か真相公開かを選ぶ局面
```

### Reference Stock Notes

詳細なストックは `prompt/story_reference.md` を正本とする。
ここでは、抽出する構造の例だけを示す。

抽象カード例:

- State Secret Engine: 制度や記録の奥に真相がある
- Inherited Wound Engine: 長い因縁、継承、親世代の罪が現在へ届く
- Rule-Bound Encounter Engine: 敵や接触者が明確なルールで場を支配する
- Ideological Organization Engine: 組織の大義と個人感情が衝突する
- Workplace / Life Pressure Romance: 仕事、信用、生活上の圧で恋愛関係が動く

運用案:

- Research Mode: 必要な時だけ作品やジャンルから抽象カードを作る
- Build Mode: 抽象カードを混ぜて Story Spine を作る
- Play Mode: Story Spine と組織キャストを使って自由入力を処理する

現時点の結論:

- 組織キャストは厚くする
- ストーリーは薄くする
- ただし背骨は持つ
- まずは `Organization Cast Pre-Generation + Minimal Story Spine` で検証する

## Target Layout

```text
LIRIA/
├── play.sh
├── scenarios/
├── prompt/
├── style/
├── templates/
│   └── session/
│       ├── session.json
│       ├── current/
│       │   ├── player.md
│       │   ├── gm.md
│       │   ├── harem.md
│       │   └── hotset.md
│       ├── cast/
│       │   ├── heroine/
│       │   └── npc/
│       ├── design/
│       │   ├── villain_design.md
│       │   ├── visual_pipeline.md
│       │   └── manga_pipeline.md
│       ├── indexes/
│       │   ├── cast_index.md
│       │   ├── decision_index.md
│       │   └── event_index.md
│       └── archive/
│           ├── chapters/
│           ├── events/
│           └── logs/
├── saves/
    └── session_XXX/
        ├── session.json
        ├── current/
        ├── cast/
        ├── design/
        ├── indexes/
        └── archive/
└── exports/
    └── session_XXX/
        └── manga/
            └── YYYYMMDD/
                └── HHMMSS_<type>_<slug>/
```

## Runtime Relationship

```mermaid
flowchart TD
    play["play.sh"]
    scenario["scenarios/<id>/config.sh"]
    prompt["GALGE.md + prompt/*.md"]
    style["style/*"]
    session["saves/<session_name>/session.json"]
    current["saves/<session_name>/current/*"]
    hotset["saves/<session_name>/current/hotset.md"]
    heroine["saves/<session_name>/cast/heroine/*.md"]
    npc["saves/<session_name>/cast/npc/*.md"]
    design["saves/<session_name>/design/*"]
    indexes["saves/<session_name>/indexes/*"]
    archive["saves/<session_name>/archive/*"]

    play --> scenario
    scenario --> prompt
    prompt --> style
    prompt --> session
    prompt --> current
    current --> hotset
    hotset --> heroine
    hotset --> npc
    hotset --> design
    indexes --> archive
    prompt --> archive
```

## Source Of Truth

| 情報 | 正本 |
|---|---|
| 現在フェーズ / 現在フック / 脅威クロック / 勢力クロック | `saves/<session_name>/current/gm.md` |
| 知識スコープ / 誰が何を知っているか | `saves/<session_name>/current/gm.md` |
| Knowledge Boundary / Anti-Leading / Anti-Meta Dialogue Guard | `saves/<session_name>/current/gm.md` |
| Appearance Profile / Ability Constraint Profile / Work Profile / Life Base | `saves/<session_name>/current/player.md` |
| 主人公の Visual Character Sheet | `saves/<session_name>/current/player.md` |
| 主人公のキャラID / 関係性 / 秘密 / 内面 | `saves/<session_name>/current/player.md` |
| プレイヤー能力の現在仕様 / HP / 残回数 / Equipment / Tools | `saves/<session_name>/current/player.md` |
| Relationship / Heroine Network 全体状態 / 嫉妬 / 関係フック | `saves/<session_name>/current/harem.md` |
| Heroine Crisis Role | `saves/<session_name>/current/harem.md` |
| AFFINITY / bond の current value | `saves/<session_name>/current/harem.md` |
| ヒロイン個別の tone / Layer / fixed memory / 呼称 / Visual Character Sheet | `saves/<session_name>/cast/heroine/*.md` |
| ヒロインのキャラID / 関係性 / 秘密 / 内面 | `saves/<session_name>/cast/heroine/*.md` と current の知識スコープ |
| NPC 個別の tone / role / fixed memory | `saves/<session_name>/cast/npc/*.md` |
| GM-only Body Profile / 正確な身長・3サイズ等の裏設定 | 成人ヒロインは `saves/<session_name>/cast/heroine/*.md`、成人主要NPCは `saves/<session_name>/cast/npc/*.md` |
| 関係組織 / 外圧 / Organization Doctrine Layer | `saves/<session_name>/design/villain_design.md` |
| image gen skill 連携方針 / visual pipeline | `saves/<session_name>/design/visual_pipeline.md` |
| 自然文漫画化 / manga export pipeline | `saves/<session_name>/design/manga_pipeline.md` |
| manga export package / prompt package | `exports/<session_name>/manga/*` |
| 画像、立ち絵、model sheet、seed、URL | Visual Character Sheet の `generated asset references`。補助参照でありキャラID正本ではない |
| 章履歴 / イベント履歴 / 生ログ | `saves/<session_name>/archive/*` |
| archive 参照索引 | `saves/<session_name>/indexes/*` |
| 再開1ターン目の軽量入口 | `saves/<session_name>/current/hotset.md` |

`hotset.md` は正本ではない。保存時に現在の `current/*` と必要な cast / design / index から上書き再生成する。

## Session Lifecycle

### new

1. launcher が session 名を受け取る。未指定なら未使用名を採番する
2. `templates/session/` から `saves/<session_name>/` を scaffold する
3. `session.json` に scenario id、作成時刻、schema version を記録する
4. GM はその session 配下の `current/*`、`cast/*`、`design/*`、`indexes/*`、`archive/*` だけを初期化する
5. repo ルートの cast や別 session の cast には書かない

### resume

1. session 名を受け取る。未指定なら launcher の既定ルールで選んだ session 名を出力する
2. `session.json` と `current/gm.md` を読む
3. 現在フェーズ、現在フック、進行中クロックを確認する
4. `current/hotset.md` を読む。古い場合は再生成する
5. hotset に必要な session-scoped cast だけ読む
6. 必要なら `design/*` と `archive/*` を引く
7. 再開1シーン目を hotset の圧と入口から始める

## Episode Pipeline

1. `current/gm.md` から現在フックを 1-3 本取る
2. 必要なら `design/villain_design.md` から Organization Doctrine、接触面、外圧、弱い継ぎ目を取る
3. エピソードタイプを決める
4. 今回の対象キャラを決め、該当 session の `cast/*` だけ読む
5. style / reference を引く
6. フック / キャラ / 脅威 / 勢力 / プレイヤー行動モデルへ変換する
7. 本文生成
8. 結果を `current/*` に反映
9. 必要なイベントだけ `archive/*` へ追記
10. `hotset.md` を上書き再生成する

## Legacy Read-Only Fallback

古い session には次が残る場合がある。

- `saves/<session_name>/player.md`
- `saves/<session_name>/gm.md`
- `saves/<session_name>/harem.md`
- `saves/<session_name>/villain_design.md`
- repo ルートの cast ディレクトリ

これらは read-only fallback であり、main path ではない。
新規 session と通常保存では作らない、同期しない、正本扱いしない。

旧 session を読む必要がある時だけ fallback として参照し、読み取った情報は session 配下の `current/*`、`cast/*`、`design/*` へ移す。
互換維持のために live write path を複雑化しない。

## Integrity Guardrails

- session 間で cast を共有しない
- `current/player.md`、`current/gm.md`、`current/hotset.md` の現在フェーズ / 再開アンカーを揃える
- `hotset.md` に複数時点の再開アンカーを残さない
- `Appearance Profile`、`Ability Constraint Profile`、`Work Profile`、`Life Base`、`Equipment / Tools` を圧縮で落とさない
- `Organization Doctrine Layer` は design を正本にし、current には今効く接触面と外圧だけを置く
- NPC/ヒロインの台詞に GM、シナリオ、フラグ、イベント、好感度、判定などのメタ語を出さない
- 画像だけでキャラID、関係性、秘密、内面を確定しない。`current/player.md` と `cast/heroine/*.md` を正本にする
- manga export package は `scripts/create_manga_export.sh` で雛形を作ってよいが、プレイヤーに CLI を覚えさせる導線にはしない
- `docs/maintenance/core_notes.md`、`README.md`、architecture docs に live session state を置かない
- 既存の個人セッションは repo 外の legacy asset として扱い、本体の固定参照にしない
- `bash scripts/check_session_integrity.sh <session_name>` で軽量チェックを回す
