# TODO

## 目的

このリポジトリを、単一巨大プロンプト依存の卓から、
**長編でも壊れにくい GM システム**へ段階移行する。

狙いは3つ。

1. 再開時に必要な情報だけを軽く読めること
2. キャラの口調・関係・記憶が巻き戻らないこと
3. 敵・ヒロイン・脅威が同じアーキテクチャ上で連動すること

関連文書:
- `ARCHITECTURE.md` — 構成図と source of truth
- `GALGE.md` — 実行正本
- `README.md` — 起動方法とディレクトリ案内

## Current Phase: 本命プレイ前の整合

直近の実装で、LIRIA v1 は「数値バトル中心」ではなく、
**危機処理、組織圧、能力制約、装備、外見保存、漫画化導線、長期記憶検証** を同じ運用面に載せる段階まで進んだ。

最近完了:

- combat を、倒す/倒されるではなく、逃げる、守る、交渉、隠す、耐える、助けを呼ぶ、能力使用、代償、余波で扱う危機処理へ更新
- villain / organization を、Organization Doctrine、contact surface、weak joint で運用する方針へ更新
- Ability Constraint Profile により、能力の限界、できないこと、代償、痕跡を保存対象化
- Equipment / Tools により、装備と道具を万能解決ではなく準備・携行・破損・場面制約つきで扱う方針へ更新
- Appearance Profile と Visual Character Sheet により、外見、服装、表情、持ち物、三面図/PVの土台を保存対象化
- memory / manga export を、Manga Export Candidates と Natural Language Manga Export の自然文導線へ接続
- Anti-Meta Dialogue により、メタ説明をキャラの口調と世界内の受け流しへ寄せた
- PI Player smoke / pre_compress の接続を、本命プレイ前の最低限の破綻検知として更新

次の現実的な残件:

- `Story Reference Layer + Organization Cast Pre-Generation + Minimal Story Spine` を実プレイで検証する。狙いは、漫画/作品の構造ストックを抽象化して使い、組織の理念はあるのに主要人物が抽象メモだけで出てしまう事故を防ぐこと
- 実 smoke を回し、new -> 1 turn -> save -> resume -> pre_compress で session-scoped path と保存項目が欠けないか確認する
- 本命新規プレイを開始し、初期状態、危機処理、組織圧、ヒロイン反応、漫画化導線が自然に出るか見る
- 長編運用で、Ability Constraint Profile、Equipment / Tools、Appearance Profile、Organization Doctrine がログ置き場化しないよう保持量を調整する
- Manga Export Candidates が多すぎる/薄すぎる場合の抽出基準をチューニングする
- `prompt/style_bridge.md` を切るか、adult/Style Layer は現状維持にするか判断する

## 現在地

この TODO は、複数 session 対応と source-of-truth 整理を前提に更新済み。
上の Current Phase が最新の読み始め地点で、下のロードマップは履歴と残件確認用。

完了した方針:

- 標準 layout は `saves/<session_name>/current`, `cast`, `design`, `indexes`, `archive`
- cast は `saves/<session_name>/cast/heroine` と `saves/<session_name>/cast/npc` に置く
- `hotset.md` は derived cache であり、正本ではない
- session 直下 mirror は main path から外し、legacy read-only fallback として扱う
- 既存の個人プレイ資産は repo 外の legacy asset として扱い、新規 session の固定値にしない
- validation に multi-session regression を追加
- integrity check を session-scoped layout 前提に更新

今回のリファクタで完了した実装:

- launcher / prompt の session 名動的化
- `templates/session/` と `scripts/create_session.sh` による session scaffold 生成
- live cast の `saves/<session_name>/cast/` への移行
- session 直下 mirror の削除と read-only fallback 化
- 既存プレイ資産の current anchor 正規化
- `CORE.md` の live state 除去
- `.DS_Store` / `._*` の削除と `.gitignore` 追加

## ステータス早見表

| 項目 | 状態 | 補足 |
|---|---|---|
| Phase 0: Source of Truth 方針 | 完了 | `current/*`, `cast/*`, `design/*` を正本として固定 |
| Phase 1: Prompt Layer 分割 | 完了 | 分割 prompt を session-scoped path 前提へ更新 |
| Phase 2: Multi-session Save Layout | 完了 | 新規 session scaffold と self-contained layout を導入 |
| Phase 3: Hotset / Resume | 完了 | hotset を単一 cache として正規化 |
| Phase 4: Memory Model / Compression | 完了 | cast 保存先を session-scoped に変更 |
| Phase 5: Integrity Check | 完了 | lightweight check script を追加し、main path から mirror を外した |
| Phase 6: Legacy Migration | 完了（archive backfill は任意） | 既存資産を新 layout へ移し、legacy mirror は削除 |
| Phase 7: Validation | 完了 | new -> save -> resume と cross-session isolation を追加 |

