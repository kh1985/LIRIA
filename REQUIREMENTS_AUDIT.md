# REQUIREMENTS_AUDIT

## Purpose

この文書は、旧 inner-galge 由来の機能要件・非機能要件を棚卸しし、LIRIA v1 の正本定義に照らして `KEEP / ADAPT / DEFER / REMOVE / REVIEW` に分類するための監査メモである。

LIRIA の正本定義:

> LIRIAは、恋愛・生活・事件を通して、プレイヤーのインナーと関係性が変化していくAI TRPG型恋愛シミュレーション。

## Audit Scope

確認対象:

- `README.md`
- `CONCEPT.md`
- `REQUIREMENTS.md`
- `MEMORY_MODEL.md`
- `ARCHITECTURE.md`
- `GALGE.md`
- `prompt/*.md`
- `scripts/*.sh`
- `templates/session/**`
- `tests/pi_player/**`

今回の監査は原則レビューのみであり、要件監査のための `REQUIREMENTS_AUDIT.md` 追加以外の実装変更は行わない。

## Classification Legend

- `KEEP`: LIRIA v1 にそのまま必要
- `ADAPT`: 仕組みは使うが LIRIA v1 向けの調整が必要
- `DEFER`: 将来拡張に回す
- `REMOVE`: LIRIA v1 では不要、または旧 inner-galge 由来として外す
- `REVIEW`: 価値はあるが、まだ判断材料が足りない

## Executive Summary

監査結果の要点:

1. 新規開始Q&A、GM仕様、知識境界、保存分配、session 分離、PI Player テスト基盤は LIRIA v1 の中核として残すべき状態に近い。
2. `save / resume` と `initial_answers.md` の設計は、旧 inner-galge より明確に改善されている。ここは `KEEP` が多い。
3. `romance.md`、`runtime.md`、`combat.md` には、旧 inner-galge / 冒険RPG 由来の「ハーレム自由モード」「G 通貨」「拠点投資」「装備スロット」「重い HP 管理」が残っており、LIRIA v1 向けの `ADAPT` が必要。
4. `villain_engine.md` は「事件 / 外圧」エンジンとして使えるが、勢力類型や上位脅威の扱いは v1 の現代寄り運用に寄せ直す必要がある。
5. 生ログ保存、integrity check、PI Player テストは有効だが、「ログを漫画脚本化する」までの正式要件は未定義であり、現状は `DEFER` が妥当。

---

## Functional Requirements

### 新規開始Q&A
- Classification: KEEP
- Priority: High
- Current: `prompt/core_newgame.md` で Q0-Q6、内部生成、`design/initial_answers.md` と `current/*.md` への保存分配まで定義済み。
- LIRIA v1での扱い: 新規プレイ初期化の正本として維持する。
- Risk: 後続 prompt が旧要件に引っ張られると、Q&A だけ v1 でも実プレイが旧仕様へ戻る。
- Next Action: `core_newgame.md` を起点に、恋愛・生活・事件・インナー以外の初期化要素を増やしすぎない運用を固定する。

### AI GM進行
- Classification: KEEP
- Priority: High
- Current: `prompt/core.md` と `prompt/gm_policy.md` により、AI GM が状況運用者として振る舞う前提が明文化されている。
- LIRIA v1での扱い: 中核機能として維持する。
- Risk: `runtime.md` や `romance.md` の旧設計が強いと、GM が状況運用者ではなく攻略ゲームの管理者へ寄る。
- Next Action: GM の仕事を `恋愛・生活・事件の運用` に限定するレビュー観点を今後も維持する。

### 自由入力
- Classification: KEEP
- Priority: High
- Current: `core.md` と `gm_policy.md` で、プレイヤー自由入力を物語入力の中心として扱っている。
- LIRIA v1での扱い: TRPG 型の根幹として維持する。
- Risk: save/resume や相談モードが増えるほど、自由入力の意味論が曖昧になる。
- Next Action: 自由入力の種別を `通常入力 / 内心 / gm相談 / 誘導` に分ける現行整理を維持する。

### gm相談モード
- Classification: KEEP
- Priority: High
- Current: `gm_policy.md` で `gm` / `(gm` プレフィックスがメタ相談モードとして定義され、`core.md` にも入力例がある。
- LIRIA v1での扱い: 詰まり防止の実用機能として維持する。
- Risk: 物語本文とメタ解説が混ざると immersion を壊す。
- Next Action: テスト観点に「物語停止」「メタだけ返す」を残し、PI Player smoke で回帰確認する。

