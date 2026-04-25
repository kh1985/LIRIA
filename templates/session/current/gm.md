# GM State

> ここは `design/initial_answers.md` から反映された運用用の current GM state。事件とフックはプレイ中に更新する。

## World Seed

## 初期生活圏台帳 / Base Area Dossier
> Q1 の拠点/生活圏から作る運用用の土地台帳。本文では説明せず、描写・導線・小物・組織接触面へ変換する。

- 地域名:
- 実在アンカー:
- 土地の質感:
- 主人公の接点:
- ヒロイン導線:
- 組織の接触面:
- シーン小物:
- 汎用化回避:
- 情報の確度:

## First Daily Disturbance
> Q5 で選ばれた、最初に揺れる日常の面。本文では「事件タイプ」として説明せず、生活上の小さな乱れとして出す。

## Incident Seeds

## 現在のフック / Active Hooks
- 1:
- 2:
- 3:

## Local Expansion Notes
> 未準備地で生成した接点のうち、再訪/連絡/事件接続/プレイヤー関心が立ったものだけ短く残す。通行人や一度きりの店は保存しない。

- location:
  - one face:
  - one bridge:
  - one cost:
  - status: named one-shot | recurring contact | dossier candidate

## 土地台帳 / Location Dossiers
> 遠出先、旅先、未準備地が再訪/連絡/事件接続/プレイヤー関心で重要化した時だけ昇格する。観光説明ではなく、描写と導線の足場。

- location:
  - 地域名:
  - 実在アンカー:
  - 土地の質感:
  - 主人公の接点:
  - ヒロイン導線:
  - 組織の接触面:
  - シーン小物:
  - 汎用化回避:
  - 情報の確度:
  - status: active | recurring | archived

## Manga Export Candidates
> 自然文で漫画化 / ヒロインPV / 三面図 / 立ち絵 / キャラシートを求められた時の候補。相談型は作中時間を止めて2-3個だけ提示する。実生成明示型は裏ジョブ化して物語を止めない。未確定秘密を絵で確定させない。

- candidate:
  - source:
  - export type: model-sheet | heroine-teaser | scene-card | one-page
  - target characters:
  - appeal:
  - guardrails:
  - package path:
  - status: proposed | selected | packaged | queued | generating | generated | failed

## 脅威クロック / Threat Clocks

## 勢力クロック / Faction Clocks

## Organization Doctrine Current Pressure
> 長期設計の正本は `design/villain_design.md`。ここには今効いている接触面と外圧だけを置く。

- 関係組織:
  - Organization Doctrine:
  - contact surface:
  - 今動いている外圧:
  - weak joint / 弱い継ぎ目:
  - 内部矛盾:
  - 外部レバレッジ:

## Plausibility Notes

## 知識スコープ台帳 / Knowledge Notes

## Knowledge Boundary / Anti-Leading
- known:
- suspected:
- unknown:
- こちらから誘導してはいけない未発見情報:

## Anti-Meta Dialogue Guard
- 台詞に出さない語: GM / シナリオ / フラグ / イベント / 好感度 / 判定
- 作中での言い換え:

## 直近の後遺症 / Recent Consequences

## 直近の成長監査 / Recent Growth Audit

## プレイヤー観測メモ（軽量） / Player Observation Notes

## 自動セーブ管理 / Autosave Counter
- 方針: 10シーンごと
- 実行補助: 通常シーン終了時に `bash scripts/autosave_turn.sh <session_name>` を使う
- 前回保存からのシーン数: 0/10
- 最終保存:
- 次回自動保存:
- 自動セーブ保留: なし
