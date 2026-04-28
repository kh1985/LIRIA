# prompt/story_reference

このファイルは LIRIA の Story Reference Layer 正本である。
参照作品の固有名詞、台詞、キャラ、展開を再現するための資料ではない。
使ってよいのは、物語が動く抽象構造だけである。
例文や stock の具体物・職業・導入・台詞は構造理解用であり、本文へコピーしない。

重要:
ここにある Reference Engine は、固定の漫画リストではない。
会話中にユーザーが挙げた作品名は、あくまで「こういう構造が欲しい」という例・方向性ヒントとして扱う。
それらの作品を LIRIA の正本参照元として固定してはいけない。

## 目的

LIRIA は一本道シナリオではなく、自由入力TRPGを基点にした恋愛シミュレーションである。
ただし、組織や事件が完全に即興だけで動くと、敵や関係者が抽象語を喋るだけの霧になりやすい。

Story Reference Layer は、以下を防ぐために使う。

- 何の話か分からない
- 敵組織が理念だけで人物が薄い
- 主要NPCが意味深なことだけ言う
- ヒロインと事件が分離する
- プレイヤーが別行動した時に世界側が止まる

## 参照の禁止事項

- 作品の固有名詞を本文へ持ち込まない
- キャラクター、名場面、台詞、設定を再現しない
- 展開の順番をそのまま使わない
- 参照元をプレイヤーに説明しない
- `これは〇〇っぽい話` と本文で言わない

## 参照元の扱い

参照元は、次の3種類に分けて扱う。

1. `default stock`
   - このファイルに最初からある Reference Engine。
   - すぐ使える初期カードであり、固定作品リストではない。
2. `user hint`
   - ユーザーが会話中に挙げた作品、ジャンル、好み、嫌いな展開。
   - 正本化せず、抽象構造だけを一時的に取り出す。
3. `session-derived`
   - 新規開始Q&A、実プレイログ、ヒロイン、組織、舞台から、その session 用に作る一時エンジン。
   - 既存ストックに合わない時は、こちらを作ってよい。

GMは、ユーザーが「今回はこの作品群を参考にして」と明示しない限り、特定作品を固定参照元として扱わない。
必要なのは「どの漫画か」ではなく、「その session に必要な物語構造は何か」である。

## 参照の使い方

1. プレイヤーの Q&A、生活基盤、インナー、能力、恋愛好み、最初の日常の揺れを見る。
2. `Reference Selection Policy` で Q&A をタグ化する。
3. `references/story_media_stock.md` は必要時だけ参照し、候補を 3-5 個に絞る。
4. 候補から Reference Engine または session-derived engine を 1-3 個だけ選ぶ。
5. 固有設定を捨て、LIRIA の現代社会、生活、恋愛、能力、関係組織へ変換する。
6. `design/story_reference.md` に採用理由を短く保存する。
7. `design/story_spine.md` に Main Question と Reveal Ladder を作る。

具体物、出来事、職業、最初の接触は、新規開始Q&A、主人公の生活、ヒロインの日常、能力、恋愛の好みから卓ごとに再生成する。

## Reference Selection Policy

作品候補を選ぶ時は、作品名からではなく、Q&A と実ログから `selection signals` を作る。

### Step 1: Signals

次の信号を拾う。
ここに並ぶ語は selection signal であり、事件の小物カタログではない。採用時は必ず Q&A と現在卓の生活へ再翻訳する。

- `romance / sweetness`
  - 正妻感、同居、嫉妬、独占欲、秘密、視線、沈黙、未遂、身分差、 forbidden love、大人の女、官能、帰る場所
- `life / base`
  - 店、事務所、家業、職場、近所、通勤路、家、食事、生活費、評判、客
- `institution / record`
  - 役所、病院、会社、学校、警察、契約、監査、本人確認、口座、ID、ログ、音声、映像、紹介状
- `organization / ideology`
  - NPO、財団、公安、研究会、自治会、企業、治安、保護、効率化、地域浄化、能力者管理
- `ability / rule`
  - 強い能力、条件、代償、痕跡、クールダウン、観測者、記録改ざん、本人性、触れてはいけない物
- `place / inherited wound`
  - 土地、旅先、古い店、先代、家族、昔の約束、手紙、鍵、地域の噂、閉じた共同体
- `inner / recovery`
  - 孤独、喪失、自己嫌悪、執着、帰る場所、救われたい/救いたい、壊れた日常
- `media / social gaze`
  - SNS、配信、報道、炎上、噂、人気商売、芸能、情報屋、観客

### Step 2: Candidate Shortlist

`references/story_media_stock.md` を見る場合でも、50作品全部を読むな。
Quick Selection Guide と上の signals から、候補を 3-5 個だけ選べ。

候補化の優先順位:

1. LIRIA は恋愛シミュレーションなので、`romance / sweetness` が強い場合はロマンス系候補を最低 1 個入れる。
2. 事件や組織がある場合は、pressure 系候補を 1 個入れる。
3. 能力が強い場合は、ability / rule 系候補を 1 個入れる。
4. 拠点や土地が強い場合は、life / place 系候補を 1 個入れる。
5. 同じ作者・同じ構造に寄りすぎる候補を複数入れない。似た候補は 1 個へ圧縮する。

候補ごとに、次を短く見る。

- positive signal: なぜ今のQ&Aに合うか
- negative signal: なぜ合わない可能性があるか
- romance compatibility: 恋愛/ヒロイン/生活へ接続できるか
- copy-risk: 固有名詞、名場面、能力名を引っ張りそうな危険はあるか

### Step 3: Selection

候補から採用する engine は 1-3 個まで。

推奨配分:

- romance engine: 0-1 個。恋愛信号が強い時は必須。
- pressure engine: 1 個。事件や組織を霧にしないための外圧。
- texture / scene engine: 0-1 個。拠点、旅先、土地、生活感、文体の厚み。

`romance floor`:
LIRIA は恋愛シミュレーションである。
制度、組織、能力、事件の信号が強い時でも、恋愛と生活を押し潰すな。
候補が事件系に偏った場合は、必ず次のどれかを選定理由へ混ぜる。

- ヒロインが何を守り、何に怯え、何を言えないのか
- 主人公との約束、帰る場所、共同生活、嫉妬、身体距離へどう接続するか
- 事件後に二人の空気がどう変わるか

採用しない候補も、なぜ落としたかを `Rejected / Avoided Engines` に短く残すと、次のGMが迷いにくい。

### Step 4: Conversion

候補作品をそのまま使わず、次へ変換する。

- romance source -> 視線、沈黙、嫉妬、約束、身体距離、帰る場所
- institution source -> 照会、記録、手続き、窓口、契約、紹介停止
- organization source -> 理念、接触面、主要人物、内部矛盾、弱い継ぎ目
- ability source -> 条件、代償、痕跡、誤解、関係リスク
- place source -> 店、道、土地、気候、食べ物、古い物、地域の噂

抽象 engine は、選んだ時点で `design/story_spine.md` の Concrete Story Arc へ短く具体化する。
全文プロットや台詞は作らず、core truth / end choice はプレイヤー向け本文へ露出しない。

- abstract theme -> core truth
- relationship structure -> NPC intent
- suspense structure -> clue chain
- reversal structure -> midpoint reveal
- ethical conflict -> end choice

### Step 5: Save

`design/story_reference.md` には、次を保存する。

- selection signals
- candidate shortlist
- selected engines
- rejected / avoided engines
- LIRIA conversion notes

作品名や stock id は内部監査用に短く残してもよいが、本文やNPC台詞には絶対に出すな。
作品名を保存する場合も、`source hint` として扱い、正本設定にしない。

### Step 6: Concrete Handoff

選んだ engine は、保存して終わりにしない。
必ず次へ渡す。

- `design/story_spine.md`
  - `Main Question`
  - `Reveal Ladder`
  - `Pressure Direction`
  - `Heroine Tie`
  - `if ignored`
- `design/organization_cast.md`
  - 組織が出るなら、最初から主要NPC候補を 3-5 人作る
  - 役職だけでなく、欲しいもの、信じている理念、矛盾、話し方、何を知っているかを持たせる
  - 画面に出た時点で「灰色の男」のような抽象語だけの人物にしない
- `current/case.md`
  - 最初に触れる物、人、場所、記録、関係、能力使用の入口へ落とす
  - 事件名だけ、組織名だけ、理念だけで始めない

## Reference Engine Stock

これは初期ストックである。
この5つに限定しない。
新規開始Q&Aや実プレイログから、より適切な構造が見えた場合は、session-derived engine を作ってよい。
作品候補の研究棚は `references/story_media_stock.md` に置く。
これは毎回読み込む prompt ではなく、必要時に 1-3 個だけ抽象化して使うための外部カタログである。
以下の stock は例の具体語を流用せず、life-first / heroine-first に変換して使え。

### Institution Secret Engine

参考構造:
国家、軍、研究、行政、病院、企業監査など、公的・準公的な制度の奥に真相が埋まっている。

LIRIA変換:
役所、病院、学校、会社、警察、管理会社、委託先、相談窓口、記録保全、本人確認、福祉制度、研究委託。

効く時:

- Q6 が社会の窓口、仕事、信用、記録のズレに寄っている
- 主人公の生活基盤が職場、事業、行政手続き、相談業に接続している
- ヒロインが職務、資格、家族、過去の記録で縛られている