### 内心入力
- Classification: KEEP
- Priority: High
- Current: `gm_policy.md` の `Input Semantics` と `Thought and GM Input Boundary` で `( ... )` を主人公の内心として扱うルールが定義されている。
- LIRIA v1での扱い: インナー可視化のための重要機能として維持する。
- Risk: NPC が内心を当然のように知ると、知識境界と人格一貫性が同時に崩れる。
- Next Action: 内心は行動宣言ではないことを継続的にレビューし、必要時だけ能力持ちキャラに限定して拾わせる。

### Anti-Leading
- Classification: KEEP
- Priority: High
- Current: `gm_policy.md` に `Narrative Integrity / Anti-Leading` があり、プレイヤーの願望や断定を事実化しない方針がある。
- LIRIA v1での扱い: 自律的な恋愛シミュレーションを守る中核ルールとして維持する。
- Risk: このルールが弱いと、LIRIA は「言ったもの勝ち」の攻略ゲームに戻る。
- Next Action: PI Player と人間レビューの双方で、軽い誘導入力への返答を定期確認する。

### Knowledge Boundary
- Classification: KEEP
- Priority: High
- Current: `gm_policy.md` の `Character Knowledge Boundary`、`Known / Suspected / Unknown`、`Thought and GM Input Boundary` により定義済み。
- LIRIA v1での扱い: 会話事故防止の必須要件として維持する。
- Risk: save/resume で current 側の知識スコープ更新が漏れると、再開時に破綻する。
- Next Action: `current/gm.md` と `current/harem.md` に知識境界メモを残す現行設計を維持し、`INTEGRITY_CHECK.md` の確認項目を活かす。

### ヒロイン生成
- Classification: ADAPT
- Priority: High
- Current: `core_newgame.md` では Q3 を全体のヒロイン生成バイアスとして扱っているが、`romance.md` には旧ハーレム前提の生成文脈が残る。
- LIRIA v1での扱い: 維持するが、「攻略対象の束」ではなく「自律した人物群」の生成へ寄せる必要がある。
- Risk: `romance.md` の旧前提が強いと、Q3 の好みが「量産型ハーレム選定」へ崩れる。
- Next Action: `romance.md` の生成導線から `旅先 / ハーレム攻略 / 主人公補助役` 寄りの文言を棚卸しし、現代生活圏ベースへ調整する。

### bond / AFFINITY
- Classification: ADAPT
- Priority: High
- Current: `runtime.md` と `romance.md` で広く使われている。bond は全 NPC、AFFINITY は恋愛深度として運用される。
- LIRIA v1での扱い: 仕組みは有用なので残すが、数値設計と言葉遣いは見直しが必要。
- Risk: `AFFINITY 5 = ハーレムの一員として定着` のような旧表現が、現在のコンセプトと正面衝突する。
- Next Action: AFFINITY の語彙を `攻略 / 陥落 / ハーレム定着` から、`関係変化 / 合意 / 深化` に置き換える要件整理を次フェーズで行う。

### 深化ベクトル
- Classification: ADAPT
- Priority: Medium
- Current: `romance.md` と `save_resume.md` に `hidden 深化ベクトル` があり、AFFINITY 5 以降の関係変化を扱う。
- LIRIA v1での扱い: 概念としては有効だが、旧ハーレム終盤運用の残り香を削る必要がある。
- Risk: 深化ベクトルが「特定の到達後のご褒美管理」に見えると、LIRIA v1 の関係変化の連続性を壊す。
- Next Action: 深化ベクトルを「複数関係の生活・信頼・摩耗管理」として再定義するレビュータスクを立てる。

### ヒロイン間関係
- Classification: ADAPT
- Priority: Medium
- Current: `runtime.md`、`save_resume.md`、`current/harem.md` で active なヒロイン間ベクトルを扱う前提がある。
- LIRIA v1での扱い: 維持するが、`ハーレム管理コスト` よりも `共同体 / 嫉妬 / 共有境界 / 利害調整` に寄せる。
- Risk: 現行の REQUIREMENTS 由来の「ハーレム管理システム」が前面に出ると旧ゲーム性へ戻る。
- Next Action: ヒロイン間関係を `共同生活 / 知識共有 / 利害衝突` の観点で書き直す候補として整理する。

