# Legacy Concept Audit

Note: This audit predates the `GALGE.md` -> `LIRIA.md` rename. Mentions of
`GALGE.md` below describe the former prompt orchestrator name as historical
context.

## 結論

- 現時点で、LIRIA の中核 prompt / requirements / session template に「ヒロイン攻略報酬化」「AFFINITY 到達による自動解禁」「ハーレム構築の主目的化」「能力無双」「戦闘勝利報酬」「異世界・魔王討伐の標準化」「G 通貨や拠点投資の主目的化」といった危険な旧思想の残骸は見当たらない。むしろ現行正本の多くは、これらを明示的に否定している。
- 名前だけの旧名残は残っている。特に `GALGE.md` は現役の prompt orchestrator であり、`templates/session/current/harem.md` は現役の関係性ネットワーク保存先である。中身は現行 LIRIA に寄っているが、名前は現行定義とズレるため rename 候補として強い。
- すぐ対応すべきなのは、実行導線に入っている旧名の整理と、active style layer の思想整理である。`style/reference.md` と `style/rules.md` は単なる履歴ではなく現役参照される層なので、古い冒険 RPG / ヒロイン類型 / 身体テンプレートの影響が実行時文体へ混ざるリスクがある。
- 後回しでよいものは、`docs/legacy/**`、禁止事項としての旧語、過去設計を説明する maintenance docs、別プロジェクト・参照棚として明示されている prototype / reference である。

## 監査方針

- この監査はキーワード grep ではなく、`git ls-files` によるファイル役割インベントリから、各ファイルの責務・文脈・現在の LIRIA 定義との整合性を読む意味監査である。
- 旧語の有無そのものは判定基準にしない。旧語が「禁止事項」「警告文」「legacy 説明」「過去の掃除ログ」として残っている場合は問題なしとした。
- 判定は以下で分けた。

| 判定 | 意味 |
|---|---|
| A. 問題なし | 現行 LIRIA 方針を支える、または legacy / 禁止事項として適切に隔離されている |
| B. 名前だけ違和感 | 中身は現行 LIRIA だが、ファイル名・見出し・外部パス名が旧い |
| C. 役割誤認リスク | 実行正本 / legacy / maintenance の境界が読者やツールに誤認されうる |
| D. 思想の名残リスク | 旧ゲーム目的・冒険 RPG 化・ヒロイン類型化などが生成へ影響しうる |
| E. 修正推奨 | rename、文言修正、docs 移動、参照差し替えを近いうちに行うべき |

## ファイル分類サマリ

