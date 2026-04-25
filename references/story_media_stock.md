# Story Media Reference Stock

LIRIA 用の作品候補棚。
これは固定参照元リストではなく、物語構造を抽象化するための研究メモである。

## Use Policy

- 作品名、キャラ名、台詞、名場面、展開順を本文へ持ち込まない。
- 使うのは `story engine`, `organization engine`, `romance / life engine`, `crisis engine`, `scene engine` の抽象構造だけ。
- 新規開始Q&Aや実ログに合うものを 1-3 個だけ選び、`design/story_reference.md` に短く変換して保存する。
- 50作品を毎回プロンプトへ読み込まない。トークン効率のため、このファイルは研究棚として扱う。
- ユーザーが作品名を明示した時だけ、その作品を `user hint` として扱う。

## Selection Criteria

- LIRIA の恋愛・生活・事件へ変換しやすい。
- 恋愛シミュレーションとして、視線、沈黙、嫉妬、約束、同居、身分差、秘密、官能の余韻へ変換できる。
- 組織、制度、能力、謎、関係性、内面のどれかに強い構造がある。
- 敵や関係者を「意味深な抽象語」ではなく、濃い人物として出せる。
- 主人公が無視、脱線、遠出をしても、世界側が動く理由を作れる。
- 有名さだけではなく、プレイした時に面白い圧や余韻へ変換できる。

## 50 Candidate Works

### Manga / Anime Core

1. **Fullmetal Alchemist** / manga, anime
   - extract: Institution Secret, family loss, forbidden research, moral cost.
   - use: 行政、研究、病院、企業の奥に真相が埋まる外圧。
   - do not copy: 錬金術、国家名、兄弟構図、固有陰謀。

2. **Monster** / manga, anime
   - extract: Medical guilt, pursued monster, moral responsibility, ordinary Europe-scale dread.
   - use: 医師、相談員、過去の救済が現在の危機になる話。
   - do not copy: 天才殺人鬼、双子、ドイツ舞台。

3. **20th Century Boys** / manga
   - extract: Childhood symbol, cult growth, nostalgia weaponized as conspiracy.
   - use: 昔の遊び、約束、地域記憶が巨大な外圧へ変わる話。
   - do not copy: 友民党、幼少期ノート、終末予言。

4. **Pluto** / manga, anime
   - extract: Robot/personhood grief, investigation through victims, war trauma.
   - use: 能力者や非人間的存在の権利、喪失、調査の静かな重み。
   - do not copy: Astro Boy設定、ロボット刑事、固有キャラ。

5. **Billy Bat** / manga
   - extract: Symbol crossing history, creators manipulated by hidden power.
   - use: 漫画、広告、SNS、都市伝説が組織圧になる話。
   - do not copy: コウモリ記号、歴史事件の展開順。

6. **Death Note** / manga, anime
   - extract: Rule-bound power, cat-and-mouse, public justice persona.
   - use: 強すぎる能力を条件・痕跡・社会的リスクで制御する。
   - do not copy: ノート、死神、L/キラ構図。

7. **Hunter x Hunter** / manga, anime
   - extract: Ability conditions, factions, exam/social gate, dangerous charisma.
   - use: 能力の制約設計、交渉、危機突破の機転。
   - do not copy: 念、ハンター協会、旅団。

8. **JoJo's Bizarre Adventure** / manga, anime
   - extract: Strange rule encounters, flamboyant enemies, situational pressure.
   - use: 1シーンごとに「何がルールか」を読ませる危機。
   - do not copy: スタンド、血統名、ポーズ、固有能力。

9. **Chainsaw Man** / manga, anime
   - extract: Want-driven protagonist, institutional hunters, intimacy and exploitation.
   - use: 欲望、仕事、組織利用、恋愛の危うさを同時に出す。
   - do not copy: 悪魔公安、チェンソー、固有関係。

10. **Jujutsu Kaisen** / manga, anime
   - extract: Curses from human negativity, school/institution, rule-heavy fights.
   - use: インナーや社会の歪みが能力現象化する設定。
   - do not copy: 呪術高専、術式名、宿儺構図。