### 事件/外圧
- Classification: ADAPT
- Priority: High
- Current: `core_newgame.md` の Q5、`gm_policy.md`、`runtime.md`、`villain_engine.md` で強く支えられている。
- LIRIA v1での扱い: 必須機能として残すが、v1 では現代的な入口を優先し、異形・裏世界は匂わせに留める。
- Risk: `villain_engine.md` の勢力論理が強すぎると、日常より陰謀が主役になりやすい。
- Next Action: `villain_engine.md` を「事件 / 外圧エンジン」として使い、v1 では導入条件を保守的にする方針を明文化する。

### 戦闘/危機処理
- Classification: ADAPT
- Priority: High
- Current: `combat.md` は詳細で強い。`HP`、部位別コンディション、敵設計、直接圧処理まで厚く定義されている。
- LIRIA v1での扱い: 戦闘専用ではなく `危機処理` として縮約して残す。
- Risk: 現状の厚さだと、恋愛・生活より危機シミュレータとしての比重が高くなる。
- Next Action: v1 では `combat.md` の適用範囲を「危機で何を払ったかを返す」へ絞り、戦術詳細を簡略モードへ落とす要件を検討する。

### HP/状態
- Classification: ADAPT
- Priority: High
- Current: `combat.md` で HP 帯、コンディション、回復、非戦闘消耗まで細かく定義されている。`save_resume.md` でも現在HP保存が必須。
- LIRIA v1での扱い: 維持するが、細密戦闘管理ではなく `危機 / 消耗 / 無理の可視化` に絞る。
- Risk: 数値と帯管理が前面に出ると、生活・恋愛より RPG 的リソース管理に見える。
- Next Action: `HP/状態` は `簡略ルールだが省略はしない` という要件に再整理し、帯の簡素化候補を別タスク化する。

### お金/生活/事業
- Classification: ADAPT
- Priority: High
- Current: `core_newgame.md` では生活ランク / 事業状態の簡略運用を推す一方、`runtime.md` には `500G` や拠点投資、施設収入など経営ゲーム寄り要素が残る。
- LIRIA v1での扱い: 生活基盤を動かす要素として残すが、数値経済シミュレーションは弱める。
- Risk: 現状のままだと現代生活物ではなく、RPG 商売システムへ回帰する。
- Next Action: v1 の金銭要件を `生活ランク / 余裕 / 事業状態 / 今回の支払い圧` に限定する見直し案を作る。

### 装備/道具
- Classification: ADAPT
- Priority: High
- Current: `romance.md` に武器 / 防具 / アクセサリーの 3 枠装備とプレゼントによる AFFINITY 上昇が残っている。
- LIRIA v1での扱い: `装備` ではなく `道具 / 仕事道具 / 証拠 / 生活アイテム / 危機対応ギア` として簡略化する。
- Risk: 3 枠装備や数値ボーナスは旧 RPG 色が強く、恋愛・生活・事件の主軸を食う。
- Next Action: 装備スロット制を v1 から外し、持ち物タグや状況道具へ落とす要件検討を行う。

### セーブ/再開
- Classification: KEEP
- Priority: High
- Current: `save_resume.md`、`ARCHITECTURE.md`、`MEMORY_MODEL.md`、`scripts/check_session_integrity.sh` が揃っている。
- LIRIA v1での扱い: 必須機能として維持する。
- Risk: legacy fallback の説明がまだ多く、main path と読み分けを誤る余地がある。
- Next Action: v1 公開時は `legacy fallback は旧卓専用` とする注意を継続し、新規運用では `current/*`, `cast/*`, `design/*` に限定する。

### initial_answers.md
- Classification: KEEP
- Priority: High
- Current: `templates/session/design/initial_answers.md`、`core_newgame.md`、`save_resume.md` で正本扱いが定義済み。
- LIRIA v1での扱い: 初期条件の正本として維持する。
- Risk: current と混ざると、プレイ中の変化と初期条件が追えなくなる。
- Next Action: save/resume と integrity check の両方で `initial_answers.md` を上書きしないルールを維持する。

### current/*.md
- Classification: KEEP
- Priority: High
- Current: `current/player.md`、`current/gm.md`、`current/harem.md` が現在状態の正本として整理されている。
- LIRIA v1での扱い: そのまま維持する。
- Risk: 項目が増えすぎると current 層が肥大化し、hotset や archive の役割を侵食する。
- Next Action: current は `今効いている情報` のみに保ち、長文履歴は archive へ送る原則を維持する。