| 分類 | ファイル群 | 判定 |
|---|---|---|
| root entry | `.gitignore`, `README.md`, `CONCEPT.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md`, `TODO.md`, `GALGE.md`, `play.sh`, `liria` | 主要説明は現行 LIRIA に整っている。`GALGE.md` は現役正本なのに旧名で B/E。`TODO.md` は現役タスクと古い構想整理が同居し C 低。 |
| prompt正本 | `GALGE.md`, `prompt/core.md`, `prompt/gm_policy.md`, `prompt/core_newgame.md`, `prompt/runtime.md`, `prompt/case_engine.md`, `prompt/combat.md`, `prompt/villain_engine.md`, `prompt/romance.md`, `prompt/save_resume.md`, `prompt/lite_*.md`, `prompt/story_reference.md`, `prompt/manga_export.md`, `prompt/visual_character_sheet.md`, `prompt/pi_player.md` | 中核は A。`GALGE.md` と `current/harem.md` 参照は B/C。`prompt/runtime.md` は冒険 RPG 風の例が active prompt に残り D/E。`prompt/romance.md` は AFFINITY 自動解禁を否定しており A だが、一部旧モデル名は B。 |
| script/tool | `play.sh`, `liria`, `scenarios/liria/config.sh`, `scripts/*.sh`, `scripts/*.py` | 実行導線は現行 `liria` に整理済みで A。`config.sh` と integrity scripts は `GALGE.md` / `harem.md` を現役 contract として固定しており B/E。AI/PI playtest の外部 `gal-sim-testers` fallback は C/E。 |
| session template | `templates/session/**` | 中身は layout v3 の current/archive/design/indexes 構造で A。`templates/session/current/harem.md` は関係性ネットワークとして正しく機能しているが名前だけ B/C/E。 |
| style layer | `style/rules.md`, `style/reference.md`, `style/defaults/*.md` | `style/defaults/*` は概ね A。`style/reference.md` と `style/rules.md` は active style layer として旧冒険・敵攻略・ヒロイン類型・身体テンプレートを混ぜうるため D/E。 |
| docs/current | `docs/architecture/**`, `docs/usage/**`, `docs/validation/**`, `docs/maintenance/**`, `docs/*.md` | 多くは現行説明または保守資料で A。`docs/top_level_cleanup_plan.md` と `docs/maintenance/core_notes.md` は役割を明記しており A。`TODO.md` 的な計画文書は読む入口によって C 低。 |
| docs/legacy | `docs/legacy/CLEANUP_REPORT.md`, `docs/legacy/PROMPT_SPLIT_PLAN.md` | legacy として隔離されており A。 |
| persona/test | `personas/*.yaml`, `personas/README.md`, `tests/**`, `prompt/pi_player.md` | QA 用 persona と smoke docs は A。旧語は拒否条件として使われる箇所が多い。外部 `gal-sim-testers` fallback だけ B/C/E。 |
| reference/prototype | `references/story_media_stock.md`, `prototypes/market_familiar.md` | 参照棚・別プロジェクト prototype と明示されており A。 |
| skill/local support | `skills/liria-prompt-auditor/SKILL.md`, `scripts/liria_prompt_auditor.py`, `docs/liria_prompt_auditor.md` | prompt/session hygiene の保守支援で A。今回も補助的に実行し、旧思想監査とは別軸の warning として扱った。 |

## 気になった箇所