## 実装ロードマップ

### Phase 0: Source Of Truth 方針
**優先度: 最優先**  
**状態: 完了**

完了:

- `ARCHITECTURE.md` に session-scoped source of truth 表を反映
- `current/player.md` `current/gm.md` `current/harem.md` の責務を固定
- `cast/heroine` `cast/npc` を session 配下へ固定
- `design/villain_design.md` を session 配下の設計資料の正本に固定
- legacy mirror を read-only fallback へ格下げ

残件:

- なし

### Phase 1: Prompt Layer 分割
**優先度: 高**  
**状態: 完了**

完了:

- `docs/legacy/PROMPT_SPLIT_PLAN.md` を追加
- `prompt/core.md` `prompt/runtime.md` `prompt/combat.md` を追加
- `prompt/save_resume.md` `prompt/villain_engine.md` `prompt/romance.md` を追加
- ランチャーが分割 prompt を読む構造を導入

残件:

- `prompt/style_bridge.md` を切るか、style は現状維持にするか判断

### Phase 2: Multi-session Save Layout
**優先度: 高**  
**状態: 完了**

目的:

- current state と長期履歴を分離する
- session 間の save / cast 汚染をなくす

完了:

- docs の標準構成を `saves/<session_name>/current`, `cast`, `design`, `indexes`, `archive` に統一
- `README.md` の `.gitignore` 誤記と固定 session 説明を更新
- session 直下 mirror を main path から外した

残件:

- archive 本文のバックフィル（任意。index と current で運用可能）

完了条件:

- 新規 session が self-contained に作成される
- 通常保存が mirror を作らない
- repo ルート cast が live data として使われない

### Phase 3: Hotset / Resume Algorithm
**優先度: 最優先**  
**状態: 完了**

完了:

- hotset を正本ではなく derived cache と明記
- hotset は append ではなく上書き再生成する方針に変更
- validation に複数アンカー混在検知を追加

残件:

- 実プレイで再開1シーン目が hotset 主導になるか確認

### Phase 4: Memory Model / Compression Rule
**優先度: 高**  
**状態: 完了**

完了:

- `docs/architecture/MEMORY_MODEL.md` を session-scoped cast 前提へ更新
- 記憶を `core fixed / historical fixed / echo / volatile` に分類
- legacy import の扱いを read-only に固定

残件:

- 保持上限の実数値を決める
- archive 再昇格の運用例を増やす

### Phase 5: Integrity Check
**優先度: 高**  
**状態: 完了**

完了:

- `docs/validation/INTEGRITY_CHECK.md` を mirror 前提から session-scoped layout 前提へ更新
- legacy fallback を別節へ隔離
- `scripts/check_session_integrity.sh` を追加

残件:

- CI 化するかは後続判断

### Phase 6: Legacy Migration
**優先度: 中**  
**状態: 完了（archive backfill は任意）**

目的:

- 既存プレイ資産を壊さずに新 layout へ移す

残件:

- archive 本文バックフィル（必要になった時だけ実施）

完了条件:

- 既存プレイ資産が new layout で自然に保存・再開できる
- legacy fallback が main path に混ざらない

### Phase 7: Validation
**優先度: 中**  
**状態: 完了**

完了:

- `docs/validation/VALIDATION.md` に multi-session lifecycle を追加
- cross-session isolation を追加
- 長編・cast voice・archive 観点を session-scoped path に更新

残件:

- 実プレイで回帰観点を実測する
- 失敗時の修正フローを追加する

## プレイ体験改善ライン

アーキテクチャ改善とは別に、
**この卓をもっと面白くするための運用改善** を切り出す。

### 改善A: 事件の後遺症テンプレ
**優先度: 高**  
**状態: ルール追加済み・テンプレ不足**

完了:
- `GALGE.md` に後遺症ルールを追加
- `current/gm.md` に `直近の後遺症` 欄を追加
- `hotset.md` に再開時に返す後遺症を追加

