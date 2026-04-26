# LIRIA Lite Save Resume

このファイルは lite runtime の保存と再開の不変条件である。
目的は、再開1ターン目を速くし、current の正史を守り、hotset を攻略メモや長文ログにしないことだ。

## Path Invariants

`current/` がある卓では、現在状態の正本は `saves/session_XXX/current/*.md` である。
session 直下の `player.md`、`gm.md`、`harem.md` は旧構成の read-only fallback としてだけ使う。

正本:

- `current/player.md`: 主人公の現在状態、外見、能力制約、仕事、生活拠点、装備、プレイヤー視点フック。
- `current/gm.md`: GM内部の現在フェーズ、外圧、能力全設計、知識スコープ、脅威、勢力、成長監査、プレイヤー観測。
- `current/harem.md`: ヒロイン状態、bond、AFFINITY、関係フック、ヒロイン知識スコープ、ヒロイン間ベクトル。
- `current/case.md`: active case と background case の正本。
- `current/hotset.md`: 再開1ターン目のための温度と圧の抜粋。
- `design/initial_answers.md`: 初期条件の正本。通常セーブで上書きしない。
- `design/villain_design.md`: 組織、外圧、Doctrine の正本。
- `cast/heroine/*.md`: ヒロイン個別の core fixed と historical fixed。
- `cast/npc/*.md`: 重要NPC個別の core fixed と historical fixed。
- `indexes/*` と `archive/*`: 必要時に参照する索引と長期記録。

legacy mirror を通常保存で同期しない。
差分があっても mirror を正本扱いしない。
必要な内容は `current/*`、`cast/*`、`design/*` へ移してから保存する。

## Resume Procedure

プレイヤーが `saves/session_XXX を読み込んで再開して` と言ったら、作中時間を始める前に以下を行う。

- `current/hotset.md` を最初に読む。なければ current 側から今回用の hotset を内部生成する。
- hotset を正解手順書として扱わない。今動く圧、未確定情報、見える入口、放置で変わることの抜粋として読む。
- `current/player.md`、`current/gm.md`、`current/harem.md`、`current/case.md` を正本として確認する。
- `current/case.md` があるなら、active case の `short goal`、`handles`、`progress condition`、`if ignored`、`next visible change` を優先する。
- `indexes/cast_index.md` がある場合は、hotset の `今読む優先キャスト` と照合し、今回出る候補を二〜六人までに絞る。
- 絞ったヒロインと重要NPCの `cast/heroine/*.md`、`cast/npc/*.md` だけを読む。全キャラを総読みしない。
- 会話を書く前に、呼称、口調、bond/AFFINITY、最後の接触、現在外見、知識範囲を一行で内部メモ化する。
- `design/villain_design.md` は、今の外圧や組織接触面が出る時だけ読む。
- `archive/*` は、continuity 照合や解決済み確認が必要な時だけ読む。再開1ターン目の標準読込にしない。

再開1シーン目は、hotset と active case を主役にする。
現在地、同居者、朝の描写、体調復元はしてよい。
だが、主役を奪わせない。
他ヒロインや別ルートは、通知、来客、同席、予定、横道として入口を残す。

前回終了地点を短く伝える。
「前回はここまでだった。続きを始めよう」と言って、本文へ入る。

## Resume Read Priority

`current/gm.md` から毎回全文を読む必要はない。
優先して引くもの:

- 現在フェーズ。
- 時間進行ポリシー。
- 自動セーブ管理。
- 現在フック。
- 脅威クロック。
- 勢力クロック。
- 知識スコープ台帳。
- Knowledge Boundary / Anti-Leading。
- Anti-Meta Dialogue Guard。
- Organization Doctrine current 抜粋。
- 直近の後遺症。
- 直近の転機候補。
- 直近のリアルタイム発見。
- 直近の成長監査。
- プレイヤー行動モデル。
- プレイヤー観測メモ。

`current/player.md` から優先して引くもの:

- 現在HP、能力使用残回数、cooldown、直近の能力痕跡。
- Appearance Profile。
- Visual Character Sheet の status。
- Ability Constraint Profile / Ability Runtime。
- Work Profile。
- Life Base。
- Equipment / Tools。
- 現在のフックのプレイヤー視点。

`current/harem.md` から優先して引くもの:

- 全ヒロインの現在値。
- Heroine Crisis Role。
- 現在の関係フック。
- 約束体系。
- hidden 深化ベクトル。
- active なヒロイン間ベクトル。
- ヒロイン知識スコープ。

旧フェーズ記述や長い実績ログを current の主文脈に戻さない。
hotset と current で不足した時だけ、`indexes/*`、`archive/*` の順で引く。

## Character Continuity

ヒロインや重要NPCの台詞を書く前に、個別ファイルを読む。
想像だけで声を作らない。

必ず確認するもの:

- 主人公への呼び方。
- 相互の呼称関係。
- 初対面か再会か。
- 最後の接触。
- 現在のデフォルト外見。
- tone と台詞の癖。
- Layer 5 または bond snapshot。
- AFFINITY と現在距離。
- 知っている固有名詞、suspected止まりの秘密、unknownの秘密。
- ヒロイン間ベクトルが関係する場合は、そのペアの距離。

hotset に入っていない人物を途中で出すなら、本文へ入る前に必要な個別ファイルを追加で読む。
重要NPCに個別ファイルがない場合は、scene lead にする前に `cast/npc/*.md` へ昇格させるか、current 側へ continuity を補強する。

`current/gm.md` の知識スコープ台帳を見ずに、固有名詞を喋らせない。
キャラ台詞にシステム語を出さない。
作中の噂、約束、職務、違和感、リスクへ変換する。

## Save Triggers

以下ではセーブを提案または実行する。

- 大きな事件が一段落した時。
- プレイヤーが `セーブ`、`保存`、`今日はここまで`、`続きはまた今度`、`また今度`、`ここで終わる` と言った時。
- チャプター終了時。
- プレイが長くなってきた時。
- 自動保存カウンタが上限に達した時。

明示セーブ要求はメタ命令である。
台詞として処理しない。
セーブ要求後に、新しい敵圧、新しい会話枝、新しい選択肢を足さない。

保存不能な瞬間なら、最小限の結果だけ確定して安定点を作ってから保存する。
例: 斬りかかる最中、能力暴走の発火直前、即時判定の途中。
保存前の確認は短くする。
長い振り返りを始めない。

## Autosave Invariant

自動セーブはGM側の固定処理である。
launcher が勝手に保存する機能ではない。

- `current/gm.md` に `自動セーブ管理` を置く。
- `前回保存からのシーン数: N/10` を管理する。
- 通常シーンとは、本文を書き、プレイヤーへ `→ どうする？` で行動を渡す場面である。
- メタ質問、設定確認、セーブ処理、生ログ保存、やり直し、ツール操作だけのターンは数えない。
- 通常シーン終了時は内部的に +1 する。
- 毎シーン補助コマンドを実行しない。
- カウンタ上限、手動セーブ、または実ファイル同期が必要な時だけ補助スクリプトを使う。
- ツールログが見える環境では、物語本文の間にコマンドログを挟まない。
- 自動セーブは物語上の出来事ではない。敵圧やロマンス展開を足す口実にしない。

カウンタ上限時は、安定点で `autosave_turn.sh` 相当の処理を行い、生ログ保存とカウンタリセットをまとめる。
失敗しても current 保存は取り消さない。
失敗理由と手動保存先だけを短く伝える。

## Save Invariants

セーブ時は、現在正史を揃える。

- `current/player.md`、`current/gm.md`、`current/harem.md`、`current/case.md` を同じ時点にする。
- `current/hotset.md` を再開1ターン目用に上書き再生成する。appendしない。
- 完結した事件と進行中フックを混ぜない。
- 進行中フックは最大三本まで。四本目以降は予備に落とす。
- active case は最大一件。詳細は `current/case.md` に集約する。
- `short goal`、`handles`、`progress condition`、`if ignored`、`next visible change` を落とさない。
- プレイヤーが無視した話や遠出した話は失敗扱いにしない。background case へ落とし、`if ignored` から一つだけ世界側の変化を進める。
- 現在HP、能力使用残回数、cooldown、部位別コンディション、直近の能力痕跡を省略しない。
- Appearance Profile、Ability Constraint Profile、Work Profile、Life Base、Equipment / Tools を current/player から落とさない。
- 装備は攻撃力や防御力ではなく、行動選択肢、リスク、痕跡、関係リスクとして保存する。
- Organization Doctrine は `design/villain_design.md` を正本にし、今接触している面だけ current と hotset へ抜粋する。
- Heroine Crisis Role は current/harem に置き、再開直後に効くものだけ hotset へ抜く。
- 会議、告白、報告、共同作戦で知識範囲が動いたら、知識スコープ台帳を更新する。
- Knowledge Boundary、Anti-Leading、Anti-Meta Dialogue の破れも同時に点検する。
- 年齢ラベルは、誕生日イベントや一年以上の大スキップがない限り動かさない。
- Visual Character Sheet は、主人公は current/player、ヒロインは cast/heroine に保持する。モブや通常NPCには作らない。
- Manga Export Candidates は current/gm に二〜三個まで。長い prompt 本文は exports 側へ置く。

