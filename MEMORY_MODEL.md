# MEMORY_MODEL

## 目的

キャラ記憶、現在運用情報、履歴ログを混ぜない。

この文書では次を固定する。

- 何を session-scoped cast に残すか
- 何を current 側へ残すか
- 何を archive へ送るか
- 複数 session 間で記憶を混ぜないための境界

## Session Boundary

cast と save は session ごとに閉じる。

- 標準 cast: `saves/<session_name>/cast/heroine/*.md`, `saves/<session_name>/cast/npc/*.md`
- 標準 current: `saves/<session_name>/current/*`
- 標準 archive: `saves/<session_name>/archive/*`

同じ scenario から作った別 session でも、キャラの関係、呼称、AFFINITY、固定記憶は共有しない。
repo ルートの cast ディレクトリが残っていても、それは legacy import 用であり live data ではない。

## 記憶の4分類

### 1. core fixed

意味:

- その人物の芯

例:

- 口調
- 価値観
- 禁忌
- 基本呼称
- 年齢ラベル
- Layer 構造

保存先:

- `saves/<session_name>/cast/heroine/*.md`
- `saves/<session_name>/cast/npc/*.md`

### 2. historical fixed

意味:

- 取り消せない転換点

例:

- 告白
- 初夜
- 同行宣言
- 呼称変化
- 能力転換
- 決定的な裏切り / 和解

保存先:

- `saves/<session_name>/cast/heroine/*.md`
- `saves/<session_name>/cast/npc/*.md`
- `saves/<session_name>/archive/*`

cast には「何が変わったか」だけを短く残す。本文や長い経緯は archive へ送る。

### 3. echo

意味:

- 直近の残り香。まだ固定事実にはなりきっていない感情や空気

例:

- 事件後の気まずさ
- 照れ
- 後遺症
- 小さな不信
- 敵が残した嫌な予感

保存先:

- `saves/<session_name>/current/gm.md`
- `saves/<session_name>/current/harem.md`
- `saves/<session_name>/current/hotset.md`

### 4. volatile

意味:

- 今すぐ必要だが、長期保存するほどではない運用情報

例:

- HP
- 残回数
- 進行中フック
- 今ターンの予定
- 直近の調査メモ
- 誰が何を知っているかの台帳

保存先:

- `saves/<session_name>/current/*`

## ファイルごとの責務

| ファイル | 主に持つもの |
|---|---|
| `current/player.md` | volatile + プレイヤー視点の現在状態 |
| `current/gm.md` | volatile + echo + 世界進行 + 知識スコープ台帳 |
| `current/harem.md` | echo + 関係運用 + hidden 深化ベクトル + hidden ヒロイン間ベクトル |
| `current/hotset.md` | 再開用の echo / volatile 抜粋。正本ではない |
| `cast/heroine/*.md` | core fixed + historical fixed |
| `cast/npc/*.md` | core fixed + historical fixed |
| `design/*` | 長期設計 |
| `archive/*` | historical fixed の本文と生ログ |

## LIRIA v1 追加情報の保存先

`Appearance Profile`、`Ability Constraint Profile`、生活・仕事・組織圧は、圧縮時に落ちると再開後の行動可能性と台詞境界が変わる。次の責務分担を守る。

| 情報 | 正本 | 圧縮時の扱い |
|---|---|---|
| `Appearance Profile` | `current/player.md` | 身長、体型、基本服装、髪型、顔つき、雰囲気、現在差分は残す |
| 主人公の `Visual Character Sheet` | `current/player.md` | 画像/漫画生成用の固定資料。model sheet status、front / side / back notes、image prompt anchor、negative prompt / avoid を残す |
| ヒロインの `Visual Character Sheet` | `cast/heroine/*.md` | ヒロインだけに持たせる。text-only / prompt-ready / image-generated の状態と、generated asset references を残す |
| `Ability Constraint Profile` | `current/player.md` | output scale、trigger condition、range / target、uses / cooldown、cost、trace、collateral、social risk、relationship risk、escalation rule は残す |
| `Ability Runtime` | `current/player.md` | 残回数、cooldown、直近の trace、巻き添え、現在の社会/関係リスクは volatile として残す |
| `Work Profile` | `current/player.md` | 仕事、収入、職場/取引先、職務リスクだけ残す。細かい経済シミュレーションへ広げない |
| `Life Base` | `current/player.md` | 生活ランク、拠点自然性、同居/通勤/日常動線、生活制約を残す |
| `Equipment / Tools` | `current/player.md` | 行動選択肢、リスク、痕跡、関係リスクとして残す。攻撃力/防御力スロットにしない |
| `Organization Doctrine Layer` | `design/villain_design.md` | 組織理念、目的、規模、主要人物、接触面、弱い継ぎ目、内部矛盾、外部レバレッジを長期設計として残す |
| `Organization current pressure` | `current/gm.md`, `current/hotset.md` | 今接触している面、今動く外圧、勢力クロックへ落ちた要素だけ抜粋する |
| `Heroine Crisis Role` | `current/harem.md` | frontline / support / civilian / wildcard と危機時の行動傾向を残す |
| `Anti-Meta Dialogue` | `current/gm.md` | NPC/ヒロインが GM、シナリオ、フラグ、イベント、好感度、判定を台詞に出さないための運用メモとして残す |
| `Knowledge Boundary / Anti-Leading` | `current/gm.md`, 補助で `current/harem.md` | known / suspected / unknown と、こちらから誘導してはいけない未発見情報を残す |