残件:
- 各勢力ごとの後遺症テンプレを 3 本以上ずつ作る
- `信用 / 仕事 / 居場所 / 呼び方 / 約束 / 噂 / 顧客 / 傷` の分類運用を具体化する

### 改善B: 余韻シーン固定
**優先度: 高**  
**状態: ルール追加済み・個別テンプレ不足**

完了:
- `GALGE.md` に事件後の余韻シーン固定ルールを追加

残件:
- 主要ヒロインごとに余韻シーンの型を 2 本以上ずつ作る
- `看病 / 帰り道 / 朝の会話 / 夜の弱音` の型を整理する

### 改善C: 幹部 -> ボス の段階登場
**優先度: 高**  
**状態: ルール追加済み・下っ端層不足**

完了:
- `予兆 -> 下っ端 -> 幹部 -> ボス` の顕在化段階を追加
- 勢力ごとのボス、幹部、規模、初登場、やらかしを設計済み

残件:
- 各勢力の「下っ端の顔」を 1-2 人ずつ作る
- 幹部が残す余波テンプレを作る
- 同じ章でボスを連打しない運用例を追加する

### 改善D: 選択コストの見える化
**優先度: 高**  
**状態: ルール追加済み・実データ運用強化待ち**

完了:
- `GALGE.md` に選択コストの可視化ルールを追加
- 3本フックに `放置時の悪化` と `解決後に残るもの` を追加

残件:
- 既存プレイ資産の主要フックに、実際の悪化連動をもっと具体化する
- 1ターン選択で何が 1 段進むかを current 側で見えやすくする

### 改善E: 半分だけ正しい敵台詞
**優先度: 中**  
**状態: ルール追加済み・台詞集不足**

完了:
- `GALGE.md` に「敵に図星を言わせる」ルールを追加
- 各勢力の例文を少数追加

残件:
- 各勢力に図星台詞を 3 本以上ずつ作る
- 主人公と主要ヒロインそれぞれへの刺さり方を台詞化する

### 改善F: 下っ端の顔
**優先度: 中**  
**状態: 未着手**

やること:
- 各勢力に `よく出る下っ端` を 1-2 人作る
- 名前、口調、得意な嫌がらせ、逃げ方だけ固定する
- 倒しても別口で再登場できる位置づけにする

完了条件:
- 各勢力に反復登場できる雑魚顔がいる
- 「またこいつか」が作れる

### 改善G: 世界の自律性
**優先度: 最優先**  
**状態: 着手**

目的:
- ヒロインだけでなく、世界、敵、土地、期限も自律して動いて見えるようにする
- 「プレイヤーが触った時だけ開く箱」感を減らす

やること:
- `prompt/runtime.md` に「世界が待たない」ルールを追加
- `prompt/villain_engine.md` と runtime の間で、`ロマンス中に乱入しない` と `外側の進行は止まらない` を分離する
- 各フックに `放置で起きる事実変化` を current 側で持ちやすくする
- 襲撃以外の悪化テンプレ（証拠消し、対象移動、噂、締切短縮、先回り）を増やす

完了条件:
- プレイヤーが1本を選んだ時、別の1本で景色が変わる
- 脅威が「触るまで止まっている」ように見えない

### 改善H: 探索の段階化とご都合主義の抑制
**優先度: 最優先**  
**状態: 着手**

目的:
- 探索を「一回で全部わかる」構造から外す
- 能力が都合よく効いても、見え方に摩擦を残す

やること:
- 探索を `予兆 -> 手がかり -> 検証 -> 深部 -> 回収` の段階で運用する
- `下見` の上限を明文化する
- 能力でショートカットできる段数を制限する
- 能力が刺さった時の `ツッコミ / 部分成功 / 軽い代償` ルールを prompt 化する
- hotset を `手順書` ではなく `圧と未確定情報の抜粋` へ寄せる

完了条件:
- 一回の訪問で `手がかり / 意味 / 使い方 / 核心` を同時回収しない
- hotset が攻略メモではなく状況メモとして機能する

### 改善I: HP / ステータスの実戦化
**優先度: 高**  
**状態: 着手**

目的:
- HP やコンディションを「戦闘がある時だけ動く飾り」にしない
- 戦闘が少ない章でも、身体の余力や無理がプレイに効くようにする

