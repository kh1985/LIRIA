# Top Level Cleanup Plan

## 結論

トップレベルには、初見の入口、起動に必要なもの、実行正本、根幹設計だけを残すのがよい。

現状は root 直下に設計文書、監査メモ、計画書、macOS launcher、旧整理レポートが並んでいる。すぐ削除すべき Git 管理対象は見当たらないが、`docs/` 配下へ移すと見通しがよくなる候補は多い。

今回の推奨は以下。

- root に残す: `README.md`, `CONCEPT.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md`, `TODO.md`, `GALGE.md`, `play.sh`, `liria`, `.gitignore`
- docs へ移す候補: `INTEGRITY_CHECK.md`, `MEMORY_MODEL.md`, `VALIDATION.md`, `REQUIREMENTS_AUDIT.md`
- legacy/archive 候補: `CLEANUP_REPORT.md`, `PROMPT_SPLIT_PLAN.md`, `CORE.md`, `起動方法.md`
- 要確認: `choose_scenario.command`, `resume_game.command`, `resume_game_codex.command`, `start_new_game.command`

注意点として、`INTEGRITY_CHECK.md`, `MEMORY_MODEL.md`, `VALIDATION.md` は README / ARCHITECTURE / `scripts/check_session_integrity.sh` から参照されている。移動時は参照更新が必須。

## 現在のトップレベル一覧

`find . -maxdepth 1 -print | sort` の結果。

```text
.
./.claude
./.codex
./.git
./.gitignore
./ARCHITECTURE.md
./CLEANUP_REPORT.md
./CONCEPT.md
./CORE.md
./GALGE.md
./INTEGRITY_CHECK.md
./MEMORY_MODEL.md
./PROMPT_SPLIT_PLAN.md
./README.md
./REQUIREMENTS.md
./REQUIREMENTS_AUDIT.md
./TODO.md
./VALIDATION.md
./choose_scenario.command
./docs
./liria
./personas
./play.sh
./prompt
./prototypes
./references
./resume_game.command
./resume_game_codex.command
./saves
./scenarios
./scripts
./skills
./start_new_game.command
./style
./templates
./tests
./起動方法.md
```

`git ls-files | awk -F/ '{print $1}' | sort | uniq -c` の要約。

```text
root markdown / launcher files: 21
docs: 4
personas: 4
prompt: 17
scripts: 18
style: 8
templates: 25
tests: 3
その他: prototypes 1, references 1, scenarios 1, skills 1, saves 1
```

Git 管理対象の root 直下ファイル。

```text
.gitignore
ARCHITECTURE.md
CLEANUP_REPORT.md
CONCEPT.md
CORE.md
GALGE.md
INTEGRITY_CHECK.md
MEMORY_MODEL.md
PROMPT_SPLIT_PLAN.md
README.md
REQUIREMENTS.md
REQUIREMENTS_AUDIT.md
TODO.md
VALIDATION.md
choose_scenario.command
liria
play.sh
resume_game.command
resume_game_codex.command
start_new_game.command
起動方法.md
```

## トップレベルに残すべきもの

| 対象 | 理由 |
|---|---|
| `.gitignore` | repo 運用上必須 |
| `README.md` | 初見の入口、起動方法、関連文書への導線 |
| `CONCEPT.md` | README 冒頭から参照されるコンセプト整理 |
| `ARCHITECTURE.md` | 実行構成と source of truth の根幹設計。README/TODOから参照あり |
| `REQUIREMENTS.md` | 主要要件。READMEから参照あり |
| `TODO.md` | 開発ロードマップ。README/ARCHITECTUREから参照あり |
| `GALGE.md` | prompt orchestrator。`scenarios/liria/config.sh` と下位runnerから直接参照あり |
| `play.sh` | メイン起動スクリプト |
| `liria` | `play.sh menu` への短い入口 |
| `prompt/` | 実行prompt正本。`scenarios/liria/config.sh` から参照あり |
| `scripts/` | 起動、検証、保存、AI playtest、auditor |
| `templates/` | 新規 session scaffold 正本 |
| `style/` | Style Layer 正本。README/ARCHITECTURE/promptから参照あり |
| `scenarios/` | launcher profile と prompt assembly 設定 |
| `personas/` | AI Persona Playtest / Harness で使用 |
| `tests/` | PI Player と AI Player Harness sample |
| `references/` | story reference 研究棚。README/promptから参照あり |
| `docs/` | 補助文書の収容先として残す |

