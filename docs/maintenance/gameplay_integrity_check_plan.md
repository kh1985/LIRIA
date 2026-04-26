# Gameplay Integrity Check Plan

## 結論

LIRIA には、Technical Integrity とは別に Gameplay Integrity の検査軸が必要である。

Technical Integrity は、repo 構造、構文、必須ファイル、リンク、Git 管理外生成物の混入などを見る。これは `scripts/check_repo_integrity.sh` と `scripts/check_session_integrity.sh` がすでに担っている領域である。

Gameplay Integrity は、恋愛、生活、事件、能力、組織圧、Knowledge Boundary、保存、再開、AI Player 検証が、物語本文と session 保存状態の間で連動しているかを見る。ファイルが存在していても、本文に痕跡が出ず、保存にも落ちず、再開にも返らない機能は「浮いている機能」として扱う。

この文書は checker 実装ではない。将来 `check_gameplay_integrity.py` を作るための v0 設計メモであり、最初は WARN / REVIEW 中心で始める。

## Technical Integrity と Gameplay Integrity の違い

Technical Integrity が見るもの:

- ファイルが存在するか
- shell / python 構文が通るか
- README のコマンド対象が実在するか
- `templates/session/` の必須ファイルがあるか
- `.gitignore` 対象が Git 管理に混ざっていないか
- repo 構造、参照、構文が破綻していないか

Gameplay Integrity が見るもの:

- 定義された機能が物語本文に痕跡を出しているか
- 本文で起きた変化が保存先に落ちるか
- 保存された情報が再開時に読まれるか
- 事件、組織、能力、ヒロイン、Knowledge Boundary が連動しているか
- prompt に書いてあるが使われない「浮いた機能」がないか
- プレイ体験上、その機能が意味を持っているか

要するに、Technical Integrity は「壊れていない repo」を見る。Gameplay Integrity は「長編 AI TRPG として続くプレイ」を見る。

## 主要連動チェーン

### 能力使用チェーン

連動:

能力を使う
-> cost / trace / social risk / relationship risk が発生する
-> 本文に痕跡が出る
-> 必要なら組織、NPC、ヒロインが反応する
-> `current/player.md` や `current/gm.md` に残る

合格状態:

能力が便利に効いても、疲労、痕跡、誤解、関係リスク、組織に拾われる可能性などが残る。能力は封じない。ただし、成功した結果が恋愛、生活、事件へ返る。

例:

記録は読めた。ただし端末のログに能力痕跡が残る。相手は安心するが、同時に「これ、誰かに説明できますか」と線を引く。

浮いている状態:

`Ability Constraint Profile` はあるが、能力を使っても疲労も痕跡も関係リスクも出ない。事件が一発解決する。

判定:

WARN 中心。一回便利に効くのは許容する。継続して便利ボタン化するなら問題。

将来の自動化ヒント:

- raw log に能力使用があるか
- 直後に cost / trace / risk / condition / clock に相当する語が出るか
- `current/player.md` の Ability Constraint Profile や condition に変化が残るか
- `current/gm.md` や `current/case.md` に痕跡、誤解、組織反応の入口が残るか

### 事件カードチェーン

連動:

visible problem
-> short goal
-> handles
-> progress condition
-> if ignored
-> next visible change

合格状態:

プレイヤーが「次に何へ触れば進むか」が分かる。物、人、場所、記録、期限、関係者が見えている。事件は抽象的な違和感ではなく、生活上の接点として手に取れる。

例:

visible problem:

- 訪問記録と予約票が同じ 19:20 に揃っている

handles:

- 榎本いおり
- 佐伯の名刺
- タブレット通知
- 明朝九時の家族会議

if ignored:

- 相談者が虚偽申告扱いになり、榎本の守秘違反疑いも強まる

浮いている状態:

事件カードはあるが、本文では「謎」「違和感」「組織の影」ばかりで、触れる物、人、場所、記録がない。

判定:

FAIL 寄りの WARN。事件カードが曖昧だと、プレイヤーが迷子になる。

将来の自動化ヒント:

- `current/case.md` に Active Case があるか
- short goal / handles / progress condition / if ignored があるか
- handles が抽象語だけでなく、人名、物、場所、記録、期限を含むか
- raw log の次 scene に、case card の handles が本文として出るか

### 組織圧チェーン

連動:

Organization Doctrine
-> contact surface
-> 担当者 / 書類 / 通知 / 手続き / 窓口
-> Pressure Clock
-> visible consequence

合格状態:

組織が理念だけでなく、生活に触れる形で出る。担当者、通知、書類、制度、手続き、窓口、期限としてプレイヤーに圧をかける。

例:

組織理念:

- 個人情報保護を盾に、記録の整合性を守る

contact surface:

- 管理会社通知
- 佐伯の名刺
- 郵便受けの警告紙
- 明朝の家族会議

浮いている状態:

`Organization Doctrine` はあるが、本文では「組織が動いている」「配置が良好」などの抽象語だけ。担当者、書類、窓口、手続きが出ない。

判定:

WARN または FAIL。抽象組織は LIRIA の事件を弱くする。

将来の自動化ヒント:

- `design/villain_design.md` や `design/organization_cast.md` に doctrine / contact surface があるか
- `current/gm.md` / `current/case.md` / hotset に現在効いている contact surface があるか
- raw log に通知、書類、担当者、窓口、期限、手続きなどの visible consequence が出るか

### ヒロイン自律チェーン

連動:

Heroine Crisis Role
-> 危機や恋愛で本人が判断する
-> 拒否 / 保留 / 条件提示 / 協力
-> 関係変化
-> `current/harem.md` / `cast/heroine/*.md` に残る

合格状態:

ヒロインが「助けられて惚れる」だけではない。本人の事情、境界線、利害、恐れ、仕事、守りたいものを持っている。恋愛寄りプレイヤーの踏み込みにも、好意確定ではなく本人の判断を返せる。

例:

「私が“全部関わってください”と言えば、あなたは背負ってくれるんですか。私が“ここまで”と言えば、本当にそこで止まれますか。」

浮いている状態:

`Heroine Crisis Role` はあるが、危機では毎回守られるだけ。恋愛では拒否も保留もなく、好意だけが進む。

判定:

FAIL 寄り。LIRIA の核に関わる。

将来の自動化ヒント:

- raw log にヒロインの判断、拒否、保留、条件提示、協力があるか
- `current/harem.md` に関係変化や Heroine Crisis Role の現在運用が残るか
- `cast/heroine/*.md` に fixed memory / tone / boundary / role の更新があるか
- AI Player Harness の romance-first persona で即落ち、同意境界崩れ、好意確定が多発していないか

### Knowledge Boundaryチェーン

連動:

誰が何を見たか
-> 誰が何を知ったか
-> 誰が疑うだけか
-> 誰が知らないままか
-> 台詞・行動に反映

合格状態:

GM 地の文で、必要に応じて 1-3 行だけ自然に境界を整理する。NPC が GM 視点の真相を喋らない。推測と確定知識が分かれている。

例:

分かるのは、ここまでだ。
佐伯の名刺と通知には同じ手順の匂いがある。
榎本は、郵便受けの紙までは知らなかった。
佐伯がこの作業場を見ているかは、まだ分からない。

浮いている状態:

NPC が GM 視点の真相を喋る。知らないはずの固有名詞を出す。推測が確定情報として扱われる。

判定:

FAIL。長編の信用が壊れる。

将来の自動化ヒント:

- raw log に境界整理らしい短い地の文があるか
- `current/gm.md` に Knowledge Boundary / Anti-Meta guardrail があるか
- `current/harem.md` と `current/gm.md` の shared / hidden が矛盾していないか
- 重要 NPC / ヒロイン台詞に未発見の固有名詞、真相、システム語が混ざっていないか

### Save / Resumeチェーン

連動:

本文で起きた変化
-> `current/player.md` / `current/gm.md` / `current/harem.md` / `current/case.md`
-> `cast/`
-> `indexes/` / `archive/`
-> `current/hotset.md`
-> resume で再開 1 シーン目に返る

合格状態:

本文で起きた重要変化が保存に落ちる。再開時に関係、事件、約束、境界線、能力痕跡が巻き戻らない。hotset は正本ではなく、再開用の derived cache として機能する。

例:

榎本が「今夜追わない」という条件を出した
-> `current/case.md` の relationship stake / next visible change に残る
-> hotset に「榎本との約束: 今夜は佐伯を追わない」が残る
-> resume でその境界線が巻き戻らない

浮いている状態:

本文では関係が動いたが、`current/harem.md` や `case.md` に残らない。resume 後に初対面のような距離へ戻る。

判定:

FAIL。長編 AI TRPG として致命傷。

将来の自動化ヒント:

- raw log に Save Notes / 保存候補があるか
- raw log の重要変化が current 側の該当ファイルにあるか
- hotset が current の derived cache として短くまとまっているか
- resume 直後ログに、直前の約束、境界線、事件入口、能力痕跡が返るか

### Manga Exportチェーン

連動:

絵になる場面
-> Manga Export Candidates
-> package 化
-> exports
-> status 更新

合格状態:

本編中で漫画化候補が自然に拾われる。ただし本編 GM が漫画化補助に飲まれない。明示的な漫画化依頼があった場合だけ package / export へ進む。

浮いている状態:

Manga Export Candidates だけ溜まるが、実際の package 導線とつながらない。または本編中に漫画化補助が出すぎて、プレイテンポを壊す。

判定:

WARN / REVIEW。本編破綻より優先度は低い。

将来の自動化ヒント:

- `current/gm.md` の Manga Export Candidates が 2-3 個程度に収まっているか
- packaged / generated の候補が package path と status を持つか
- raw log に漫画化補助の説明が出すぎていないか
- Visual Character Sheet が主人公とヒロインだけを対象にしているか

## 浮いている機能の症状

浮いている機能は、次のどれかとして現れる。

- prompt に項目はあるが、本文に痕跡が出ない
- 本文に痕跡はあるが、保存先に落ちない
- 保存先に落ちるが、resume で読まれない
- current にはあるが、物語上の行動、台詞、選択肢に意味を持たない
- design に理念だけがあり、contact surface がない
- case card に抽象的な謎だけがあり、触れる物、人、場所、記録、期限がない
- ヒロインに role はあるが、本人の拒否、保留、条件提示、協力がない
- Ability Constraint Profile はあるが、能力使用後に cost / trace / risk がない
- Manga Export Candidates はあるが、候補管理か package 化のどちらにもつながらない

Gameplay Integrity の目的は、機能の数を増やすことではなく、機能がプレイ体験内で意味を持っているかを見ることである。

## 判定レベル

OK:

- 連動が確認できる
- 本文、保存先、再開入口が同じ出来事を指している

WARN:

- 機能の痕跡が薄い
- ただし 1 回だけなら許容できる
- 継続観察でよい

REVIEW:

- 面白さ、ヒロインの魅力、関係の温度など、人間判断が必要
- 自動判定で FAIL にしすぎると LIRIA の自由度を削る

FAIL:

- 長編運用を壊す
- Knowledge Boundary 破れ
- 保存巻き戻り
- session 構造破損
- current / cast / design / hotset の矛盾が resume に混ざる

## 自動化してよいもの / 人間レビューに残すもの

自動化してよいもの:

- case card に required fields があるか
- raw log に Save Notes があるか
- Manga Candidates があるか
- Knowledge Boundary らしい整理文があるか
- `current/case.md` に active case があるか
- hotset が長すぎないか
- 保存候補と current 保存先の対応があるか
- `current/player.md` に Ability Constraint Profile があるか
- `current/gm.md` に Knowledge Boundary / Manga Export Candidates があるか
- `current/harem.md` に Heroine Crisis Role があるか

自動化しすぎない方がいいもの:

- このヒロインが魅力的か
- 恋愛の温度が良いか
- 事件が面白いか
- 組織圧がちょうどよいか
- 外見描写が長すぎるか
- 文豪シーンが効いているか
- 余韻が良いか
- プレイヤーの好みに刺さっているか

