# LIRIA ファイル関係マップ

## このドキュメントの目的

このドキュメントは、LIRIA のフォルダ・ファイル関係を「どこが入口で、何を読み、何を生成し、どこを更新するか」という観点で見るための地図です。

プログラムの細かい実装ではなく、初めて触る人が次の流れを把握できることを目的にしています。

- `play.sh` から起動する
- `scenarios/liria/config.sh` と `prompt/` の内容を読んで GM を起動する
- `templates/session/` から `saves/session_xxx/` を生成する
- 進行中は `saves/session_xxx/current/` や関連フォルダを更新する
- 必要に応じてログ、復旧候補、漫画化・画像化用の出力を扱う

## Mermaid を見る方法

このファイルは Mermaid の `flowchart TD` を使っています。

- VS Code では Markdown Preview Mermaid Support などの Mermaid 対応拡張を入れて、Markdown プレビューを開いてください。
- Obsidian では Mermaid が有効な状態で、この Markdown を開いてください。
- 図が大きい場合は、プレビュー側でズームアウトするか、Obsidian の別ペイン表示で確認すると見やすくなります。

## LIRIA 全体のまとめ図

```mermaid
flowchart TD
    A[ユーザー] --> B[play.sh]
    B --> C{起動モード}

    C -->|new| D[新規開始]
    C -->|resume| E[続きから]
    C -->|list| F[セッション一覧]
    C -->|cleanup| G[不要セッション削除]

    B --> H[scenarios/liria/config.sh]
    H --> I{prompt profile}
    I -->|fast| J[通常prompt]
    I -->|full| K[重いprompt込み]
    I -->|lite| L[軽量prompt]

    J --> M[prompt群を選ぶ]
    K --> M
    L --> M

    M --> M1[LIRIA.md]
    M --> M2[prompt/core.md]
    M --> M3[prompt/gm_policy.md]
    M --> M4[prompt/case_engine.md]
    M --> M5[prompt/runtime.md]
    M --> M6[prompt/combat.md]
    M --> M7[prompt/villain_engine.md]
    M --> M8[prompt/romance.md]
    M --> M9[prompt/save_resume.md]

    D --> N[prompt/core_newgame.md]
    N --> N1[Q0 舞台]
    N --> N2[Q1 生活基盤]
    N --> N3[Q1.5 外見]
    N --> N4[Q2 インナー]
    N --> N5[Q3 能力]
    N --> N6[Q4 恋愛の好み]
    N --> N7[Q5 初期関係]
    N --> N8[Q6 日常の違和感]

    D --> O[session名を決める]
    O --> P[scripts/create_session.sh]
    P --> Q[templates/session]
    Q --> R[saves/session_xxxを生成]

    E --> S[既存sessionを探す]
    S --> T[saves/session_xxxを読む]

    R --> U[CodexまたはClaude起動]
    T --> U
    M1 --> U
    M2 --> U
    M3 --> U
    M4 --> U
    M5 --> U
    M6 --> U
    M7 --> U
    M8 --> U
    M9 --> U
    N --> U

    U --> V[GMが物語を進行]
    V --> W[saves/session_xxxを更新]

    W --> X[current]
    W --> Y[cast]
    W --> Z[design]
    W --> AA[indexes]
    W --> AB[archive]

    X --> X1[player.md]
    X --> X2[gm.md]
    X --> X3[relationships.md]
    X --> X4[case.md]
    X --> X5[hotset.md]
    X --> X6[mechanics_card.md]
    X --> X7[checkpoints]

    Y --> Y1[heroine]
    Y --> Y2[npc]

    Z --> Z1[initial_answers.md]
    Z --> Z2[story_reference.md]
    Z --> Z3[story_spine.md]
    Z --> Z4[organization_cast.md]
    Z --> Z5[villain_design.md]
    Z --> Z6[visual_pipeline.md]
    Z --> Z7[manga_pipeline.md]

    AA --> AA1[cast_index.md]
    AA --> AA2[decision_index.md]
    AA --> AA3[event_index.md]

    AB --> AB1[logs]
    AB --> AB2[events]
    AB --> AB3[chapters]
    AB --> AB4[checkpoints]

    N1 --> Z1
    N2 --> Z1
    N3 --> Z1
    N4 --> Z1
    N5 --> Z1
    N6 --> Z1
    N7 --> Z1
    N8 --> Z1

    N2 --> X1
    N3 --> X1
    N4 --> X1
    N5 --> X1
    N6 --> X3
    N7 --> X3
    N8 --> X4

    N8 --> Z2
    N8 --> Z3
    N8 --> Z4

    X5 --> X1
    X5 --> X2
    X5 --> X3
    X5 --> X4

    AA1 --> Y1
    AA1 --> Y2
    AA2 --> AB2
    AA3 --> AB2

    V --> AC{漫画化や画像化}
    AC -->|必要時| AD[prompt/manga_export.md]
    AC -->|必要時| AE[prompt/visual_character_sheet.md]
    AD --> AF[exports]
    AE --> AF
    X1 --> AF
    Y1 --> AF

    V --> AG{ログ復旧が必要}
    AG -->|生ログ保存| AH[scripts/save_rawlog.sh]
    AH --> AB1
    AG -->|保存候補作成| AI[scripts/extract_newgame_state_candidates.py]
    AB1 --> AI
    AI --> AJ[保存候補md]
    AJ --> X1
    AJ --> X3
    AJ --> X4
    AJ --> X5
    AJ --> Z1
    AJ --> Z2
    AJ --> Z3
    AJ --> Z4

    W --> AK[scripts/check_session_integrity.sh]
    AK --> AL[整合チェック]

    AM[変更したいこと] --> AN{変更対象}
    AN -->|新規開始Q&A| N
    AN -->|保存と再開| M9
    AN -->|GM基本| M2
    AN -->|入力の扱い| M3
    AN -->|事件や依頼| M4
    AN -->|通常進行| M5
    AN -->|能力や危機| M6
    AN -->|敵や組織圧| M7
    AN -->|ヒロイン反応| M8
    AN -->|新規sessionの型| Q
    AN -->|session生成処理| P
    AN -->|整合チェック| AK
```