やること:
- `prompt/combat.md` に非戦闘危険シーンでの HP 減少ルールを追加
- 追跡、逃走、侵入、環境突破、能力の無理押しでコンディションが動く運用を明文化する
- 7-9 の部分成功で `進めたが払った` を基本化する
- 低HP / 負傷が、その後の会話や移動でも描写に残るようにする

完了条件:
- 戦闘ゼロの章でも、HP / コンディション / 残回数の少なくとも1つが意味を持つ
- プレイヤーが休息や回復を選ぶ理由が自然に発生する

## 追加タスク

## 別軸構想: 人格OS / 仮想世界問答エンジン

この章は `LIRIA` 本編の改修ではなく、
**別プロジェクトとして切り出す前提の構想メモ**。

狙い:
- ギャルゲーの皮を外しても使える「人格運用エンジン」を抜き出す
- 相談、壁打ち、SNS、訓練、シミュレーションへ流用する
- 将来的には GitHub の買い切り販売、または companion AI 設計キット化する

前提:
- 本体は「恋愛」ではなく **関係の積み上がり**
- 本体は「戦闘」ではなく **人格・記憶・関係更新の構造**
- HP や能力残回数は用途次第で不要

### 構想1: ギャルゲーから抜き出すコア
**優先度: 高**
**状態: 発想確定・未整理**

残す:
- キャラの核
  - 価値観
  - 禁忌
  - 話し方
  - 変わらない性格
- 関係の進展
  - 信頼
  - 距離
  - 秘密共有
  - 役割変化
- 記憶の層
  - `core fixed`
  - `historical fixed`
  - `echo`
  - `volatile`
- 知識の非対称
  - 誰が何を知っているか
- 変化の速度制御
  - 1シーンで急に別人化しない

捨て候補:
- HP
- 戦闘
- 能力残回数
- ダンジョン的進行
- 勝敗前提のシーン処理

完了条件:
- 「人格エンジンとして最低限必要な要素」だけを別文書に切り出す
- 本編依存のフィールドと汎用フィールドを分離できる

### 構想1.5: 能力成長の軽量フレーム
**優先度: 高**
**状態: 発想確定・未整理**

目的:
- 能力を消さずに残しつつ、`修行したら何でも生える` ご都合主義を防ぐ
- ガチガチの数値ゲームにせず、物語の体温を残したまま成長範囲だけ固定する

基本方針:
- 能力は `核` `使い方` `例外解放` の3層で管理する
- `核` は変えない
- `使い方` は修行や実戦で伸びる
- `例外解放` は転機、重大な失敗、異物接触、人間関係の変化でしか開かない

最小フォーマット案:
- `core`
  - 能力の本質。例: 浸透 / 誘導 / 共鳴 / 記録 / 切断 / 読解
- `domains`
  - 何に効きやすいか。対人 / 対物 / 感知 / 広域 / 精密 など
- `cannot`
  - 何には効かないか。死者蘇生、完全洗脳、都合のいい情報生成など
- `cost`
  - 何を払うか。回数、疲労、痕跡、暴走、関係悪化など
- `trace`
  - 使うと何が残るか。観測痕、周囲の違和感、監視リスクなど
- `growth`
  - 今どこまで育っているか。出力 / 精度 / 持続 / 燃費 / 安定性
- `breakthrough`
  - 次の解放条件。修行ではなく、物語上の転機に紐づける

修行で伸びてよいもの:
- 成功率
- 安定性
- 射程
- 出力
- 燃費
- 再現性

修行で伸ばさないもの:
- 系統そのものの追加
- 世界法則を超える新効果
- 万能化
- 便利なだけの裏技

メモ:
- `能力がなくても成立するが、あると別の解き方が生まれる` を目標にする
- 人間関係の反応は能力で雑に突破しない
- ダイスや非戦闘判定を入れるなら、能力の成功率より `代償の重さ` `痕跡` `発見の深さ` に使う

完了条件:
- 各能力に `核` と `できないこと` が最低1つずつ定義される
- 修行で伸びる項目と、転機でしか開かない項目が分離される
- `能力なしでも回るシーン` と `能力があると気持ちいいシーン` を分けて設計できる

### 構想2: 関係システムへの拡張
**優先度: 高**
**状態: 発想確定・未整理**

目的:
- 好感度システムから、汎用の関係システムへ拡張する
- 女性ヒロイン以外でも、年季の入った相棒、フィクサー、古参、マスター等を扱えるようにする

