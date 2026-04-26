# VALIDATION

## 目的

長編化しても、次が壊れていないかを確認する。

- 口調
- 関係
- 敵勢力
- save / resume
- 複数 session の分離

## 最低限の回帰シナリオ

### 0. LIRIA v1 initial state

確認:

- new session の初期 `current/` が、プレイヤーの内面断定ではなく観測可能な状態から始まる
- `player.md` に現在フェーズ、コンディション、能力使用残回数、Ability Constraint Profile、Equipment / Tools がある
- ヒロインが生成または昇格された場合、`cast/heroine/*.md` に Visual Character Sheet と Heroine Crisis Role の入口がある
- `gm.md` に脅威クロック、Organization Doctrine、contact surface、weak joint の入口がある
- 初回 resume で、危機、関係、探索の入口が混ざり、一本道の攻略指示になっていない
- 初期保存に Manga Export Candidates と Anti-Meta Dialogue の候補を置ける余白がある

### 1. multi-session lifecycle

確認:

- `bash play.sh list-sessions` で既存 session を確認できる
- `bash play.sh new <scenario> <session_name>` または `bash play.sh <scenario> new <session_name>` で任意名の session を作れる
- session 名未指定の new は未使用名を採番し、選んだ session 名を出力する
- 新規 session に `session.json`、`current/`、`cast/`、`design/`、`indexes/`、`archive/` が揃う
- `cast/heroine/` と `cast/npc/` が session 配下にある
- new -> save -> resume が同じ session 配下だけで閉じる
- resume で session 名未指定時は、launcher が選んだ session 名を出力する
- 既存プレイ資産は移行例として扱い、新規 session の初期化元や保存先に固定しない

### 2. cross-session isolation

確認:

- session A で作成 / 更新した cast が session B に現れない
- session B の `current/hotset.md` が session A の再開アンカーを指さない
- rawlog 保存先が指定 session の `archive/logs/` になる
- 同名キャラが別 session にいても、AFFINITY / bond / 呼称 / fixed memory が混ざらない
- repo ルートの legacy cast を live data として読まない
- session 直下 mirror を正本扱いしない

### 3. save -> resume

確認:

- `current/*` を優先して読む
- `hotset` の主役が再開1シーン目に効く
- `hotset` は cache として扱われ、保存時に上書き再生成される
- 再開1シーン目の主役 NPC に session-scoped cast file がある
- 上位存在 / scene lead NPC が出るなら bond に関係なく session-scoped cast file がある
- `gm.md` の知識スコープ台帳を復元してから会話が始まる
- legacy fallback を誤って正本扱いしない

### 4. romance continuity

確認:

- AFFINITY 5 のキャラが急に硬くならない
- 呼称が巻き戻らない
- 事件後に余韻シーンが入る
- hidden 深化ベクトルがキャラごとに違う
- ヒロイン間ベクトルが active ペアだけに絞られている

### 5. villain continuity

確認:

- 勢力は `予兆 -> 下っ端 -> 幹部 -> ボス` の順で出る
- ロマンス中に敵が乱入しない
- ロマンス中に敵が乱入しなくても、外側の脅威クロックや状況変化は止まっていない
- 敵が実害か後遺症を残す
- `gm.md` の勢力クロックに「直近の変動」があり、個別脅威クロックと繋がっている
- ランダムイベントの発火率が、能力使用後に下がるような矛盾になっていない
- active な脅威クロックが 2 以上ある章で、`hotset` や `gm.md` に直接圧候補が 0 本のままになっていない
- 直接圧が「報告だけ」「電話だけ」「書類だけ」で代用されていない
- 組織ごとに Organization Doctrine があり、手口、優先順位、禁じ手が同じ顔になっていない
- contact surface が、受付、仲介者、協力企業、噂、現場担当など具体的な接点として見える
- weak joint が、内部分裂、手続きの穴、依存先、信用の弱さなど攻略以外の形でも使える
- 敵組織の圧が、討伐対象ではなく、交渉、逃走、暴露、保護、切断、潜伏の選択肢を生む
- 迷いやすい判断点で選択補助を出す場合、`1-3` の自然な候補と `4. 自由入力` になっており、正解/成功/好意/真相を保証していない
- 通常会話、余韻、flow scene で毎ターン番号つき選択肢を出していない

### 6. world autonomy / exploration

確認:

- プレイヤーが触らなかったフックが、1-3シーン以内に何らかの事実変化として返ってくる
- その変化が敵襲だけに偏っていない
- 1回の探索で `手がかり / 意味 / 使い方 / 核心` が全部同時に開いていない
- `下見` なのに核心回収まで進んでいない
- 能力が探索でちょうど効いた時、ツッコミ・不確定さ・軽い代償のどれかが入っている
- `hotset` や朝の todo が、次の正解ルートの指示書になっていない
- 戦闘がない章でも、追跡、侵入、環境突破、能力の無理押しで HP / コンディション / 残回数のどれかが意味を持って動いている

### 6.5. ability / equipment crisis handling

確認:

- 危機は倒すか倒されるかだけでなく、逃げる、守る、交渉、隠す、耐える、助けを呼ぶ、能力使用の選択で処理される
- Ability Constraint Profile の `できないこと`、代償、痕跡が、成功時にも残る
- Equipment / Tools が万能解決にならず、準備、携行、場所、壊れる可能性の制約を持つ
- 能力と道具が同時に効く時、どちらか片方の価値を消さず、組み合わせの余波が残る
- 失敗や部分成功が、単なる足止めではなく、情報、信用、退路、体力、関係の変化になる