## 分割版

全体図が大きすぎる場合は、以下の分割図を用途別に見てください。各図は入口、生成、読み込み、保存、変更先を分けて確認できるようにしています。

### 1. 起動フロー

`play.sh` からどの起動モードに進み、どの設定を読んで GM 起動へ進むかを見る図です。

```mermaid
flowchart TD
    S1[ユーザー] --> S2[play.sh]
    S2 --> S3{起動モード}
    S3 -->|new| S4[新規開始]
    S3 -->|resume| S5[続きから]
    S3 -->|list| S6[セッション一覧]
    S3 -->|cleanup| S7[不要セッション削除]
    S2 --> S8[scenarios/liria/config.sh]
    S8 --> S9{prompt profile}
    S9 -->|fast| S10[通常prompt]
    S9 -->|full| S11[重いprompt込み]
    S9 -->|lite| S12[軽量prompt]
    S10 --> S13[prompt群を選ぶ]
    S11 --> S13
    S12 --> S13
    S4 --> S14[CodexまたはClaude起動]
    S5 --> S14
    S13 --> S14
```

### 2. new時の生成フロー

新規開始時に Q&A を読み、session 名を決め、`templates/session/` から `saves/session_xxx/` を作る流れです。

```mermaid
flowchart TD
    N1[新規開始] --> N2[prompt/core_newgame.md]
    N2 --> N3[Q0 舞台]
    N2 --> N4[Q1 生活基盤]
    N2 --> N5[Q1.5 外見]
    N2 --> N6[Q2 インナー]
    N2 --> N7[Q3 能力]
    N2 --> N8[Q4 恋愛の好み]
    N2 --> N9[Q5 初期関係]
    N2 --> N10[Q6 日常の違和感]
    N1 --> N11[session名を決める]
    N11 --> N12[scripts/create_session.sh]
    N12 --> N13[templates/session]
    N13 --> N14[saves/session_xxxを生成]
    N3 --> N15[design/initial_answers.md]
    N4 --> N15
    N5 --> N15
    N6 --> N15
    N7 --> N15
    N8 --> N15
    N9 --> N15
    N10 --> N15
    N4 --> N16[current/player.md]
    N5 --> N16
    N6 --> N16
    N7 --> N16
    N8 --> N17[current/relationships.md]
    N9 --> N17
    N10 --> N18[current/case.md]
```

### 3. resume時の読み込みフロー

既存 session を探し、保存済みの状態を読んで GM 起動へ渡す流れです。

```mermaid
flowchart TD
    R1[続きから] --> R2[既存sessionを探す]
    R2 --> R3[saves/session_xxxを読む]
    R3 --> R4[current]
    R3 --> R5[cast]
    R3 --> R6[design]
    R3 --> R7[indexes]
    R3 --> R8[archive]
    R4 --> R9[player.md]
    R4 --> R10[gm.md]
    R4 --> R11[relationships.md]
    R4 --> R12[case.md]
    R4 --> R13[hotset.md]
    R5 --> R14[heroine]
    R5 --> R15[npc]
    R6 --> R16[story_reference.md]
    R6 --> R17[story_spine.md]
    R7 --> R18[cast_index.md]
    R7 --> R19[decision_index.md]
    R7 --> R20[event_index.md]
    R3 --> R21[CodexまたはClaude起動]
    R21 --> R22[GMが物語を進行]
```