候補パラメータ:
- 信頼
- 緊張
- 敬意
- 恐れ
- 利用価値
- 本音開示度
- 帰属感
- 依存
- 嫉妬
- 未消化感情

メモ:
- 恋愛は関係カテゴリの1つに落とす
- 主要キャラは女だけである必要はない
- 「誰に聞くか」で返答が変わる構造を強める

完了条件:
- 恋愛前提でない関係値モデルを定義する
- 非恋愛キャラのサンプルを最低3体作る

### 構想3: 仮想世界での問答を相談UIにする
**優先度: 高**
**状態: 発想確定・未整理**

目的:
- 通常の「相談箱AI」ではなく、文脈のある対話環境を作る
- 例: 散歩しながら相談、バーで相談、事務所で壁打ち、帰り道の会話

仮説:
- 人は「正解」だけでなく、「誰に・どこで・どの関係の中で言われたか」を求めている
- 相談は、情報処理よりも関係つきの応答の方が深く刺さる

用途候補:
- 人生相談
- 仕事の壁打ち
- SNS発信相談
- 創作相談
- 人間関係シミュレーション

完了条件:
- 仮想世界の問答が刺さる理由を設計言語で説明できる
- 最低1本、相談特化の world / scene テンプレを作る

### 構想4: Player AI / GM AI / Logger AI の三層化
**優先度: 中**
**状態: 叩き台あり**

目的:
- 自動プレイ、観戦ログ生成、人格検証を可能にする

役割:
- `GM AI`: 世界、秘密、NPC、圧を管理する
- `Player AI`: 欲望、癖、弱点を持って不完全に選ぶ
- `Logger AI`: 要約、記憶更新、破綻検知を行う

重要ルール:
- Player は hidden state を読まない
- GM は Player の内心を前提に譲らない
- Logger だけが両者差分を見てよい
- 3者の目的関数を分ける

用途:
- 開発用ログ量産
- SNS断片生成
- 商品デモ生成
- 人格ブレの検証

#### 次フェーズ: AI Player Harness
**優先度: 中**
**状態: 最小Harness着手**

目的:
- PI Player smoke と AI Persona Playtest の次段として、複数personaによる実プレイ風検証を安全に回す
- 人間プレイヤー1人では見切れない GM破綻、ヒロイン自律性、恋愛/生活/事件の絡み、能力の便利すぎ、Knowledge Boundary違反、漫画化候補を早めに検出する
- AIプレイヤーを最終的な面白さ判定者にせず、人間レビューのためのQA補助として扱う

やること:
- 複数personaを指定できる設定形式を作る（最小実装: `tests/ai_player_harness/sample.yaml`）
- personaごとに turn数を指定し、20〜100ターン程度の長めの実プレイ風 raw log を生成できるようにする（最小実装: config item の `turns`）
- 生成した raw log を `scripts/analyze_play_log.sh` に渡す標準導線を作る（最小実装: 下位 `run_ai_persona_playtest.py` の既存分析を利用）
- persona別 report を出し、慎重型、好奇心型、恋愛寄り、事件寄りなどの傾向差を見られるようにする（最小実装: `saves/_harness_reports/ai_player_harness_*.md`）
- persona拡充として `romance_first_player` を追加し、ヒロイン即落ち、好意確定、同意境界の破綻を検出しやすくする
- 将来的に `save/resume`、`pre_compress_check.sh`、`check_session_integrity.sh` との接続を検討する
- report には GM破綻、ヒロイン自律性、恋愛/生活/事件の絡み、能力/装備の便利すぎ、Knowledge Boundary違反、漫画化候補を含める
- 次に必要なpersona候補: `case_solver`、`reckless_player`、`completionist_player`

やらないこと:
- AIに save ファイルを直接編集させない
- 完全自律GM/Playerループをいきなり本格実装しない
- AIプレイヤーの評価を、本命プレイの面白さ判定として扱わない

完了条件:
- 3者構成のテンプレファイルを用意する
- 1本、自動実行サンプルのログを出す
- AI Player Harness の最小仕様として、複数persona、turn数指定、raw log生成、analyze連携、persona別reportの境界が決まっている

### 構想5: 買い切り商品化
**優先度: 高**
**状態: 発想確定・未着手**

目的:
- SaaS より先に、GitHub / zip の買い切り商品として売る