11. **Dorohedoro** / manga, anime
   - extract: Grotesque city texture, factional magic, found family, casual violence.
   - use: 生活感のある裏社会、敵味方のゆるい反転。
   - do not copy: ホール、魔法使い世界、爬虫類頭。

12. **Golden Kamuy** / manga, anime
   - extract: Treasure map across bodies, regional culture, competing factions, food/life texture.
   - use: 旅先・土地・食・文化情報から事件を濃くする。
   - do not copy: 刺青囚人、北海道金塊、固有民族描写の流用。

13. **Berserk** / manga, anime
   - extract: Trauma bond, ambition, betrayal, demonic pressure as inner wound.
   - use: 執着、守る/壊す、愛憎が巨大外圧へ変わる話。
   - do not copy: 烙印、鷹の団、固有怪物。

14. **Vinland Saga** / manga, anime
   - extract: Revenge to pacifism, historical force, violence cost, chosen life.
   - use: 戦わない選択、暴力の後遺症、生活を選ぶ終盤選択。
   - do not copy: ヴァイキング史実展開、固有人物。

15. **Attack on Titan** / manga, anime
   - extract: Walled society, hidden history, us/them reversal, militarized youth.
   - use: 組織側の正義が反転する大きな外圧。
   - do not copy: 巨人、壁、固有国家構造。

16. **Psycho-Pass** / anime
   - extract: Public safety algorithm, quantified morality, inspector/enforcer tension.
   - use: 行政・AI・能力者管理が恋愛と生活を測る圧。
   - do not copy: シビュラ、ドミネーター、公安局設定。

17. **Ghost in the Shell** / manga, anime, film
   - extract: Identity, cybernetic body, state security, networked self.
   - use: 本人性、記録、身体、意識の境界を扱う事件。
   - do not copy: 公安9課、義体、固有事件。

18. **Akira** / manga, anime film
   - extract: Youth, psychic power, state experimentation, city-scale rupture.
   - use: 能力者の社会管理、都市の噂、暴走の痕跡。
   - do not copy: ネオ東京、AKIRA計画、バイクギャング固有像。

19. **Neon Genesis Evangelion** / anime
   - extract: Institutional apocalypse, child pilots, inner wounds, opaque adults.
   - use: インナーと外圧が同期して世界を揺らす構造。
   - do not copy: エヴァ、使徒、NERV、固有宗教記号。

20. **Cowboy Bebop** / anime
   - extract: episodic cases, cool melancholy, past catching up, found crew.
   - use: 依頼回、過去回、女との距離、余韻重視の章。
   - do not copy: 宇宙賞金稼ぎ、ビバップ号、固有過去。

21. **Puella Magi Madoka Magica** / anime
   - extract: Cute wish system hiding cost, contract, sacrifice, repeated despair.
   - use: 願い・能力・代償・少女/ヒロインの自律性。
   - do not copy: 魔法少女契約、魔女、QB。

22. **Steins;Gate** / visual novel, anime
   - extract: small experiment becomes conspiracy, time alteration cost, intimacy by timelines.
   - use: 些細な能力使用が関係や記録をずらす話。
   - do not copy: Dメール、ラボメン、固有タイムマシン。

23. **Serial Experiments Lain** / anime
   - extract: Network identity, reality bleed, lonely girl and digital society.
   - use: SNS、記録、噂、本人性の崩れ。
   - do not copy: Wired、lain固有像、90sネット演出。

24. **Parasyte** / manga, anime
   - extract: body invasion, coexistence, human/inhuman ethics.
   - use: 体内/同居する異物、ヒロインが怖がる能力の余波。
   - do not copy: 寄生生物、右手相棒。

25. **The Promised Neverland** / manga, anime
   - extract: safe home as prison, children deducing system, caretaker ambiguity.
   - use: 保護施設、寮、相談所、NPOの裏側。
   - do not copy: 農園、鬼、脱出計画。

26. **Land of the Lustrous** / manga, anime
   - extract: identity erosion, beautiful body damage, immortal society, longing.
   - use: 身体変化、自己同一性、守られるほど変わるヒロイン。
   - do not copy: 宝石人、月人。

