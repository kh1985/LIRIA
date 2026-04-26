# prompt/case_engine

このファイルは LIRIA v1 の case engine 正本である。
役割は、固定ストーリーを書くことではない。
事件 / 依頼 / 違和感を、プレイヤーが自由に触れる **短い事件カード** として管理することだ。

## 基本方針

- ストーリーの順番は固定しない
- だが、今動いている事件には「次に触れる足場」を持たせる
- 謎の全容は隠してよい
- 短期目的、触れる物、人、場所、放置時の悪化は隠すな
- 事件カードは保存効率を優先し、長文描写や会話ログを入れない

## 保存先

事件カードは `current/case.md` に保存する。

`current/gm.md` には重複して長く書かない。
`current/hotset.md` には、再開に必要な active case の最小抜粋だけを書く。

## Light Story Reference Pass

fast profile では `prompt/story_reference.md` 全文を通常起動に入れない。
それでも新規開始時は、Q6 後の `Initial Story Assembly` で最低限の story reference 接続を必ず行う。

この pass で行うこと:

1. Q0-Q6 / Optional Avoid Notes から `selection signals` を抽出する。
   - 生活導線、恋愛 / ヒロイン、能力、制度 / 記録、組織、場所、インナー、避けたいモチーフを見る。
2. Reference Engine を 1-3 個だけ選ぶ。
   - 既存 stock を使ってもよいが、固有作品名、キャラ、名場面、台詞、展開は使わない。
   - 合わなければ session-derived engine を作ってよい。
3. 採用 engine を LIRIA へ変換する。
   - 現代社会、生活導線、恋愛 / ヒロイン、能力、関係組織、場所の手触りへ落とす。
4. `design/story_reference.md` に採用メモを短く残す。
   - selection signals、candidate shortlist、selected engine、LIRIA conversion、avoid direct imitation を残す。
5. `design/story_spine.md` に薄い背骨を作る。
   - Main Question / Reveal Ladder / Pressure Direction / Heroine Tie を最低限作る。
6. 組織や外圧がある場合、`design/organization_cast.md` に主要人物候補を 3-5 人作る。
   - 現場担当、交渉担当、理念担当、内部矛盾担当、ヒロイン生活圏担当の役割を分ける。
7. `current/case.md` に、最初に触れる人・物・場所・記録・期限・if ignored・next visible change を落とす。

この pass は固定プロットを作る工程ではない。
初回シーンが、抽象語ではなく「誰が、何で困っていて、最初に何へ触れるか」を持って始まるための配線である。

### Initial Story Assembly から case を作る時の契約

- `current/case.md` には、今触れる足場だけを短く置く。
- Reference Engine 名、元作品の固有名詞、黒幕の全体像、長い真相説明、固定章立てを case に入れるな。
- active case があるなら、`visible problem / visible request / short goal / handles / progress condition / if ignored / next visible change` を空にするな。
- `handles` は 2-5 個に絞り、物、人、場所、記録、関係、能力反応の入口にする。
- ヒロインや重要NPCの利害は `relationship stake` に短く置き、好意確定や攻略報酬にしない。

## Case Card Format

`current/case.md` は、active case を最大1件、background case を最大2件まで持つ。
3件を超える場合は、弱いものを `archive/events/` か `indexes/event_index.md` へ落とせ。

```text
## Active Case
- id:
- title:
- phase:
- visible problem:
- visible request:
- short goal:
- handles:
- progress condition:
- if ignored:
- next visible change:
- relationship stake:
- last delta:

## Background Cases
- id:
  - title:
  - pressure:
  - if ignored:
  - next ping:
```

各項目は短く書け。
1項目1行を原則にし、長い説明文にするな。

## Phase

事件は以下のどれかの phase に置く。

- `seed`: まだ匂いだけ
- `entry`: 入口が見えた
- `offered`: 依頼、相談、持ち込みが出た
- `accepted`: プレイヤーが関与を選んだ
- `first_handle`: 最初に触れる物 / 人 / 場所が決まった
- `pressure`: 相手側や世界側の圧が見えた
- `choice`: 守る / 進める / 退く / 能力使用などの判断点
- `progress`: 何かが一段分かった
- `aftermath`: 余波、関係変化、生活への戻り
- `background`: プレイヤーが今は触っていないが裏で動いている
- `closed`: 現在の事件としては閉じた

同じ phase で説明だけを何シーンも続けるな。
2シーン続けて `last delta` が空なら、次のシーンでは必ず `progress / pressure / choice / aftermath` のどれかを発生させろ。

## Visible Request Gate

初回の `entry / offered` では、真相は隠してよい。
ただし、依頼や相談として成立する見える情報は隠すな。

最低限、本文か事件カードに以下を短く出せ。

- 依頼人 / 相談者
- 当事者の最低限の属性、または名前を伏せる理由
- 困っている手続き / 物 / 場所 / 記録
- 放置すると止まる生活、仕事、関係、期限
- 主人公に最初に頼む行動
- 今すぐ触れる handles 2-4個

原因、黒幕、能力の本質、組織の全体像は隠してよい。
依頼の主語、困りごと、頼む行動まで隠すな。

## Handles

`handles` は、プレイヤーが次に触れる足場である。
抽象語ではなく、物、人、場所、記録、関係、能力使用の入口にしろ。

良い例:
- `上司の名刺`
- `社員証`
- `机の引き出し`
- `会議室`
- `面談記録`
- `梓の証言`
- `今夜の着信`

悪い例:
- `会社の違和感`
- `謎を調べる`
- `印の正体`
- `組織の闇`

## Progress Condition

`progress condition` は、この場面で何が分かれば一段進むかを書く。
真相全体ではなく、小さな前進でよい。

例:
- `どの物が異常の入口か1つ分かる`
- `誰が記録を消したかではなく、どの記録が消えたか分かる`
- `ヒロインが何を隠しているかではなく、隠している理由の種類が見える`

## If Ignored

プレイヤーが事件を無視した場合、事件は停止しない。
ただし、全フックを一気に悪化させるな。

`if ignored` には、放置時に起きる具体変化を短く書け。

例:
- `記録が消える`
- `対象が再発する`
- `ヒロインが会社で疑われる`
- `相手が別の接触面へ移る`
- `証拠が移送される`

## 遠出 / 寄り道

プレイヤーが別の街、旅行先、沖縄などへ行ってよい。
その場合:

- 今の active case は `background` へ落としてよい
- `if ignored` に従って裏で1つだけ変化させる
- 新しい土地では、必要になった時だけ local case を小さく作る
- local case は、その土地の人、店、道具、生活導線から作る
- 元の事件を白紙リセットするな

## Runtime Rule

GMは各シーン開始前に `current/case.md` を確認する。

- active case があるなら、本文中に `short goal` か `handles` のどれかを自然に出す
- case は `story_spine` の実行表ではなく、今プレイヤーが触れる足場である。story_spine の抽象語をそのまま本文へ出すな
- 新しい謎を足す時は、既存 case の `handles` か `next visible change` に接続する
- 接続できない謎は、今は出さないか background case に落とす
- プレイヤーが迷っている時は、新しい謎を足さず、`visible problem / handles / progress condition` を短く返す

## Token Budget

事件カードは軽く保て。

- active case は 12行以内を目安にする
- background case は1件4行以内
- 固有名詞、長い心理描写、台詞、伏線説明を詰め込まない
- 伏線の長文は `current/gm.md` ではなく、必要に応じて `archive/events/` へ送る
- 再開時に必要なのは「次に何を触れば進むか」であり、過去ログの再現ではない