作るべき圧:

- ヒロインの仕事、資格、通院、家族、住まいが止まりかける
- 主人公の信用、事業、紹介、生活手続きに確認が入る
- 通常窓口では解けない記録や担当者の食い違いが出る

### Inherited Wound Engine

参考構造:
長い因縁、継承、喪失、愛憎、親世代や創設者の傷が現在へ届く。

LIRIA変換:
家業、古い店、土地、閉じた地域、元恋人、家族の約束、消えた記録、昔の事件、師弟、先代からの負債。

効く時:

- Q1 が拠点、家業、地域、古い縁を持つ
- Q2 に喪失、執着、帰る場所、守りたいものがある
- ヒロインが過去を隠している

作るべき圧:

- ヒロインや主人公が継がなかった役目、場所、約束が生活へ戻ってくる
- 家族、先代、地域の知人が、現在の関係や恋愛距離を揺らす
- 土地や店の記憶が、今の居場所と選択を問う

### Ideological Organization Engine

参考構造:
組織の大義、政治、革命、秩序、保護、効率と、個人の感情や恋愛が衝突する。

LIRIA変換:
治安維持、能力者保護、効率化、地域浄化、医療安全、企業コンプライアンス、自治会、NPO、研究倫理。

効く時:

- 組織が悪役一枚ではなく、筋の通った理念を持つ必要がある
- プレイヤーが社会へ積極的に介入しそう
- ヒロインが組織側/反組織側/中間の立場を持つ

作るべき圧:

- 正しいことをしているつもりの担当者
- 切り捨てられる少数
- 組織内の良心
- 外部協力者
- 大義と生活の衝突

### Rule-Bound Encounter Engine

参考構造:
能力や異常に明確なルールがあり、敵や接触者がそのルールで場を支配する。

LIRIA変換:
能力の発動条件、記録改ざんの条件、本人確認の穴、契約の条文、病院/会社/学校の運用ルール、SNSや物流の仕様。

効く時:

- 主人公の能力が強い
- 敵の能力や手続きが抽象化しやすい
- 危機をバトルではなく、条件読みと機転で動かしたい

作るべき圧:

- 条件
- 例外
- クールダウン
- 観測者
- ヒロインが守る日常にだけ出る禁止条件
- 破ると残る痕跡

### Charismatic Contact Engine

参考構造:
巨大組織そのものより、濃い主要人物、刺客的な担当者、紹介者、中心人物の引力で場面が動く。

LIRIA変換:
現場担当、交渉役、情報屋、店主、相談員、医師、元公安、地域の顔役、SNS運営者、ヒロインの近しい人物。

効く時:

- 組織を出しすぎるとプレイヤーが無力に感じる
- 重要NPCをヒロイン級に濃くしたい
- プレイヤーが人物への興味で動く

作るべき圧:

- 一人の濃い担当者
- 個人的な癖
- 守りたい人
- 口調のルール
- 交渉できる一点
- 露見すると崩れる弱み

## Story Spine への変換

Reference Engine を選んだら、必ず次の形へ落とす。

```text
Main Question:
この話は、主人公とヒロインに何を問うのか。

Reveal Ladder:
真相や組織の輪郭が見える段階。3-6段階でよい。

Pressure Direction:
プレイヤーが無視した時、組織や世界側が何を進めるか。

Heroine Tie:
ヒロインの生活、秘密、仕事、身体感覚、恋愛感情のどこへ刺さるか。

End Choice Seeds:
終盤で選びうる天秤。固定エンドではなく、選択候補の種。
```

## 運用原則

- Reference Engine は 1-3 個まで。盛りすぎると散る。
- Stock 外の engine を作る時も、必ず抽象構造として書く。作品名、キャラ名、名場面を保存しない。
- ユーザーが例として出した作品を、固定の参照元リストに格上げしない。
- `story_spine.md` は短く保つ。長編プロット表にしない。
- プレイヤーが無視、遠出、脱線しても、Pressure Direction だけは裏で進めてよい。
- ただし、プレイヤーの選択を無効化するために使うな。世界側が動いた結果として見せろ。
- ヒロインの自律性を必ず含めろ。事件だけが進んで恋愛が止まるなら、Story Spine として失敗である。

## Session-Derived Engine Template

既存 Stock だけでは合わない時は、次の形で session 用エンジンを作る。

```text
### [engine name]

source type:
default stock / user hint / session-derived

abstract structure:
何が物語を動かす構造か。

why it fits this session:
Q&A、主人公、ヒロイン、生活導線、最初の揺れのどこに合うか。

LIRIA conversion:
現代社会、恋愛、生活、能力、関係組織へどう変換するか。

do not imitate:
真似してはいけない固有要素、具体物、職業、導入、展開、キャラ、台詞。
```