27. **March Comes in Like a Lion** / manga, anime
   - extract: depression, found family, everyday meals, quiet recovery.
   - use: 事件後の生活回復、恋愛以前の居場所作り。
   - do not copy: 将棋プロ、川本家固有関係。

28. **Nana** / manga, anime
   - extract: love, ambition, cohabitation, jealousy, adult consequences.
   - use: ヒロイン同士、夢、恋愛、同居、選べない感情。
   - do not copy: バンド名、二人のナナ構図。

29. **Ooku: The Inner Chambers** / manga
   - extract: gendered power inversion, palace politics, duty and intimacy.
   - use: 性別役割、制度恋愛、権力の中の親密さ。
   - do not copy: 江戸大奥の固有反転設定。

30. **Yokohama Kaidashi Kikou** / manga
   - extract: slow life after decline, place memory, gentle melancholy.
   - use: 拠点、喫茶店、土地、静かな時間の価値。
   - do not copy: アンドロイド喫茶店、終末風景。

### Film / Drama / Novel / Game Expansion

31. **The Wire** / TV drama
   - extract: institutions as characters, street/police/politics/school/media.
   - use: 組織を「悪の本部」ではなく社会の層として動かす。
   - do not copy: Baltimore固有事件、警察/麻薬組織の展開。

32. **Better Call Saul** / TV drama
   - extract: legal procedure, reputation, small lies becoming fate.
   - use: 主人公の信用、仕事、書類、評判の外圧。
   - do not copy: Saul/Jimmy人物、特定事件。

33. **The Americans** / TV drama
   - extract: secret life, mission vs family, intimacy under cover.
   - use: ヒロインやNPCが言えない役割を抱える関係ドラマ。
   - do not copy: 冷戦スパイ夫婦設定。

34. **Unnatural** / TV drama
   - extract: workplace team, one-case social issue, death revealing life.
   - use: 1話事件を生活・社会・感情に接続する。
   - do not copy: UDIラボ、法医解剖固有設定。

35. **The Lives of Others** / film
   - extract: watcher changed by watched person, state surveillance, conscience.
   - use: 敵側/監視側NPCが主人公やヒロインに揺らぐ。
   - do not copy: 東ドイツ秘密警察、作家監視の固有展開。

36. **Michael Clayton** / film
   - extract: corporate cover-up, fixer, legal pressure, tired conscience.
   - use: 会社・財団・NPOの現実的な揉み消し。
   - do not copy: 法律事務所、農薬企業、固有人物。

37. **In the Mood for Love** / film
   - extract: restrained longing, almost-affair, repeated meetings, erotic absence.
   - use: 触れないのに濃い、視線と沈黙で進む甘美な距離。
   - do not copy: 香港1960年代、不倫隣人設定、固有演出。

38. **Before Sunrise / Before Trilogy** / film
   - extract: walking conversation, time-limited intimacy, memory across years.
   - use: 会話だけで恋が進む、旅先や一夜の濃密な関係。
   - do not copy: ウィーン一夜、列車出会い、固有会話。

39. **Portrait of a Lady on Fire** / film
   - extract: forbidden gaze, portrait as intimacy, delayed touch, remembered love.
   - use: ヒロインを「見る/見られる」ことで恋が深くなる場面。
   - do not copy: 18世紀画家、肖像画依頼、固有終幕。

40. **Rebecca** / novel, film
   - extract: gothic marriage, absent rival, mansion memory, jealousy and inheritance.
   - use: 前の女、屋敷、噂、正妻感と不安を混ぜる恋愛。
   - do not copy: Manderley、前妻名、固有真相。

41. **Jane Eyre** / novel
   - extract: gothic romance, moral self-respect, secret in the house, unequal love.
   - use: 強い女の自尊心、屋敷の秘密、踏み込む恋。
   - do not copy: ロチェスター、屋根裏、固有展開。

42. **Pride and Prejudice** / novel
   - extract: misread character, class pressure, verbal sparring, slow trust.
   - use: 第一印象の誤解、会話の刺し合い、じわじわ惚れる関係。
   - do not copy: Bennet/Darcy、舞踏会、英国階級設定。

