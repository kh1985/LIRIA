# CLEANUP REPORT

## 削除 / 退避候補

- `saves/session_001/`
  - 本体には含めず、個人プレイログ / 旧実セッションとして repo 外へ退避する対象。
  - この作業では「本体から除外する方針」と `.gitignore` を整備した。ローカルに実在する場合の物理移動は未実施。
- `saves/*`
  - 実セッション全般を Git 管理対象外に変更。
- `logs/`, `rawlogs/`, `tmp/`, `*.local.md`
  - ローカル作業物として Git 管理対象外に変更。

## session_001 固定参照の除去結果

- `README.md`
  - `session_001` 前提を削除し、`bash play.sh new` / `bash play.sh resume` / `bash play.sh liria ...` の汎用説明へ更新。
- `docs/usage/startup.md`
  - 再開例を `session_001` 固定から `session_002` の汎用例へ変更。
- `ARCHITECTURE.md`, `INTEGRITY_CHECK.md`, `TODO.md`
  - `session_001` を本体前提の記述から外し、「repo 外の個人 legacy asset」扱いへ変更。

## 固有名詞の整理結果

- コア文書内の `月読堂`, `澪`, `凪`, `怜`, `真凛`, `シルヴィ`, `kaneko`, `kaneco` は、可能な範囲で以下へ抽象化した。
  - `拠点共同体`
  - `主人公`
  - `和装ヒロイン`, `実務派ヒロイン`, `夜の店ヒロイン`, `自由人ヒロイン`, `公権力出身ヒロイン`
- `K&N`, `Lys`, `つくよみケア` は今回の検索対象内では見つからなかった。

## 新規プレイ開始に必要な最小ファイル

- `play.sh`
- `scenarios/liria/config.sh`
- `scripts/create_session.sh`
- `templates/session/**`
- `GALGE.md`
- `prompt/*.md`
- `style/*.md`

## 人間が次に確認すべき点

- ローカルに `saves/session_001/` や個人ログが残っている場合、repo 外の退避先へ移す。
- `bash play.sh new` で新規 session を作り、`templates/session/` から期待通りに scaffold されるか確認する。
- 公開前にもう一度固有名詞検索を回し、今回の検索対象以外の私物ワードが未混入か確認する。
- `prompt/` と `style/` の抽象化表現が、実運用で弱すぎないかを実プレイで確認する。
