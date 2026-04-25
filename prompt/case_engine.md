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

## Case Card Format

`current/case.md` は、active case を最大1件、background case を最大2件まで持つ。
3件を超える場合は、弱いものを `archive/events/` か `indexes/event_index.md` へ落とせ。

```text
## Active Case
- id:
- title:
- phase:
- visible problem:
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