43. **Wuthering Heights** / novel
   - extract: obsessive love, revenge, inheritance, place as emotional curse.
   - use: 愛憎、執着、土地、世代をまたぐ恋の傷。
   - do not copy: Heathcliff/Cathy、荒野屋敷、固有家系。

44. **The Handmaiden** / film
   - extract: deception romance, erotic power reversal, inheritance trap.
   - use: 騙し合いから本気へ変わる危険で甘い恋。
   - do not copy: 1930年代朝鮮/日本、詐欺計画、固有反転。

45. **Normal People** / novel, TV
   - extract: class difference, miscommunication, recurring intimacy, young adulthood.
   - use: 何度も近づいて離れる、言えなさが恋をこじらせる関係。
   - do not copy: アイルランド学校/大学、固有カップル。

46. **Never Let Me Go** / novel, film
   - extract: gentle institution horror, youth friendship, love under predetermined fate.
   - use: 残酷な制度を日常と恋愛の静けさで見せる。
   - do not copy: クローン寄宿学校、臓器提供。

47. **Disco Elysium** / game
   - extract: inner voices, politics, failed adult, investigation through self.
   - use: プレイヤーのインナーを行動と会話で露出させる。
   - do not copy: Revachol、スキル人格、主人公設定。

48. **Return of the Obra Dinn** / game
   - extract: reconstructing past from fragments, names/roles/fates as puzzle.
   - use: ログ、写真、証言から事件を再構成する調査。
   - do not copy: 船、懐中時計、死亡場面再生。

49. **Parasite** / film
   - extract: class architecture, house as pressure device, deception and intimacy.
   - use: 拠点、家、仕事、階層差が事件と恋愛を歪ませる。
   - do not copy: 半地下家族、家庭教師侵入。

50. **13 Sentinels: Aegis Rim** / game
   - extract: multiple protagonists, romance fragments, timeline puzzle, looming invasion.
   - use: 複数ヒロイン/NPCの秘密を断片開示する長期構造。
   - do not copy: 巨大ロボ、固有時系列、セクター設定。

## Selection Tags

`prompt/story_reference.md` の `selection signals` から、この棚を見る時の早見表。
作品番号は source hint であり、LIRIA の正本設定ではない。

- romance / sweetness: 28, 29, 37, 38, 39, 40, 41, 42, 43, 44, 45, 50
- life / base: 12, 27, 28, 30, 34, 37, 40, 49
- institution / record: 1, 2, 16, 31, 34, 35, 36, 46, 48
- organization / ideology: 1, 15, 16, 19, 31, 33, 35, 46
- ability / rule: 6, 7, 8, 21, 22, 23, 47, 48, 50
- place / inherited wound: 3, 12, 13, 14, 30, 40, 41, 43
- inner / recovery: 4, 13, 19, 21, 27, 30, 37, 39, 45, 46
- media / social gaze: 5, 6, 9, 16, 23, 31, 35, 36, 49
- charismatic contact / dense NPC: 5, 8, 11, 20, 31, 33, 35, 44

## Quick Selection Guide

- 行政・病院・会社・制度の奥へ潜る: 1, 2, 16, 31, 34, 36, 46
- 古い因縁や土地が効く: 3, 12, 13, 14, 30, 40, 41, 43
- 能力ルールと機転が欲しい: 6, 7, 8, 21, 22, 47, 48
- 組織の大義と個人感情: 1, 15, 16, 19, 31, 35, 46
- 甘美なロマンス、視線、沈黙、余韻: 28, 29, 37, 38, 39, 40, 41, 42, 43, 44, 45
- ヒロイン/関係性を濃くしたい: 9, 20, 27, 28, 29, 33, 37, 39, 44, 45, 50
- 生活感と拠点を濃くしたい: 12, 27, 28, 30, 34, 40, 49
- 敵/関係者を濃い人物で出したい: 5, 8, 11, 20, 31, 35, 44

## Research Sources Used

- Japan Media Arts Festival / Agency for Cultural Affairs
- Wikipedia summaries for factual metadata and high-level premise checks
- BFI / Sight and Sound context for film canon
- GamesRadar and similar current list articles for game/film discovery
- Official or encyclopedia-style pages for notable games and novels