## docs/ 配下へ移動候補

| 現在 | 移動先案 | 理由 | 移動時に必要な更新 |
|---|---|---|---|
| `INTEGRITY_CHECK.md` | `docs/validation/INTEGRITY_CHECK.md` | save / resume 整合確認の詳細。重要だがroot必須ではない | README, ARCHITECTURE, TODO, `scripts/check_session_integrity.sh` |
| `MEMORY_MODEL.md` | `docs/architecture/MEMORY_MODEL.md` | 記憶モデル詳細。rootよりarchitecture配下が自然 | README, ARCHITECTURE, TODO, `scripts/check_session_integrity.sh` |
| `VALIDATION.md` | `docs/validation/VALIDATION.md` | 回帰確認観点。validation配下が自然 | README, ARCHITECTURE, TODO, `scripts/check_session_integrity.sh` |
| `REQUIREMENTS_AUDIT.md` | `docs/maintenance/REQUIREMENTS_AUDIT.md` | 要件監査メモ。`REQUIREMENTS.md` からリンクすれば十分 | REQUIREMENTS |
| `docs/liria_prompt_auditor.md` | `docs/maintenance/liria_prompt_auditor.md` | 既にdocs内だがmaintenance配下が自然 | docs/maintenance_task_template.md |
| `docs/maintenance_task_template.md` | `docs/maintenance/maintenance_task_template.md` | 保守テンプレ。maintenance配下が自然 | 参照があれば更新 |
| `docs/story_generation_improvement_plan.md` | `docs/planning/story_generation_improvement_plan.md` | 実装済みの改善計画。planning配下が自然 | 参照があれば更新 |
| `docs/liria_friend_intro.md` | `docs/product/liria_friend_intro.md` | 非公開プレビュー紹介文。product/docs配下が自然 | 参照があれば更新 |

## legacy/archive 候補

| 現在 | 移動先案 | 理由 | 補足 |
|---|---|---|---|
| `CLEANUP_REPORT.md` | `docs/legacy/CLEANUP_REPORT.md` | 過去の cleanup 結果。通常運用では読まない | 履歴価値はあるので削除ではなく退避 |
| `PROMPT_SPLIT_PLAN.md` | `docs/legacy/PROMPT_SPLIT_PLAN.md` | prompt分割は主要部分が実装済み。TODO上の履歴参照のみ | 将来 `prompt/style_bridge.md` 判断だけTODOへ残せばroot不要 |
| `CORE.md` | `docs/legacy/CORE.md` または `docs/maintenance/CORE.md` | 実行正本ではなく保守要約。ARCHITECTURE/TODOから参照あり | 残すなら `docs/maintenance/core_notes.md` に改名候補 |
| `起動方法.md` | `docs/legacy/起動方法.md` または `docs/usage/startup.md` | READMEに起動方法が統合済み。日本語ファイル名も扱いづらい | renameするなら `docs/usage/startup.md` が安全 |

## 要確認ファイル

| 対象 | 理由 | 方針 |
|---|---|---|
| `choose_scenario.command` | READMEから未参照だが macOS ダブルクリック運用で便利な可能性 | 使用者確認。残すなら README に「macOS launcher」節を追加 |
| `resume_game.command` | 同上 | 使用者確認 |
| `resume_game_codex.command` | 同上 | 使用者確認 |
| `start_new_game.command` | 同上 | 使用者確認 |
| `prototypes/market_familiar.md` | TODOから参照あり。別軸試作 | root直下ではなく `prototypes/` のままでよい |
| `skills/liria-prompt-auditor/SKILL.md` | Codex skill のローカル資料。通常docsではない | 現状維持 |

## 扱いにくい名前の候補

| 種別 | 対象 | 問題 | 方針 |
|---|---|---|---|
| 日本語ファイル名 | `起動方法.md` | shell / Windows / Codex grep で扱いづらい。`git ls-files` では quoted octal 表示になる場合あり | `docs/usage/startup.md` へ移動/rename候補 |
| 長いpath | `saves/*/archive/logs/*_ai_persona_playtest.md` | 80〜90文字台。Git管理外ログなので問題は小さい | 掃除対象またはローカル保持 |
| 空白入りファイル名 | なし | `find ... -name "* *"` では該当なし | 現状問題なし |
| 同義/重複気味 | `README.md` と `起動方法.md` | 起動説明が重複 | READMEを正にして `起動方法.md` はlegacy/usageへ |
| 同義/重複気味 | `CORE.md` と `GALGE.md` / `prompt/core.md` | `CORE.md` は実行正本ではなく保守要約 | docs/maintenanceかlegacyへ |
| 同義/重複気味 | `PROMPT_SPLIT_PLAN.md` と現行 `prompt/` 構成 | 分割済み計画書 | docs/legacyへ |