### hotset
- Classification: KEEP
- Priority: High
- Current: `core_newgame.md`、`save_resume.md`、`INTEGRITY_CHECK.md` で再開用の短い要約キャッシュとして定義されている。
- LIRIA v1での扱い: 維持する。
- Risk: 攻略メモ化、Q&A 全文の複写、複数アンカー混在が起きると再開品質が落ちる。
- Next Action: `hotset` を `今動いている圧 / 未確定情報 / 見えている入口 / 放置で変わること` に絞る原則を維持する。

### 生ログ保存
- Classification: KEEP
- Priority: Medium
- Current: `scripts/save_rawlog.sh`、`save_resume.md`、`README.md`、`pre_compress_check.sh` に生ログ保存の流れがある。
- LIRIA v1での扱い: current 保存の補助として維持する。
- Risk: 生ログが current の代替と誤認されると、セーブ構造が再び崩れる。
- Next Action: `raw log は archive/logs の追加資産` という位置づけを維持し、current 正本との混同を避ける。

### compress前チェック
- Classification: ADAPT
- Priority: Medium
- Current: `scripts/pre_compress_check.sh` は active session 前提で `現在HP`、`AFFINITY`、`再開アンカー`、生ログの有無などを見ている。
- LIRIA v1での扱い: 必要だが、fresh session と長期運用 session の違いを踏まえた運用に調整が必要。
- Risk: 新規 scaffold 直後には未充足で落ちやすく、`壊れている` と誤認される。
- Next Action: `pre_compress` は「圧縮前の運用チェック」であることを README か script コメントでさらに明確化する。

### PI Playerテスト
- Classification: KEEP
- Priority: Medium
- Current: `prompt/pi_player.md`、`tests/pi_player/README.md`、`tests/pi_player/smoke_test.md` が追加済み。
- LIRIA v1での扱い: 人間プレイの代替ではない smoke / regression テストとして維持する。
- Risk: PI Player を標準プレイヤー像と誤認すると、プレイ体験の設計がテスト向けに引っ張られる。
- Next Action: `PI Player は回帰検証専用` の位置づけを README と tests 側で保ち続ける。

### ログ→漫画脚本化候補
- Classification: DEFER
- Priority: Medium
- Current: 生ログ保存と archive はあるが、`漫画脚本化` そのものの正式要件や匿名化・編集基準は未定義。
- LIRIA v1での扱い: 将来の資産化候補として価値はあるが、まだ仕様化は早い。
- Risk: 公開前提の整理なしにログを資産化すると、秘匿性・権利・編集粒度で事故る。
- Next Action: これはプロダクト機能か、制作ワークフローかを先に決める。機能化するなら抽出ルールと匿名化ルールを別途定義する。

---

## Non-Functional Requirements

### 長期継続性
- Classification: KEEP
- Priority: High
- Current: `MEMORY_MODEL.md`、`ARCHITECTURE.md`、`VALIDATION.md` に長編前提の分離と確認観点がある。
- LIRIA v1での扱い: 重要な非機能要件として維持する。
- Risk: current / cast / archive の責務が崩れると、長編で破綻する。
- Next Action: archive 逃がし、hotset 再生成、current 圧縮の方針を継続する。

### キャラ人格の一貫性
- Classification: KEEP
- Priority: High
- Current: `VALIDATION.md`、`MEMORY_MODEL.md`、`save_resume.md` で tone / Layer / fixed memory / 呼称整合を確認する仕組みがある。
- LIRIA v1での扱い: そのまま維持する。
- Risk: `current` の短メモだけで再登場キャラを回すと声が崩れる。
- Next Action: 再登場キャラや route key NPC を cast file 管理へ上げるルールを維持する。

### 知識境界
- Classification: KEEP
- Priority: High
- Current: `gm_policy.md`、`INTEGRITY_CHECK.md`、`VALIDATION.md` に監査観点まで揃っている。
- LIRIA v1での扱い: 必須。
- Risk: 知識境界は一度崩れると修復コストが高い。
- Next Action: `Known / Suspected / Unknown` の更新を save 処理観点として維持する。