売るもの:
- 人格AI設計キット
- 長期記憶運用キット
- 仮想世界問答テンプレート
- 用途別パック
  - 伴走AI
  - SNS相棒
  - 創作相棒
  - 壁打ちAI

売り方の仮説:
- X に会話断片を流す
- 「シナリオ」ではなく「育つ人格の設計」を売る
- ネタバレ不能であることはむしろ利点

必要物:
- 商品README
- 導入手順
- 変更ポイント一覧
- サンプルキャラ
- ライセンス / 利用条件

体験価値メモ:
- この商品は「設定資料」ではなく **体験そのもの** を売る
- コア価値は以下
  - キャラとの対話で関係が育つ
  - プレイヤー自身も、どういう人間か少し見えてくる
  - 仮想世界で「生きている感じ」が出る
  - 楽しいだけでなく、気づきや学びがある
- 普通のAI相談との差分
  - 相談箱ではなく、文脈のある出来事として会話が進む
  - 「誰に・どこで・どの関係の中で言われたか」が価値になる
  - 正解だけでなく、関係つきの応答が返る

売り文句の方向性メモ:
- 「育つ人格と、積み上がる関係を遊ぶ」
- 「毎回違うのに、同じ人がそこにいる」
- 「相談ではなく、仮想世界での対話体験」
- 「遊びながら、自分のことも少し分かる」

完了条件:
- 1本、買い切り商品として成立する最低構成を作る
- X 用のデモ断片を10本用意する

### 構想6: 投資botではない companion の試作
**優先度: 中**
**状態: 試作あり**

メモ:
- 既存ヒロインを「投資家」に変形すると別人格化しやすい
- 専用人格の方が安全
- 役割は売買推奨ではなく `観測・警戒・記録`

試作:
- `prototypes/market_familiar.md`

方針:
- 何を買うかを決める存在ではなく、
  「なぜ今それを買いたいのか」「壊れた時にどうするか」を言語化させる存在にする

完了条件:
- 投資 / SNS / 相談の3系統で companion 試作を各1体ずつ作る

### Save Trigger の明文化
**優先度: 高**  
**状態: 完了**

目的:
- `セーブ` `保存` `今日はここまで` をモデル解釈任せにしない

完了:
- `GALGE.md` に save trigger の強制ルールを追加
- 保存不能な瞬間だけ最小解決後に保存する方針を追加

補足:
- これは小変更
- 将来の「本当の save engine 実装」とは別物

### Legacy Mirror Policy
**優先度: 中**  
**状態: 方針更新済み**

目的:
- session 直下 mirror を main path から外し、ズレが live resume に混ざるのを防ぐ

完了:
- 正本は `current/*` `cast/*` `design/*` `indexes/*` `archive/*` と固定
- session 直下ファイルは legacy read-only fallback と固定
- 新規 session と通常保存では mirror を作らない方針に更新

残件:
- 既存資産に残る mirror の削除または隔離

## 今すぐやる順番

1. 世界の自律性ルールの定着と実プレイ確認
2. 探索の段階化と hotset 非手順書化の定着
3. 既存プレイ資産の archive バックフィルの続き
4. 下っ端の顔と余波テンプレの追加
5. 勢力ごとの後遺症テンプレと余韻シーン型の量産
6. Validation 観点を実プレイで回す
7. `prompt/style_bridge.md` を切るか、現状維持にするか判断

## 完了済み

- source of truth の固定
- 既存プレイ資産の v2 互換レイアウト初期化
- `current/` 優先の resume ルール
- hotset の導入と再開1シーン目主導
- villain engine の接続
- 敵勢力、ボス、幹部、規模、初登場、やらかしの設計
- 参考資料 -> 抽象化 -> 再具体化の villain 運用
- ロマンス中に敵が乱入しないルール
- 事件後の後遺症ルール
- 余韻シーン固定ルール
- 選択コストの可視化
- 敵に図星を言わせるルール
- Save Trigger の明文化
- Integrity Check 手順書の追加
- Memory Model 文書化と prompt 反映
- Legacy Mirror Policy の read-only fallback 化
- 既存 cast の fixed memory 方針整理
- Prompt Layer 分割設計の作成
- `prompt/save_resume.md` `prompt/villain_engine.md` の runtime 接続
- `prompt/romance.md` の runtime 接続
- `prompt/core.md` `prompt/runtime.md` `prompt/combat.md` の切り出し
- Validation 観点の固定
