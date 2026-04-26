# Technical Integrity Check Plan

## 結論

- Technical Integrity は repo / script / docs / template / prompt assembly の技術的な破綻を防ぐためのチェックである。
- Gameplay Integrity とは別物である。
- `scripts/check_repo_integrity.sh` は実行実装、本文書は仕様書である。

Technical Integrity は「実行基盤が壊れていないか」を見る。ファイルが存在し、構文が通り、参照先が実在し、生成物が Git に混ざらず、通常起動や resume が必要な情報だけを読む構造を保っているかを確認する。

## Gameplay Integrity との違い

| 区分 | 見るもの | 主な対象 |
| --- | --- | --- |
| Technical Integrity | ファイル、構文、参照、生成物混入、安全性、CLI、portability、prompt assembly、処理効率 | `scripts/*`, `play.sh`, `liria`, `scenarios/*`, `templates/session/*`, docs links, Git tracked files |
| Gameplay Integrity | 物語本文、保存、再開、能力、事件、ヒロイン、組織圧の連動 | raw log, `saves/<session>/current/*`, `cast/*`, `design/*`, `indexes/*`, `archive/*` |

Technical Integrity は「repo と実行経路が壊れていないか」を判定する。Gameplay Integrity は「長編 AI TRPG として、本文で起きた変化が保存され、再開され、物語上の意味を持ち続けるか」を判定する。

## チェック項目

| 項目 | 目的 | 現在の実装状況 | OK条件 | WARN条件 | FAIL条件 | 将来の追加候補 |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Repo構造の健全性 | LIRIA の root / prompt / scenario / template / script 構造を保つ | `check_repo_integrity.sh` が必須 root, template, prompt file を存在確認 | 必須ファイルと主要ディレクトリが揃う | 任意ディレクトリや executable bit が欠ける | 必須ファイル欠落、root entrypoint 欠落 | `templates/session/**` の階層を manifest 化して検査 |
| 2. Entry Point / CLIの健全性 | `play.sh` / `liria` が起動口として壊れていないことを見る | `bash -n play.sh liria` の構文確認のみ | CLI script が構文上有効 | help / prompt-only smoke 未実施 | entrypoint 欠落、構文エラー | `bash play.sh --help`, `bash play.sh list`, `bash play.sh cleanup-sessions --dry-run` の軽い smoke |
| 3. Python / shell構文 | script が構文エラーで止まらないことを保証 | `python3 -m py_compile scripts/*.py`, `bash -n scripts/*.sh play.sh liria` | 全対象が構文OK | shell executable bit 欠落 | Python / shell 構文エラー | Python import smoke、shellcheck は任意の heavy check |
| 4. 必須ファイル存在確認 | README の利用手順と scaffold の前提が実在することを保証 | root, prompt, README掲載コマンド対象を存在確認 | listed file が存在 | README と実装が軽微にずれる | README の主要コマンド対象や prompt 正本が欠落 | README から command target を抽出して自動検査 |
| 5. Prompt assembly参照確認 | `scenarios/liria/config.sh` の prompt file 列挙が実在し、profile が意図通り軽重分離されることを見る | `play.sh` 実行時は欠落で fail、repo check では固定 prompt file のみ確認 | fast / lite / full の列挙先が全て実在 | full 用 heavy prompt が通常 profile に混ざりそう | 通常起動で不要な heavy prompt を常時読む | config の array を shell で展開して全 profile の file existence と heavy 混入を検査 |
| 6. Markdownリンク確認 | docs のローカル `.md` リンク切れを防ぐ | README / ARCHITECTURE / TODO の `.md` link を検査 | 参照先が実在 | docs/maintenance など未検査範囲にリンク切れ可能性 | 主要 docs のリンク切れ | docs 全体へ拡張する `--full` mode |
| 7. Session template / save schema確認 | 新規 session scaffold が self-contained で正本階層を持つことを見る | 必須 template file の存在確認。session 個別は `check_session_integrity.sh` が担当 | `session.json`, `current`, `cast`, `design`, `indexes`, `archive` が揃う | 任意 sidecar や `.gitkeep` 欠落 | session scaffold の必須階層欠落 | `session.json` の軽い JSON schema / layout_version / source_of_truth 検査 |
| 8. Legacy fallback確認 | rename 後の正本名と legacy read-only fallback の境界を守る | `check_session_integrity.sh` が `current/harem.md` fallback を warning 扱い | `relationships.md` が正本、legacy は read-only fallback | legacy mirror が残るが main path へ混ざらない | 新規 session が `harem.md` mirror を作る、fallback を正本化する | repo check で template に legacy mirror がないことを確認 |
| 9. Git管理外生成物混入チェック | `saves`, `exports`, logs, generated prompt, cache が Git に混ざるのを防ぐ | `git ls-files` に対して generated path guard | generated / local artifact が tracked されない | 未知の generated path が guard 外にある | saves / exports / logs / `.codex/generated` 等が tracked | guard pattern の manifest 化、large local file detection |
| 10. 削除系コマンドの安全性 | cleanup が誤削除や tracked file 削除をしないことを見る | `play.sh cleanup-sessions` は protected / tracked / unsafe name を判定。repo check は未検査 | dry-run で候補、保護、削除不可が分かる | dry-run smoke 未実施 | tracked file や unsafe path を削除候補にする | `cleanup-sessions --dry-run` を `--full` で smoke |
| 11. Prompt肥大化 / heavy prompt誤読込 | 通常プレイの prompt が過大になりすぎないようにする | `liria_prompt_auditor.py --root .` を repo check が実行し warn を拾う | fast/lite が通常用途に必要な prompt だけ読む | prompt が大きい、重複がある、lite が大きい | heavy surface prompt が通常 profile に混入 | profile ごとの char count budget と duplicate policy detection |
| 12. 外部private path依存 | 個人PCの絶対パスや private file 前提を repo に混ぜない | 現行 repo check では未実装 | repo 内相対パスと portable command で完結 | README に個人環境例が残る | `/Users/...`, private token, local-only path が実行前提になる | private path grep、secret-like token grep |
| 13. Portability | macOS 以外や minimal shell 環境で壊れにくくする | `bash -n` と `python3` availability のみ | bash / python3 / git があれば軽い check が動く | `rg` など任意依存がないと一部 skip | 必須処理が非portable command 固定 | dependency report、GNU/BSD 差分を避ける smoke |
| 14. Observability / 出力の分かりやすさ | check の結果から次に直す場所が分かるようにする | `[OK]`, `[WARN]`, `[FAIL]`, summary を出す | fail と warning がファイル名付きで読める | warning が多すぎて日常利用しにくい | fail 理由が不明、summary がない | machine-readable output、warning category、`--quiet` / `--full` |