## 参照更新が必要そうな箇所

移動候補を実際に動かす場合、以下の参照更新が必要。

| 移動対象 | 参照元 |
|---|---|
| `INTEGRITY_CHECK.md` | `README.md`, `ARCHITECTURE.md`, `TODO.md`, `scripts/check_session_integrity.sh` |
| `MEMORY_MODEL.md` | `README.md`, `ARCHITECTURE.md`, `TODO.md`, `scripts/check_session_integrity.sh` |
| `VALIDATION.md` | `README.md`, `ARCHITECTURE.md`, `TODO.md`, `scripts/check_session_integrity.sh` |
| `REQUIREMENTS_AUDIT.md` | `REQUIREMENTS.md` |
| `PROMPT_SPLIT_PLAN.md` | `TODO.md` |
| `CORE.md` | `ARCHITECTURE.md`, `TODO.md` |
| `起動方法.md` | `CLEANUP_REPORT.md` |
| `docs/liria_prompt_auditor.md` | `docs/maintenance_task_template.md`, `scripts/liria_prompt_auditor.py` の漏れ検知文字列 |

特に `scripts/check_session_integrity.sh` は root の `ARCHITECTURE.md MEMORY_MODEL.md INTEGRITY_CHECK.md VALIDATION.md TODO.md` を直接 `rg` している。docs移動時はスクリプトの検査対象も更新する。

`GALGE.md` と `prompt/*.md` は `scenarios/liria/config.sh` と `scripts/run_ai_persona_playtest.py` に固定pathで並んでいるため、今回は移動候補にしない。

## 理想レイアウト案

```text
LIRIA/
├── .gitignore
├── README.md
├── CONCEPT.md
├── ARCHITECTURE.md
├── REQUIREMENTS.md
├── TODO.md
├── GALGE.md
├── play.sh
├── liria
├── prompt/
├── scripts/
├── templates/
├── style/
├── scenarios/
├── personas/
├── tests/
├── references/
├── prototypes/
└── docs/
    ├── architecture/
    │   └── MEMORY_MODEL.md
    ├── validation/
    │   ├── INTEGRITY_CHECK.md
    │   └── VALIDATION.md
    ├── maintenance/
    │   ├── REQUIREMENTS_AUDIT.md
    │   ├── liria_prompt_auditor.md
    │   └── maintenance_task_template.md
    ├── planning/
    │   └── story_generation_improvement_plan.md
    ├── product/
    │   └── liria_friend_intro.md
    ├── usage/
    │   └── startup.md
    └── legacy/
        ├── CLEANUP_REPORT.md
        ├── CORE.md
        └── PROMPT_SPLIT_PLAN.md
```

macOS launcher を残す場合は root に置くか、`launchers/macos/` を新設する案もある。ただしダブルクリック用途ではroot直下の方が発見しやすい可能性があるため要確認。

## 次回、実際に移動する場合の安全手順

1. `docs/architecture`, `docs/validation`, `docs/maintenance`, `docs/planning`, `docs/product`, `docs/usage`, `docs/legacy` を作る。
2. まず参照が少ない `CLEANUP_REPORT.md`, `PROMPT_SPLIT_PLAN.md`, `起動方法.md` から移動する。
3. `README.md`, `TODO.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md` のリンクを更新する。
4. `scripts/check_session_integrity.sh` のドキュメント検査対象を新pathへ更新する。
5. `docs/liria_prompt_auditor.md` を移す場合は、`docs/maintenance_task_template.md` と `scripts/liria_prompt_auditor.py` の漏れ検知文字列を更新する。
6. `git grep -n "旧ファイル名"` で古いpath参照を確認する。
7. `bash scripts/run_ai_player_harness.sh --help`、`python scripts/liria_prompt_auditor.py --root .`、`bash scripts/check_session_integrity.sh <任意のローカルsession>` など、影響範囲の軽い確認を行う。
8. `git diff --check` を実行する。
9. ひとまとまりで commit する。

## 今回実施しないこと

- ファイル削除はしない。
- ファイル移動はしない。
- rename はしない。
- README / TODO / scripts / prompt は書き換えない。
- この文書以外のファイルは変更しない。