| ファイル | 箇所 | 種別 | 内容 | 判定 | 推奨対応 |
|---|---|---|---|---|---|
| `GALGE.md` | ファイル名、root 正本、`README.md` / `ARCHITECTURE.md` / `scenarios/liria/config.sh` / integrity scripts からの参照 | B/E | 中身は `# LIRIA -- GMシステムプロンプト` で、現行定義と旧目的の否定が明確。ただし現役 prompt orchestrator の名前が `GALGE.md` のまま。 | 名前だけの旧名残。思想リスクは低いが、実行正本名なので誤認リスクは高い。 | `LIRIA.md` への rename と参照更新。移行中は compatibility alias を設けると安全。 |
| `templates/session/current/harem.md` | session current 正本、`prompt/save_resume.md` / `prompt/romance.md` / `prompt/runtime.md` / scripts / docs からの参照 | B/C/E | 内容は Relationship State であり、ヒロイン攻略帳ではなく関係性・情報共有・相互ベクトルの管理。だが active path が `harem.md`。 | 中身は A、名前は B。保存構造の source of truth なので C/E。 | `current/relationships.md` または `current/relationship_network.md` へ移行。旧 path は読み取り fallback として短期維持。 |
| `style/reference.md` | active style layer 全体 | D/E | 参考作品リストと episode algorithm が、冒険・敵・攻略・ダンジョン・技進化・敵との対峙を強く扱う。`ARCHITECTURE.md` と `GALGE.md` では style layer として現役扱い。 | 単なる reference/prototype ではなく、生成方針に混ざる可能性がある。旧冒険 RPG 化リスク。 | 現行 `prompt/story_reference.md` と `references/story_media_stock.md` に寄せて再設計。古い story engine 部分は legacy へ移す候補。 |
| `style/rules.md` | チラリズム描写ルール、ヒロイン別の例 | D/E | 成人ガードはあるが、和装・夜の店・自由人・実務派・公権力出身など固定ヒロイン類型と身体 / 下着例が active style rule にある。 | 自律した関係性の人物より、旧ギャルシム的な類型・身体テンプレートへ寄せるリスク。 | 「セッション由来の人物性に従う視覚フック」へ一般化。固定ヒロイン taxonomy と身体数値例は削る。 |
| `prompt/runtime.md` | サンプルと random event 周辺 | D/E | 村、長老、水路、焚き火、岩場、谷、行商人、酒場、宿、野盗、怪異、レアイベント、貴重なアイテム、ラッキースケベ等の例が active runtime に残る。 | ガードレールは現代 LIRIA を向いているが、例示が生成の誘導として冒険 RPG / 旧イベント表へ戻す可能性がある。 | 都市・学校/職場・生活接点・事件余波・関係性変化の例へ差し替え。 |
| `GALGE.md` | 文豪シーンテンプレートと AFFINITY による scene type 運用 | D 低 | AFFINITY に応じて scene style を変える説明がある。`prompt/romance.md` 側では自動報酬・身体的親密さの解禁ではないと明確に否定されている。 | 現状は危険な自動解禁ではないが、読み方によっては親密度ゲートに見えうる。 | 「許可 / 解禁ではなく描写密度の目安」と明記し、可能なら style bridge へ分離。 |
| `prompt/romance.md` | `gal-simベース`, `inner-trpgベース`, `current/harem.md` 参照 | B/C | 関係性設計は現行 LIRIA で、AFFINITY 自動報酬化を否定している。旧モデル名と保存ファイル名だけ残る。 | 名前だけの名残。思想リスクは低い。 | `relationships` rename 後に用語を更新。旧モデル名は「関係性観測モデル」などへ置換候補。 |
| `scripts/run_pi_player_smoke.py`, `scripts/run_ai_persona_playtest.py`, `tests/pi_player/*.md` | 外部 persona fallback path | B/C/E | local persona がある場合はそちらを使うが、fallback と docs に `/marketing/character/output/gal-sim-testers/...` が残る。 | runtime 正本ではないが、QA 導線が旧 gal-sim tester を呼び戻す可能性がある。 | fallback を `personas/` 配下の LIRIA persona に固定し、外部 path 依存を削除または任意指定化。 |
| `prompt/runtime.md` | 異形接触フック | D 低 | 現代の違和感・生活圏の圧力として使えば現行に合うが、裏世界・怪異退治へ広げると旧ジャンルへ傾く。 | ガード付きなら許容。過用時のみリスク。 | 事件と関係性に返る使用条件を強める。 |
| `docs/maintenance/core_notes.md`, `docs/top_level_cleanup_plan.md`, `TODO.md` | maintenance / planning 文書 | C 低 | 役割はかなり明記されているが、root の `TODO.md` は古い構想整理も含み、読み手によって現行仕様と混同しうる。 | 実行には影響しない。docs 導線整理の対象。 | 完了済み / 履歴部分は `docs/maintenance/` または `docs/legacy/` へ寄せる候補。 |
| `scripts/liria_prompt_auditor.py` の結果 | prompt assembly / numbered choices warning | C | 旧思想そのものではないが、`runtime` や prompt 群の肥大、番号選択肢 warning が出ている。 | prompt hygiene の残課題。旧思想監査とは別軸。 | prompt 分割・choice 表現の整理を別 task で継続。 |

## 名前だけの名残

- `GALGE.md` は現役 prompt orchestrator なので、`LIRIA.md` への rename 候補として最優先。
- `templates/session/current/harem.md` は中身が関係性ネットワークであり、`relationships.md` または `relationship_network.md` への rename 候補。
- `prompt/romance.md` の `gal-simベース` / `inner-trpgベース` は現行理論の由来として読めるが、現役仕様名としては古い。rename 後の用語更新候補。
- `scripts/run_pi_player_smoke.py` と `scripts/run_ai_persona_playtest.py` の外部 `gal-sim-testers` fallback は、QA support であっても名前の印象が強い。現行 `personas/` へ寄せる候補。
- `prompt/style_bridge.md` が TODO 上に残りつつ、実際の style 方針は `GALGE.md` と `style/reference.md` / `style/rules.md` に分散している。これは旧名というより責務名の整理候補。