### 誘導耐性
- Classification: KEEP
- Priority: High
- Current: `gm_policy.md` と PI Player テストで明示的に確認できる。
- LIRIA v1での扱い: 必須。
- Risk: 恋愛シミュレーションほどプレイヤーの希望入力が強くなるため、崩れやすい。
- Next Action: 軽い誘導入力を smoke test の定番ケースに残す。

### 旧セッション混入防止
- Classification: KEEP
- Priority: High
- Current: `.gitignore`、`check_session_integrity.sh`、`MEMORY_MODEL.md`、`ARCHITECTURE.md` が session 分離を前提にしている。
- LIRIA v1での扱い: GitHub 公開上の必須要件として維持する。
- Risk: legacy fallback の存在自体は必要だが、main path と混ざると事故る。
- Next Action: `legacy read-only fallback` の扱いを旧卓専用として保ち、新規公開用途では参照頻度を下げる。

### prompt肥大化防止
- Classification: ADAPT
- Priority: High
- Current: prompt は分割されたが、`runtime.md`、`romance.md`、`combat.md` は依然として大きく、継承された旧要件も多い。
- LIRIA v1での扱い: 必要だが、現状は十分ではない。
- Risk: prompt が太いままだと、API 化時のコスト・理解負荷・矛盾混入が増える。
- Next Action: 次フェーズで `romance / runtime / combat` の軽量化候補を抽出し、v1 必須仕様だけに絞る。

### hotset肥大化防止
- Classification: KEEP
- Priority: High
- Current: `save_resume.md`、`INTEGRITY_CHECK.md`、`VALIDATION.md` で強く抑制されている。
- LIRIA v1での扱い: そのまま維持する。
- Risk: hotset を便利メモとして足し続けると、再開キャッシュではなく第2の gm.md になる。
- Next Action: 監査観点として `複数アンカー禁止` と `攻略メモ化禁止` を継続する。

### GitHub公開時の秘匿性
- Classification: KEEP
- Priority: High
- Current: `.gitignore` で `saves/*`、`archive/logs/*`、`rawlogs/` を除外している。
- LIRIA v1での扱い: 維持する。
- Risk: 生ログや実 session を commit すると、個人プレイ資産が公開物へ混入する。
- Next Action: PI Player や smoke test でも実 session を commit しない運用を継続する。

### API化時のコスト制御
- Classification: REVIEW
- Priority: Medium
- Current: `--prompt-only` など launcher 側の改善はあるが、prompt そのものはまだ重い。明確な token budget 要件はない。
- LIRIA v1での扱い: 重要だが、まだ設計判断が十分ではない。
- Risk: prompt 肥大化と archive 参照量の増大で、API コストが読めなくなる。
- Next Action: API 化を本格化する前に、`minimum prompt set` と `resume read budget` を定義する。

### セッション分離
- Classification: KEEP
- Priority: High
- Current: `ARCHITECTURE.md`、`MEMORY_MODEL.md`、`create_session.sh`、`check_session_integrity.sh` で self-contained session が成立している。
- LIRIA v1での扱い: 維持する。
- Risk: 同名キャラや旧 session mirror を live path として扱うと崩れる。
- Next Action: `session-scoped only` の原則を継続し、legacy は fallback のままに留める。

### テスト容易性
- Classification: KEEP
- Priority: Medium
- Current: `PI Player`、`--prompt-only`、integrity check、smoke test 手順がある。
- LIRIA v1での扱い: 維持する。
- Risk: bash 実行や Windows sandbox の事情で自動化しにくい場面が残る。
- Next Action: 将来的に `prompt-only` ベースの半自動 smoke 実行をもう一段スクリプト化する。

### ログ資産化
- Classification: ADAPT
- Priority: Medium
- Current: 生ログ保存、archive、軽量観測メモはあるが、再利用粒度は未整理。
- LIRIA v1での扱い: 残すが、`保存` と `再利用` を分けて考える必要がある。
- Risk: raw log をそのまま資産扱いすると、長すぎる・秘匿混入・編集不能になりやすい。
- Next Action: `raw log / chapter summary / public-facing excerpt` の3層に分ける案を別途検討する。

### 成人向け表現の分離/制御
- Classification: ADAPT
- Priority: High
- Current: 概念文書では抑制方針が入っているが、`romance.md` には `身体的関係の開始`、旧ハーレム終盤運用、成人寄りの深化語彙が残る。
- LIRIA v1での扱い: adult を増やさず、必要なら関係変化の一部として制御された扱いに留める。
- Risk: 旧 inner-galge の語彙が残ると、公開用スターターキットとしての輪郭を崩す。
- Next Action: `romance.md` と関連 style から、v1 と噛み合わない成人寄り・ハーレム攻略寄り語彙を別監査タスクとして切り出す。