### 7. archive access

確認:

- index から必要なイベントだけ引ける
- archive 未読でも日常会話は始められる
- 過去因子が必要な時だけ archive を掘る
- archive へ送った本文が current に長文ログとして残っていない

### 8. cast voice

確認:

- `cast/heroine/*.md` と `cast/npc/*.md` の fixed memory から声が再現できる
- current 側の echo を読まなくても人格が崩れない
- current 側の echo を読むと、直近の温度だけが足される
- 再登場キャラの「今のデフォルト外見」が巻き戻らない
- 再会キャラを初対面みたいに扱わない
- bond 2 でも再登場するルート鍵 NPC に `cast/npc/*.md` がある
- hidden proper noun を `suspected` や `unknown` のキャラが口にしない
- 日数進行だけで、cast file の年齢ラベルが勝手に更新されない

### 9. visual / manga export

確認:

- Appearance Profile が、服、髪、体格、目立つ癖、直近の乱れを分けて保持している
- Visual Character Sheet が、正面、側面、背面、表情差分、持ち物差分へ展開できる密度を持つ
- Manga Export Candidates が、絵になる瞬間、構図、感情の見え方、台詞の短さを候補化している
- Natural Language Manga Export を求められた時、プレイヤーは自然文で依頼でき、CLI 手順を要求されない
- ヒロインPVや三面図の依頼が、保存済み Appearance Profile / Visual Character Sheet と矛盾しない
- 正確な身長や3サイズ等の `GM-only Body Profile` は、GM相談や非公開資料でのみ使われ、通常本文や公開用プロンプトへ漏れていない

### 10. anti-meta dialogue

確認:

- Anti-Meta Dialogue が、システム都合の説明ではなくキャラの口調で違和感を受け流す
- NPC が hidden state、保存構造、判定都合をメタに断定しない
- プレイヤーの自然文依頼に対し、GM は世界内の言い換えで返し、必要な内部処理だけを裏で行う
- 同じ拒否や軌道修正が毎回同じ台詞にならない

### 11. PI Player / smoke / pre_compress

確認:

- PI Player smoke が new -> 1 turn -> save -> resume -> pre_compress の流れで通る
- smoke の出力に session-scoped path 以外の live read が混ざらない
- pre_compress 後も hotset、gm、player、harem、cast の入口が欠落しない
- 圧縮後に Appearance Profile、Ability Constraint Profile、Equipment / Tools、Organization Doctrine の要点が消えない
- smoke は本命プレイの代替ではなく、破綻検知の最低線として扱う

## 長編テストの観点

### 5章後想定

- current のフックが 3 本を超えて崩れていない
- 勢力クロックが死に設定になっていない
- `hotset.md` が単一の現在アンカーだけを持っている
- session-scoped cast が必要キャラ分だけ読める

### 10章後想定

- archive に本文が溜まっても再開が重くなりすぎない
- cast ファイルがログ置き場になっていない
- ボスや幹部を同じ顔で連打していない
- `直近の転機候補 / リアルタイム発見` が 0 件のまま数章放置されていない
- `プレイヤー観測メモ（軽量）` が、生ログ化せず 3-5 行で維持されている
- `知識スコープ台帳` が stale のまま数章放置されていない
- AFFINITY 5 ヒロインの hidden 深化ベクトルが空欄のまま長期放置されていない
- active なヒロイン間ベクトルが空欄のまま、同席や共同作戦ばかり増えていない
- 2 シーン以上、active な脅威クロックの章で `combat / 逃走 / 防衛 / 突破` の入口が 0 のまま続いていない

## 壊れやすいポイント

- `current/harem.md` と cast ファイルの AFFINITY 乖離
- `current/player.md` の秘密管理と `current/gm.md` の知識スコープ台帳が食い違う
- `suspected` のキャラが hidden proper noun を断定口調で話す
- 日数カウントの進行だけで年齢ラベルを上げてしまう
- AFFINITY 5 後の関係変化が、毎回同じタグや同じ台詞の反復だけで進んでいる
- ヒロイン同士の関係が、ずっと相性表の一文だけで止まり、現在の scene に反映されない
- `hotset` が古いまま再開主役を誤る
- 主役級の再登場 NPC に cast file がない
- ルート鍵なのに `current/gm.md` の短メモだけで回している bond 2 NPC がいる
- villain 設計はあるのに gm 側クロックが動いていない
- 転機候補やリアルタイム発見を scene で拾ったのに current 側へ残していない
- mirror が stale なのに resume に混ざる
- 別 session の cast が live path に混ざる
- hotset が状況メモではなく、一本道の攻略メモになっている
- 探索で「一回行けば全部わかる」が続く
- 能力が毎回ちょうどよく効き、驚きや摩擦や軽いコストが入らない

## 1回の手動確認で見る順番

1. `docs/validation/INTEGRITY_CHECK.md`
2. `saves/<session_name>/current/hotset.md`
3. `saves/<session_name>/current/gm.md`
4. 対象ヒロイン / NPC の session-scoped cast file
5. 必要なら `saves/<session_name>/design/villain_design.md`
6. 必要なら `saves/<session_name>/archive/*`

## 合格ライン

- new -> save -> resume が session ごとに閉じる
- 再開1シーン目が 1 回で自然に始まる
- 台詞に巻き戻りがない
- 敵圧が世界や関係へ残る
- save 後に次回の入口が見えている
- legacy fallback が main path に混ざらない