## 思想の名残リスク

- 高危険度の旧思想残骸は見当たらない。具体的には、ヒロインが攻略報酬化している箇所、AFFINITY が身体的親密さの自動解禁条件になっている箇所、ハーレム構築が主目的化している箇所、能力無双や戦闘勝利報酬を主軸化している箇所、異世界・魔王討伐を標準化している箇所は確認できなかった。
- 中程度のリスクは active style layer にある。`style/reference.md` は冒険 RPG / 敵攻略 / ダンジョン / 技進化の発想を文体・episode algorithm として持ち込みうる。`style/rules.md` はヒロイン類型と身体描写テンプレートが強く、現在の「生活・事件・関係性・インナー変化」より旧ギャルシム的な人物消費に寄る可能性がある。
- `prompt/runtime.md` の例示は、現代 LIRIA の方針文よりも古い冒険 / ランダムイベントの匂いが残る。モデルは例示に引っ張られやすいため、禁止語ではなく生成誘導としてのリスクがある。
- AFFINITY 周辺は基本的に現行方針へ整理されている。`prompt/romance.md` は自動報酬・自動解禁を否定している。ただし、`GALGE.md` や style defaults の scene style mapping は「描写密度の目安」であり「許可条件」ではないことをさらに明確にすると安全。

## 放置してよい旧語

- `GALGE.md`, `REQUIREMENTS.md`, `CONCEPT.md`, `docs/liria_friend_intro.md`, `docs/maintenance/REQUIREMENTS_AUDIT.md` などで、旧語が「これは目的ではない」「禁止」「REMOVE/ADAPT」として出る箇所。
- `docs/legacy/**` に置かれている cleanup report / prompt split plan。
- `docs/maintenance/core_notes.md` の旧 `CORE.md` 説明。現役正本ではなく保守メモであることが明記されている。
- `personas/*.yaml` の `do_not` や QA 観点としての「雑なハーレム攻略」「攻略ルート」等。これらは避けるべき挙動をテストする目的で使われている。
- `scripts/analyze_play_log.py` の旧語検出。これは生成ログ QA の guard であり、旧思想の採用ではない。
- `references/story_media_stock.md` は参照棚としての抽象化資料であり、旧思想の source of truth ではない。
- `prototypes/market_familiar.md` は別プロジェクト持ち出し用 prototype と明示されているため、現行 LIRIA 正本とは分離されている。

## 次にやるなら

1. rename 候補: `GALGE.md` を `LIRIA.md` へ移行し、`scenarios/liria/config.sh`, `scripts/check_repo_integrity.sh`, README / ARCHITECTURE / TODO / docs 参照を更新する。移行中は旧名の alias または明示的な compatibility note を短期維持する。
2. 保存構造候補: `templates/session/current/harem.md` を `current/relationships.md` または `current/relationship_network.md` へ移行し、prompt / scripts / docs の参照を更新する。既存 save 互換の読み取り fallback は残してよい。
3. 文言修正候補: `style/reference.md` を現行 LIRIA の story reference / style reference として再構成し、冒険 RPG / 敵攻略 / ダンジョン / 技進化を現役 algorithm から外す。
4. 文言修正候補: `style/rules.md` の固定ヒロイン類型・身体テンプレートを、セッション固有の人物性と同意状態に基づく描写方針へ一般化する。
5. 文言修正候補: `prompt/runtime.md` の村・酒場・行商人・野盗・怪異・レアイベント・ラッキースケベ等の例を、現代の生活接点、事件の余波、関係性変化、インナー変化へ差し替える。
6. docs / tool 候補: AI/PI playtest の外部 `gal-sim-testers` fallback を local `personas/` 既定に寄せ、古い外部 tester path を任意指定に下げる。
7. 後回しでよいもの: `docs/legacy/**`、禁止事項としての旧語、`docs/maintenance/core_notes.md`、`references/story_media_stock.md`、`prototypes/market_familiar.md` は急いで触らなくてよい。