### 4. session内部構造

`saves/session_xxx/` の中で、現在状態、人物、設計、索引、履歴がどこに分かれているかを見る図です。

```mermaid
flowchart TD
    I1[saves/session_xxx] --> I2[session.json]
    I1 --> I3[current]
    I1 --> I4[cast]
    I1 --> I5[design]
    I1 --> I6[indexes]
    I1 --> I7[archive]
    I3 --> I8[player.md]
    I3 --> I9[gm.md]
    I3 --> I10[relationships.md]
    I3 --> I11[case.md]
    I3 --> I12[hotset.md]
    I3 --> I13[mechanics_card.md]
    I3 --> I14[checkpoints]
    I4 --> I15[heroine]
    I4 --> I16[npc]
    I5 --> I17[initial_answers.md]
    I5 --> I18[story_reference.md]
    I5 --> I19[story_spine.md]
    I5 --> I20[organization_cast.md]
    I5 --> I21[villain_design.md]
    I5 --> I22[visual_pipeline.md]
    I5 --> I23[manga_pipeline.md]
    I6 --> I24[cast_index.md]
    I6 --> I25[decision_index.md]
    I6 --> I26[event_index.md]
    I7 --> I27[logs]
    I7 --> I28[events]
    I7 --> I29[chapters]
    I7 --> I30[checkpoints]
```

### 5. promptレイヤ関係

起動設定が prompt 群を選び、各 prompt が GM の振る舞いを担当する関係を見る図です。

```mermaid
flowchart TD
    P1[scenarios/liria/config.sh] --> P2{prompt profile}
    P2 -->|fast| P3[通常prompt]
    P2 -->|full| P4[重いprompt込み]
    P2 -->|lite| P5[軽量prompt]
    P3 --> P6[prompt群を選ぶ]
    P4 --> P6
    P5 --> P6
    P6 --> P7[LIRIA.md]
    P6 --> P8[prompt/core.md]
    P6 --> P9[prompt/gm_policy.md]
    P6 --> P10[prompt/case_engine.md]
    P6 --> P11[prompt/runtime.md]
    P6 --> P12[prompt/combat.md]
    P6 --> P13[prompt/villain_engine.md]
    P6 --> P14[prompt/romance.md]
    P6 --> P15[prompt/save_resume.md]
    P6 --> P16[prompt/core_newgame.md]
    P8 --> P17[GM基本]
    P9 --> P18[入力の扱い]
    P10 --> P19[事件や依頼]
    P11 --> P20[通常進行]
    P12 --> P21[能力や危機]
    P13 --> P22[敵や組織圧]
    P14 --> P23[ヒロイン反応]
    P15 --> P24[保存と再開]
    P16 --> P25[新規開始QA]
```

### 6. 保存・ログ復旧フロー

GM 進行後に session が更新される流れと、生ログから復旧候補を作る流れを見る図です。

```mermaid
flowchart TD
    L1[GMが物語を進行] --> L2[saves/session_xxxを更新]
    L2 --> L3[current]
    L2 --> L4[cast]
    L2 --> L5[design]
    L2 --> L6[indexes]
    L2 --> L7[archive]
    L2 --> L8[scripts/check_session_integrity.sh]
    L8 --> L9[整合チェック]
    L1 --> L10{ログ復旧が必要}
    L10 -->|生ログ保存| L11[scripts/save_rawlog.sh]
    L11 --> L12[archive/logs]
    L10 -->|保存候補作成| L13[scripts/extract_newgame_state_candidates.py]
    L12 --> L13
    L13 --> L14[保存候補md]
    L14 --> L15[current/player.md]
    L14 --> L16[current/relationships.md]
    L14 --> L17[current/case.md]
    L14 --> L18[current/hotset.md]
    L14 --> L19[design/initial_answers.md]
    L14 --> L20[design/story_reference.md]
    L14 --> L21[design/story_spine.md]
    L14 --> L22[design/organization_cast.md]
```

### 7. 変更したい時にどこを触るか

目的別に、最初に確認するファイルやフォルダを探すための図です。