これらは人間レビューに回す。自動 checker は、面白さの判定ではなく、レビューすべき箇所を見つける補助にする。

## analyze_play_log.sh との違い

`scripts/analyze_play_log.sh`:

- raw log 単体の品質を見る
- LIRIA らしさ、ヒロイン自律性、Knowledge Boundary、保存候補、漫画化候補、選択補助などを見る
- そのログが LIRIA っぽいかを確認する

将来の `check_gameplay_integrity.py`:

- raw log と session 保存状態の連動を見る
- 本文で起きた変化が `current/`, `cast/`, `design/`, `indexes/`, `hotset.md` に保存され、再開時に返るかを見る
- そのログで起きたことが保存・再開に連動しているかを確認する

要するに:

`analyze_play_log.sh`:

- そのログは LIRIA っぽいか

`check_gameplay_integrity.py`:

- そのログで起きたことが保存・再開に連動しているか

AI Player Harness は、persona 別の raw log と analysis report を集める入口である。将来は harness の各結果に gameplay integrity report をぶら下げると、慎重型、恋愛寄り、事件寄りなどの persona 差を保存連動の観点で比較できる。

## 将来の check_gameplay_integrity.py 設計案

今回は実装しない。将来スクリプト化する場合の入力と出力だけ整理する。

入力候補:

- raw log
- analysis report
- session directory
- `current/*.md`
- `cast/*.md`
- `design/*.md`
- `indexes/*.md`
- `current/hotset.md`

出力候補:

- 浮いている機能
- 連動していないチェーン
- 保存漏れ
- resume で返らない情報
- prompt 上はあるが実ログに出ていない機能
- 人間レビューが必要な箇所

将来の最小実装案:

v1:

- raw log + `current/case.md` + `current/hotset.md` を見る
- Save Notes と `current/case.md` の対応を見る
- Knowledge Boundary と Case Card の最低限を WARN で見る

v2:

- `current/harem.md` / `cast/heroine/*.md` まで見る
- ヒロインの境界線、約束、関係変化が保存されているかを見る

v3:

- `design/villain_design.md` / `design/organization_cast.md` まで見る
- Organization Doctrine と contact surface が本文に出ているかを見る

v4:

- AI Player Harness と接続する
- persona 別に gameplay integrity report を出す

実装時の注意:

- 最初から全部を自動 FAIL にしない
- WARN / REVIEW を中心に、手動レビュー対象を見つける
- raw log だけで断定せず、session 保存状態と突き合わせる
- hotset は正本ではなく derived cache として扱う
- AI に save ファイルを直接編集させる前提にしない

## 優先順位

優先 1: Save / Resume チェーン

- 長編なので、巻き戻りが一番怖い
- 本文で動いた関係、事件、約束、能力痕跡が current / hotset に落ちるかを見る

優先 2: Case Card チェーン

- 事件が迷子になるとプレイが止まる
- visible problem / handles / progress condition / if ignored / next visible change を見る

優先 3: Knowledge Boundary チェーン

- すでに改善済みだが、今後も重要
- 長編の信用を守るため FAIL 判定に近い

優先 4: Heroine Autonomy チェーン

- 恋愛ゲームとしての生命線
- romance-first persona で破綻しやすい

優先 5: Ability / Organization チェーン

- 強くなるほど重要
- 初期段階では WARN 中心でよい

優先 6: Manga Export チェーン

- 便利だが、本編破綻より優先度は低い
- REVIEW と candidate 管理から始める

## 次にやるなら

1. `scripts/check_gameplay_integrity.py` v1 の入力仕様を決める
2. raw log + `current/case.md` + `current/hotset.md` の最小突き合わせを実装する
3. `Save / Resume`, `Case Card`, `Knowledge Boundary` の WARN を出す
4. `scripts/run_ai_player_harness.py` の report から raw log / analysis / session を拾えるようにする
5. 人間レビュー用の report format を決める

### 次回追記するなら

- README の補助コマンドに、将来 `bash scripts/check_gameplay_integrity.py ...` を載せる可能性がある
- TODO の Current Phase に、Gameplay Integrity v1 実装を追加する可能性がある