## Architecture / Algorithm Efficiency

### 目的

LIRIA が長編化・多機能化しても、起動、再開、保存、AI playtest、分析、prompt assembly が重くなりすぎないようにする。

Technical Integrity では、単に「動くか」だけでなく、構造が保守しやすく、必要な情報だけを読む設計になっているかを見る。通常起動・resume・日常 check は軽く保ち、重い sidecar、archive、AI 実行、全ログ分析は必要時だけ使う。

### 1. Prompt Assembly Efficiency

見る観点:

- fast profile が通常プレイに必要な prompt だけを読んでいるか。
- full profile / heavy surface prompt が通常起動に混ざっていないか。
- visual / manga / story_reference などの重い sidecar を常時読んでいないか。
- `LIRIA.md` + `prompt/*.md` の順番が明確か。
- 同じルールが複数 prompt に重複していないか。

判定:

- OK: fast は core / gm policy / case / runtime / combat / villain / romance / save-resume など通常プレイに必要な prompt を読み、heavy surface prompt は full だけで読む。
- WARN: prompt 重複、lite/fast の肥大、重い専門 prompt の境界が曖昧。
- FAIL: 通常起動で visual / manga / story_reference などの heavy prompt を常時読む。

将来の実装候補:

- `scenarios/liria/config.sh` の profile array を展開し、存在確認、順序、heavy prompt 混入、char count を検査する。
- 通常 mode では存在確認だけ、`--full` では profile ごとの size budget と重複検査まで行う。

### 2. Resume Efficiency

見る観点:

- resume 時に `current/hotset.md`, `current/case.md`, `current/relationships.md`, cast index など軽量入口を優先しているか。
- archive 全文や重い design sidecar を毎回読んでいないか。
- hotset が derived cache として短く保たれているか。
- hotset が攻略メモ化・長文ログ化していないか。

判定:

- OK: resume は hotset / case / relationships / indexes から入り、必要な cast と design だけ開く。
- WARN: hotset が長い、index 経由せず archive に触りがち、design sidecar を毎回読む文言がある。
- FAIL: resume が archive 全文前提になる、hotset が正本化する。

将来の実装候補:

- hotset の行数 / char count / resume anchor 数を軽く検査する。
- `templates/session/README.md` の Read Priority と `scenarios/liria/config.sh` の resume prompt 文言が矛盾しないか確認する。

### 3. Save / State Layout Efficiency

見る観点:

- `current`, `cast`, `design`, `indexes`, `archive` の責務が分離されているか。
- 同じ情報が複数ファイルに重複保存されていないか。
- `current` に履歴ログを詰め込みすぎていないか。
- `design` に置くべき長期設計が `current` に漏れていないか。
- `archive` に置くべき履歴が `hotset` に残り続けていないか。

判定:

- OK: live snapshot は `current`, 人物正本は `cast`, 長期設計は `design`, 参照口は `indexes`, 履歴は `archive` に分離される。
- WARN: current 肥大、hotset 肥大、design と current の説明重複。
- FAIL: 同じ状態が複数ファイルで矛盾する、archive 履歴が hotset に残り続ける。

将来の実装候補:

- session template と live session の layout_version / source_of_truth を検査する。
- current file の size guard と archive/index 参照の存在確認を `--full` で行う。

### 4. Script Efficiency

見る観点:

- scripts が毎回重い `find` / `grep` / AI 実行をしていないか。
- `check_repo_integrity.sh` の通常モードが重くなりすぎていないか。
- 重い検査は `--full` または別 script に逃がせるか。
- AI Player Harness の dry-run と実 run が明確に分かれているか。
- `cleanup-sessions` などの削除系が不要な探索をしすぎていないか。

判定:

- OK: 通常 check は構文・存在・リンク・軽い auditor に留める。
- WARN: repo 全体 grep や saves 全体走査が通常 mode に増える。
- FAIL: 通常 check が AI 実行、Harness 本実行、大量ログ分析、全 archive 走査を行う。

将来の実装候補:

- `check_repo_integrity.sh --full` を追加して、cleanup dry-run、prompt-only smoke、profile budget、private path grep を分離する。
- 重い構造検査は `scripts/check_architecture_efficiency.py` に切り出す。

### 5. AI Player / Analysis Efficiency

見る観点:

- AI Player Harness が不要に長い prompt を生成していないか。
- raw log / analysis / report の出力先が整理されているか。
- `analyze_play_log.sh` と将来の `check_gameplay_integrity.py` の責務が重複していないか。
- persona ごとに必要な情報だけを渡しているか。

判定:

- OK: dry-run は scaffold / prompt / report 生成で止まり、実 AI 実行や長時間分析は明示時だけ行う。
- WARN: persona ごとに重い prompt や analysis を重複生成する。
- FAIL: 通常 repo check が AI Player Harness 本実行を走らせる。

将来の実装候補:

- Harness report path と raw log path の存在確認を `--full` または専用 check に置く。
- Gameplay 側の意味検査は Technical Integrity から分離する。

### 6. Architecture Coupling

見る観点:

- prompt, scripts, templates, docs の責務が混ざっていないか。
- docs は説明、scripts は実行、templates は scaffold、prompt は GM ルールとして分離されているか。
- `LIRIA.md` が orchestrator、`prompt/*.md` が正本という関係が明確か。
- `relationships.md` や `LIRIA.md` のような rename 後の正本名が全体に一貫しているか。

判定:

- OK: 通常起動・resume・検証が軽量入口を使い、重い sidecar は必要時だけ読む。
- WARN: prompt に maintenance 手順が混ざる、docs に live session state が混ざる、rename 後の用語が一部古い。
- FAIL: scripts が prompt 本文を正本化する、templates が live save を含む、`harem.md` や `GALGE.md` が新規正本として復活する。

将来の実装候補:

- rename guard と legacy fallback guard を軽量 grep で検査する。
- docs / scripts / templates / prompt の責務境界を manifest 化する。

## 現行 check_repo_integrity.sh が見ているもの

- `git diff --check`
- staged diff check
- `python3 -m py_compile scripts/*.py`
- `bash -n scripts/*.sh play.sh liria`
- 必須 root / template / prompt file 存在
- README 掲載コマンド対象ファイル存在
- README / ARCHITECTURE / TODO の `.md` link 存在
- tracked generated files guard
- `liria_prompt_auditor.py --root .`

## 現行でまだ見ていないもの

- `play.sh` の軽い CLI smoke
- `cleanup-sessions --dry-run`
- `scenarios/liria/config.sh` の prompt file 列挙存在確認
- `session.json` schema の軽い検査
- legacy `harem.md` fallback の存在検査
- private path grep
- portability 検査
- `check_repo_integrity.sh --full` のような重めモード

## 将来の実装方針

- 通常モードは軽く保つ。
- 重いチェックは `--full` に分ける。
- AI 実行や Harness 本実行は通常モードに入れない。
- `cleanup-sessions` や prompt assembly smoke は `--full` でよい。
- WARN を増やしすぎて日常利用を重くしない。
- 処理効率の検査は、まず軽い file existence / size / profile boundary / path guard から始める。
- 重い構造チェックは `check_repo_integrity.sh --full` または `scripts/check_architecture_efficiency.py` に分ける。

## README/TODOへの追記案

今回は README / TODO を変更しない。

将来必要なら README に仕様書リンクを 1 行追加する程度に留める。

例:

```md
- Technical Integrity の設計方針: `docs/maintenance/technical_integrity_check_plan.md`
```