`current/hotset.md` は正本ではないが、再開1ターン目に影響する `Appearance Profile`、能力制約、仕事/生活、Equipment、Organization Doctrine、Heroine Crisis Role、Knowledge Boundary は短く抜粋してよい。
Visual Character Sheet は正本の `current/player.md` または `cast/heroine/*.md` から読む。hotset には必要時だけ `model sheet status` や `image prompt anchor` の短い参照を置いてよい。

## Visual Character Sheet の扱い

Visual Character Sheet は、画像/漫画生成用の固定資料だ。
対象は主人公とヒロインだけ。
モブ、名前付きNPC、cast NPC、重要NPCには作らない。

- 主人公: 新規開始時に `Appearance Profile` から `current/player.md` へ text-only で作る
- ヒロイン: `cast/heroine/[名前].md` へ昇格した時、漫画化 / 画像生成 / ヒロインPV化対象時、または再登場見込みで外見・服装・顔つき・仕草を固定したい時に作る
- 三面図/turnaround は必須ではない。image gen skill を使う段階で必要なら生成する
- `model sheet status` は `none` / `text-only` / `prompt-ready` / `image-generated` のどれかにする
- `Appearance Profile` は現在状態、Visual Character Sheet は固定資料として分ける

## 知識スコープの扱い

誰が何を知っているかは、cast file の固定人格ではなく、**current layer の運用情報**として扱う。

- 正本は `current/gm.md` の `知識スコープ台帳`
- ヒロインだけの見取り図は `current/harem.md` に補助として置いてよい
- cast file には「秘密を持つ性格」や「開示条件」は残してよいが、今どこまで誰が知ったかは current 側で管理する

知識の段階は 3 つに分ける。

- `known`: 固有名詞を含めて明示してよい
- `suspected`: 気配や仮説としてぼかしてよい。隠している固有名詞は出さない
- `unknown`: その話題に自力で触れさせない

補足:

- 文字視、触読、記憶酒、推理、嗅覚などの察知能力は、直接共有や現場観測がない限り `suspected` 止まり
- 会議、告白、報告、共同作戦で共有されたら `known` に上げてよい
- 「誰に秘密を明かしたか」という出来事そのものは `historical fixed` や archive に残してよい
- 現在の知識範囲そのものは current 側で更新し続ける
- `Anti-Leading` は、NPC/ヒロインが未発見情報へ不自然に誘導しないための境界として `current/gm.md` に置く
- `Anti-Meta Dialogue` は、作中人物の台詞に GM、シナリオ、フラグ、イベント、好感度、判定などを出さないための実行ガードとして扱う

## 年齢の扱い

日数カウントと年齢ラベルは、同じものとして扱わない。

- `第101日` のような日数は、進行管理と曜日感覚のために使ってよい
- `25歳` `20代半ば` などの年齢ラベルは、基本的に `core fixed`
- 日数が進んだだけで自動的に年齢を1つ上げない

年齢を更新してよいのは、次の場合だけ。

- 誕生日を作中イベントとして明示した
- 1年以上の大きなタイムスキップを採用した
- プレイヤーが「年齢も進める」と明示した

## 登場時の仕分け

### 1. モブ

- 名も役割もその場限り
- 保存しない。必要なら「店主」「運転手」などの役割名だけ
- 次回再登場を前提にしない

### 2. 名前付きNPC

- 名前はあるが、まだ卓の骨格には乗っていない
- まずは `current/gm.md` の短い要約で管理
- 目安は bond 1-2。ただし bond 値だけで固定しない

### 3. cast NPC