```mermaid
flowchart TD
    C1[変更したいこと] --> C2{変更対象}
    C2 -->|起動方法| C3[play.sh]
    C2 -->|prompt profile| C4[scenarios/liria/config.sh]
    C2 -->|新規開始QA| C5[prompt/core_newgame.md]
    C2 -->|保存と再開| C6[prompt/save_resume.md]
    C2 -->|GM基本| C7[prompt/core.md]
    C2 -->|入力の扱い| C8[prompt/gm_policy.md]
    C2 -->|事件や依頼| C9[prompt/case_engine.md]
    C2 -->|通常進行| C10[prompt/runtime.md]
    C2 -->|能力や危機| C11[prompt/combat.md]
    C2 -->|敵や組織圧| C12[prompt/villain_engine.md]
    C2 -->|ヒロイン反応| C13[prompt/romance.md]
    C2 -->|新規sessionの型| C14[templates/session]
    C2 -->|session生成処理| C15[scripts/create_session.sh]
    C2 -->|整合チェック| C16[scripts/check_session_integrity.sh]
```

## 図の補足説明

図は大きく 5 つの流れに分かれています。

1. 起動入口は `play.sh` です。ユーザーは `new`、`resume`、`list`、`cleanup` のような起動モードを選びます。
2. 起動時に `scenarios/liria/config.sh` が読まれ、`fast`、`full`、`lite` のような prompt profile に応じて読む prompt 群が決まります。
3. 新規開始では `prompt/core_newgame.md` の Q&A を使い、`scripts/create_session.sh` が `templates/session/` を元に `saves/session_xxx/` を作ります。
4. 再開では既存の `saves/session_xxx/` を読み、保存済みの状態から GM を起動します。
5. GM 進行中は `saves/session_xxx/current/`、`cast/`、`design/`、`indexes/`、`archive/` が更新されます。

`current/` は現在のプレイ状態、`cast/` は登場人物、`design/` は設計情報、`indexes/` は参照用の索引、`archive/` は履歴やログを置く場所です。

漫画化や画像化は通常進行とは別の必要時ルートです。`prompt/manga_export.md` や `prompt/visual_character_sheet.md` を使い、`exports/` に出力する流れとして読んでください。

ログ復旧も必要時ルートです。`scripts/save_rawlog.sh` で生ログを残し、復旧候補を作って `current/` や `design/` に反映する流れです。

## 正本・キャッシュ・ログの違い

| 種類 | 主な場所 | 役割 | 変更時の考え方 |
|---|---|---|---|
| 正本 | `prompt/`、`scenarios/liria/config.sh`、`templates/session/` | 起動時に読むルールや、新規 session の雛形 | 仕様を変えたい時に編集する |
| session 正本 | `saves/session_xxx/current/`、`cast/`、`design/` | 現在のプレイ状態、人物、設計情報 | 進行結果として更新される |
| キャッシュ | `current/hotset.md`、`indexes/` | 再開や参照を速くするための要約・索引 | 元の状態やログから再生成できる前提で扱う |
| ログ | `archive/logs/`、`archive/events/`、`archive/chapters/` | 過去の会話、イベント、章の履歴 | 後から復旧・確認するために残す |
| 出力 | `exports/` | 漫画化や画像化など、外部利用向けの成果物 | 本体状態とは分けて扱う |

正本を編集すると、以後の起動や新規 session に影響します。キャッシュや索引は便利な参照用ですが、正本そのものではありません。ログは過去の証跡なので、削除すると復旧や検証が難しくなります。

## 変更したい時にどこを触るか

| 変更したいこと | 主に見る場所 |
|---|---|
| 起動方法やモード分岐を変えたい | `play.sh` |
| LIRIA シナリオの prompt profile を変えたい | `scenarios/liria/config.sh` |
| 新規開始の Q&A を変えたい | `prompt/core_newgame.md` |
| 保存と再開の考え方を変えたい | `prompt/save_resume.md` |
| GM の基本方針を変えたい | `prompt/core.md` |
| 入力の扱いを変えたい | `prompt/gm_policy.md` |
| 事件や依頼の進め方を変えたい | `prompt/case_engine.md` |
| 通常進行のルールを変えたい | `prompt/runtime.md` |
| 能力や危機の扱いを変えたい | `prompt/combat.md` |
| 敵や組織圧を変えたい | `prompt/villain_engine.md` |
| ヒロイン反応を変えたい | `prompt/romance.md` |
| 新規 session の初期ファイル構成を変えたい | `templates/session/` |
| session 生成処理を変えたい | `scripts/create_session.sh` |
| session の整合チェックを変えたい | `scripts/check_session_integrity.sh` |

まず `play.sh` から入口を確認し、次に `scenarios/liria/config.sh` で読む prompt 群を確認すると、どのファイルがどのタイミングで使われるか追いやすくなります。
