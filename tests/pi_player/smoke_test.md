# PI Player Smoke Test

## Session Name

- `session_pi_smoke` を使う

## Goal

- 新規セッション作成
- Q&A Test Profile の適用
- `design/initial_answers.md` への保存確認
- `current/*.md` への分配確認
- `hotset.md` が短いことの確認
- GM仕様の入力解釈確認

## Setup

1. 既存の `saves/session_pi_smoke` があれば削除する
2. `bash scripts/create_session.sh liria session_pi_smoke .` で新規セッションを作る
3. `bash scripts/check_session_integrity.sh session_pi_smoke` を実行する

非TTY環境では、`bash play.sh liria new session_pi_smoke --prompt-only` を使うと、engine を起動せずに session 作成と prompt 組み立てだけ確認できる。

## Q&A Profile

`prompt/pi_player.md` の `Q&A Test Profile` を使う。

確認点:

- Q&A結果が `saves/session_pi_smoke/design/initial_answers.md` に入る
- `current/player.md`, `current/gm.md`, `current/harem.md` に要約分配される
- `current/hotset.md` に Q&A 全文を入れない

## Behavior Checks

以下の 5 ケースを最低 1 回ずつ確認する。

1. 通常入力
2. 内心入力
3. `gm` 相談
4. 誘導耐性
5. 知識境界

確認観点:

- 通常入力は物語内行動として処理される
- 内心入力は GM だけが解釈し、通常キャラには直接共有されない
- `gm` 相談は物語を進めず、メタ解説になる
- 誘導発言は推測として扱われ、好意や真相を即時確定しない
- Character Knowledge Boundary を破らない

## Smoke Log

- `pi_smoke_log.md` から、各ケースを示す短い抜粋を人間レビュー用に要約する
- 長い本命プレイには進めない

## Cleanup

1. 検証結果を要約する
2. `saves/session_pi_smoke` を削除する
3. 実セッションを Git 管理対象に加えない