- 再登場前提
- 声がぶれると困る
- ルートの鍵を握る
- scene lead を張る
- 秘密、価値観、拒否条件が要る

この段階に入ったら `cast/npc/*.md` を作る。

### 4. ヒロイン

- 恋愛進行を継続管理する
- AFFINITY が必要
- 嫉妬、呼称変化、二人きりの進行、ハーレム運用に入る

この段階に入ったら `cast/heroine/*.md` を作る。
同時に text-only の Visual Character Sheet を作り、model sheet status、image prompt anchor、continuity locks、negative prompt / avoid の保存欄を持たせる。

## 昇格ルール

### モブ -> 名前付きNPC

- プレイヤーが名前を聞いた
- その人物の視点や事情が必要になった
- 同じ人物が二度目に出る見込みがある

### 名前付きNPC -> cast NPC

次のどれか1つでも満たしたら、次の scene に入る前か次回 save までに `cast/npc/*.md` を作る。

- 二回目の再登場が決まった
- scene lead になる
- ルートの鍵になる
- bond 2 以上で、口調や距離感の再現ミスが痛い
- プレイヤーが名前を覚え、こちらも継続して使うつもりになった
- 秘密、拒否トリガー、個人の行動原理が要る

### cast NPC -> heroine

- ロマンス進行を current で追う必要が出た
- AFFINITY 管理が必要になった
- 嫉妬、約束、独占、初体験、告白などが継続軸になった
- プレイヤーと GM の双方が恋愛主役級として扱い始めた

### 原則

- 昇格はするが、安易に降格はしない
- bond は目安であって唯一条件ではない
- 声がぶれると事故るかを重視する

## 圧縮ルール

- cast ファイルに時系列ログをだらだら書かない
- 詳細本文は archive に送る
- cast ファイルには「何が変わったか」だけ要約で残す
- old echo は current 側で消すか archive に送る
- volatile を cast ファイルへ持ち込まない
- `Appearance Profile`、`Ability Constraint Profile`、`Work Profile`、`Life Base`、`Equipment / Tools` の現行値を圧縮で落とさない
- `Organization Doctrine Layer` は `design/villain_design.md` に畳み、current には今効く接触面と圧だけを残す
- Equipment は数値装備ではなく、行動選択肢、リスク、痕跡、関係リスクとして要約する
- session をまたいで cast をコピーする時は、初期テンプレとして扱い、その session の current 事実を混ぜない

## 再昇格ルール

archive に送った古い出来事でも、次の条件なら再び hotset / current 側へ引き上げてよい。

- 直接言及された
- 関係悪化や嫉妬の原因として再燃した
- 敵勢力の再登場で過去因子が必要になった
- 呼称や口調再現のために必要になった

再昇格後も、本文の正本は archive に置いたままにする。current へ戻すのは短い運用要約だけ。

## 昇格時の処理

1. どの層へ上げるか決める
2. `core fixed` を抜く
3. `historical fixed` を抜く
4. session 配下に cast file を作る
5. ヒロインへ昇格する場合だけ Visual Character Sheet を作る。NPCには作らない
6. `indexes/cast_index.md` に追加する
7. current 側へ反映する
8. 次の scene から新しい正本を読む

作ったのに読まずに本文へ入らない。

## cast ファイルの目安

### `cast/heroine/*.md`

残すべきもの:

- 基礎情報
- tone
- personality / values
- Layer 構造
- 恋愛固有の現在段階
- Visual Character Sheet（model sheet status と image prompt anchor を含む）
- fixed memory の要約

削りやすいもの:

- 途中経過の長文ログ
- 一時的な照れや気まずさ
- その時だけの調査メモ

### `cast/npc/*.md`

残すべきもの:

- 骨
- 壁
- 育つ部分
- 台詞の癖
- fixed memory の要約

削りやすいもの:

- current 側で十分な臨時情報
- 終了済みの一時案件ログ

## Legacy Import

旧 layout の cast や session 直下 mirror を読む必要がある場合は、次の扱いにする。

- legacy は read-only
- 読み取った事実は該当 session の `cast/*`、`current/*`、`design/*` に移す
- legacy 側へ書き戻さない
- legacy の stale 状態を理由に current を巻き戻さない

## 次の移行方針

1. legacy cast にある `historical fixed` 相当の塊を見つける
2. session 配下の `cast/*` へ移す
3. `echo` と `volatile` を current 側へ逃がす
4. 詳細本文は archive へ退避する
5. cast ファイルは「今後の台詞と関係再現に必要な量」に止める