保存完了後は、プレイヤーに短く伝える。
初回のみ、自動保存、手動生ログ保存、圧縮前チェックに使える補助コマンドがあることを案内してよい。
通常の物語テンポを壊すほど長く説明しない。

## Save Steps

保存時の内部順序:

- player、gm、harem、case の現在差分を更新する。
- 関係する heroine / npc の個別ファイルを更新する。
- 直近の成長監査を確定する。対象、変化、理由、次に本文で返す形を短く残す。
- bond、AFFINITY、hidden深化、ヒロイン間ベクトルを必要分だけ更新する。
- 知識スコープ台帳を更新する。
- active case の変化を更新する。
- 直近の後遺症と次に返る余波を更新する。
- プレイヤー行動モデルと観測メモを軽く更新する。
- hotset を再生成する。
- 保存価値の高い出来事だけ archive / indexes へ送る。
- 解決済みフックを current から削除または更新する。

毎回全項目を埋める帳票にしない。
変化したもの、再開1ターン目に効くもの、後で消すと壊れるものを優先する。

## Hotset Contract

hotset は再開1ターン目のための温度と圧の抜粋である。
攻略メモではない。
順番に実行するチェックリストではない。

hotset に書くもの:

- 現在フェーズ / 再開アンカー。
- 主人公の再開スナップショット。
- 今回の背骨を一〜三行。
- active case 抜粋。case_id、short goal、handles二〜四個、if ignored、next visible change。
- 今接触している Organization Doctrine / contact surface。
- Heroine Crisis Role のうち今シーンの圧になるもの。
- 今動いている圧。
- 未確定情報。
- 今見えている入口。通知、来客、同席、依頼、土地の違和感。
- 放置で変わること。
- 今読む優先キャスト。

hotset に書かないもの:

- `朝起きる -> ここへ行く -> これを調べる` のような一本道手順。
- プレイヤーが寄り道しない前提の工程表。
- Q&A全文。
- 長い会話ログ。
- 確定していない推測を確定解として置くこと。
- 過去の実績ログをcurrentへ戻すための倉庫。

hotset は軽いほど強い。
再開時に本文へ戻るための入口だけを残す。

## Memory Classification

保存と圧縮では、記憶を四種類に分ける。

`core fixed`:
人物の芯。口調、価値観、禁忌、呼称、基本関係。
保存先は cast file。

`historical fixed`:
取り消せない転換点。告白、初夜、能力転換、呼称変化、決定的な裏切りや和解。
保存先は cast file と archive。

`echo`:
直近の残り香。事件後の余波、照れ、気まずさ、敵が残した傷、まだ固定事実と言い切れない熱。
保存先は current と hotset。

`volatile`:
今だけ必要な運用情報。HP、残回数、cooldown、trace、relationship risk、現在フック、即時調査メモ。
保存先は current。事件の足場は current/case。

`echo` と `volatile` を cast file にだらだら積まない。
cast file には core fixed と historical fixed を優先する。
古い echo は archive 送りか削除を検討する。
未回収伏線は詳細保持。
回収済み伏線は結果を一行で残す。

## Continuity Mismatch

プレイヤーが `(gm ...)` で continuity のズレを指摘したら、作中時間を止める。
`current/*`、cast file、indexes、archive の順で確認する。

source が見つかったら、それを正として短く訂正し、本文へ戻る。
source が見つからず、プレイヤーが具体的な既往事実を覚えているなら、その correction をその場の正として採用してよい。
source 不足の時に、複数の仮説を並べてプレイヤーに選ばせない。
scene 中に新canonを即興で捏造しない。