## Legacy Sub-Requirements Marked REMOVE

以下は、列挙した主要要件とは別に、旧 inner-galge 由来のサブ要件として明確に外す対象である。

### 旧ハーレム攻略主目的
- Classification: REMOVE
- Priority: High
- Current: `REQUIREMENTS.md` と `romance.md` に、AFFINITY 5 やハーレム管理を中心に据える残滓がある。
- LIRIA v1での扱い: 削除する。恋愛は主軸だが、目的を「女を堕とす」「ハーレムを築く」に置かない。
- Risk: この前提が残ると、LIRIA の正本定義そのものが崩れる。
- Next Action: `romance.md` と `REQUIREMENTS.md` の旧語彙を明示的に整理する。

### RPG経営サブシステムの標準化
- Classification: REMOVE
- Priority: High
- Current: `runtime.md` に `500G`、投資施設、定期収入などの強い経営ゲーム要素が残る。
- LIRIA v1での扱い: 標準要件から外す。必要でも個別卓の拡張に留める。
- Risk: 生活基盤が経営ミニゲームに置き換わる。
- Next Action: v1 本体では `生活ランク / 余裕 / 仕事状態` に縮約する。

### 3枠装備と装備プレゼント恋愛トリガー
- Classification: REMOVE
- Priority: Medium
- Current: `romance.md` に武器 / 防具 / アクセサリーの 3 枠設計と、プレゼントによる AFFINITY 上昇が残る。
- LIRIA v1での扱い: 標準要件から外す。必要なら道具タグやイベント演出に置き換える。
- Risk: 恋愛が装備スロットと数値上昇の副産物に見える。
- Next Action: 装備を `道具 / 証拠 / 仕事ギア / 生活アイテム` に再整理する。

---

## High-Priority Review Targets

次の項目は、LIRIA v1 に合わせるための優先度が特に高い。

1. `prompt/romance.md`
   - `AFFINITY 5 = ハーレムの一員`
   - `深化タグ` の旧終盤運用
   - 装備プレゼントや身体関係開始を前提にした文脈
2. `prompt/runtime.md`
   - `500G`、拠点投資、施設収入など、現代生活寄りではなく RPG 経営寄りの要素
3. `prompt/combat.md`
   - 危機処理としては使えるが、v1 の軽さに対してやや重い
4. `prompt/villain_engine.md`
   - 事件 / 外圧エンジンとして有用
   - ただし勢力設計を強く出しすぎると v1 の匂わせ範囲を超える
5. `prompt/save_resume.md` と `scripts/pre_compress_check.sh`
   - `initial_answers.md` と current 分離には概ね整合
   - ただし fresh session と active session のチェック粒度の違いは明文化余地あり

## Suggested Next Actions

### Phase 1: 文書整合の修正
- `REQUIREMENTS.md` の旧 inner-galge 直系の章を、LIRIA v1 向けの監査結果に沿って書き換える
- 特に `ハーレム管理システム`、`装備 / 投資 / G 通貨`、`AFFINITY 5` 文脈を見直す

### Phase 2: prompt 軽量化
- `romance.md` から v1 とズレる攻略 / ハーレム終盤 / 成人寄り記述を整理する
- `runtime.md` から RPG 経営 / 世界旅要素を整理する
- `combat.md` を `危機処理コア` と `重戦闘拡張` に分けるか検討する

### Phase 3: ログ資産化の方針決定
- `archive/logs` を何に再利用するかを決める
- `漫画脚本化候補` を本当に機能要件化するか、制作ワークフローに留めるか判断する

## Final Judgment

LIRIA v1 は、起動・新規開始・保存分配・GM仕様・知識境界・session 分離という基盤ではすでに成立しつつある。

一方で、恋愛深化、装備、資金、拠点投資、ハーレム終盤運用、勢力エンジンの一部には旧 inner-galge / 冒険RPG 由来の重さが残っている。

したがって、LIRIA v1 の次の整理対象は:

- `romance` の再定義
- `money / equipment / HP` の軽量化
- `villain_engine` の v1 運用範囲の明確化
- `REQUIREMENTS.md` 自体の再整備

である。
