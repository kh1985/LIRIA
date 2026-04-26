# Story Generation Improvement Plan

This memo captures the discussion about why the current new-game and mid-story flow can become vague, and what should be improved before editing prompts.

## Implementation Status

Status: implemented in prompt/session templates.

- Q6 was made more concrete in `prompt/core_newgame.md`.
- `visible request` was added to `prompt/case_engine.md`, `templates/session/current/case.md`, and Q6/session seed guidance.
- `Truth Hiding Boundary` was added to `prompt/gm_policy.md`.
- `Mid-Story Activation Gate` was added to `prompt/runtime.md`.
- `Organization Relation Ledger` was added to `templates/session/design/organization_cast.md` and referenced from organization generation rules.
- `Branch State` was added to `templates/session/design/story_spine.md` so mid-story detours can keep active/background branches consistent.

## Problem Summary

The current system has story-generation parts, but the final handoff into playable scenes is too weak.

Existing pieces:

- `prompt/story_reference.md` selects abstract story engines from Q&A, logs, or reference stock.
- `design/story_reference.md` stores selected abstract engines and conversion notes.
- `design/story_spine.md` stores a thin story spine, not a fixed plot.
- `design/organization_cast.md` stores organizations, pressure sources, and major NPC candidates.
- `current/case.md` stores the active playable case: visible problem, short goal, handles, progress condition, if ignored, and relationship stake.

The failure is usually not "no story exists." The failure is that abstract story, organization pressure, and NPC intent are not reliably converted into a concrete visible request or playable case.

## Observed Failure Mode

In the test scene, Q6 option 4 led to a hospital / management company / identity-confirmation situation. The scene had good materials:

- hospital envelope
- management company notice
- diagnosis card copy
- record mismatch
- apparent rejuvenation
- a heroine/NPC carrying the concern

But the player could not easily tell:

- who the issue was about
- why it mattered
- what would stop if ignored
- what the NPC wanted from the protagonist
- which concrete thing to touch first

The NPC spoke in vague phrases such as "a certain person" and "not only that" for too long. This made the story feel like atmosphere without a subject.

## Key Design Distinction

Truth hiding is primarily a GM responsibility.

The GM may hide:

- the true cause
- the antagonist or organization's full purpose
- the ability rule
- hidden motives
- facts that NPCs do not know

NPCs should only hide what is natural for their position.

NPCs may hide:

- information they do not know
- confidential personal information
- a name before trust is established
- information that would endanger someone
- their own guilt, weakness, or liability

NPCs who bring a request should still make the request playable. They should provide enough subject, problem, risk, and desired first action for the player to understand the scene.

## Improvement 1: Make Q6 More Concrete

Current Q6 examples are too category-like, especially option 4.

Improve Q6 so each option includes:

- who or what arrives
- what object / document / record / place is involved
- what is at risk
- what kind of first action the protagonist can take

Proposed Q6 shape:

```md
基本質問:

`最初の場面で、主人公の日常にどんな具体的な用事や違和感が持ち込まれると入りやすい？ 誰が来るか、何の書類・物・予定があるか、何が止まりそうかを短く選んで。お任せでもいい。`

回答例:

1. 目の前の人が、言いにくい相談を持ってくる
   例: 常連、依頼人、近所の人、昔の知り合いが、封筒・鍵・写真・怪我・嘘っぽい説明を抱えて来る。

2. いつもの場所や近所で、普段と違うことが起きる
   例: 店の前に知らない荷物がある、常連が来ない、大家から連絡が来る、鍵が少し引っかかる、隣室の音だけが変。

3. 私生活や仕事の範囲で、放っておきにくい用事が入る
   例: 知人から急な呼び出しがある、仕事先から確認が来る、客から代理対応を頼まれる、家族や昔の知り合いから予定にない連絡が来る。

4. 住んでいる街やよく行く地域で、同じ話が別々の場所から出る
   例: 駅前の店、病院、管理会社、学校、交番、地域の掲示で、同じ人・部屋・荷物・写真について確認される。

5. 離れた街や複数の県から、同じ話がつながって来る
   例: 東京の病院、神奈川のホテル、埼玉の配送、地方の役所から、同じ名前・住所・写真・荷物について別々に連絡が来る。

6. お任せ
   Q1の仕事・拠点、Q2のインナー、Q3の能力、Q4/Q5の関係方針から、GMが具体的な「人・物・期限・困りごと」を作って始める。
```

## Improvement 2: Add Visible Request Gate

Add a gate near `initial case card` in `prompt/core_newgame.md`, or near the `offered` phase in `prompt/case_engine.md`.

Purpose: make sure first consultations are playable even when truth remains hidden.

Proposed rule:

```md
### Visible Request Gate / 初回依頼の見える形

初回の依頼 / 相談 / 持ち込みでは、真相は隠してよい。
ただし、依頼として成立する情報は隠すな。

`visible request` には最低限以下を含める。

- 依頼人または相談者
- 当事者の最低限の属性、または名前を伏せる理由
- 困っている手続き / 物 / 場所 / 記録
- 放置すると何が生活上止まるか
- 主人公に頼む最初の行動
- 今すぐ触れる handles 2-4個

原因、黒幕、能力の本質、組織の全体像は隠してよい。
しかし、依頼の主語、困りごと、頼みたい行動まで隠すな。
```

## Improvement 3: Add Truth Hiding Boundary

Add to `prompt/runtime.md` or `prompt/gm_policy.md`.

Purpose: prevent the GM's truth-hiding discipline from making NPC dialogue unnaturally vague.

Proposed rule:

```md
### Truth Hiding Boundary

真相を隠す主体はGMである。
NPCは、本人の知識、立場、守秘義務、恐怖、利害に従って話す。

NPCが隠してよいもの:
- 本当に知らないこと
- 守秘義務がある個人情報
- 信頼前には出せない名前や関係
- 言うと相手を危険にする情報
- 自分の弱み、罪悪感、責任

NPCが依頼時に出すべきもの:
- 自分の立場
- 困っている人の最低限の属性
- 起きている問題
- 放置した時の悪化
- 主人公に頼みたい最初の行動

NPCが「ある人」「それ」「この件」だけで会話を進め続けるな。
名前を伏せる場合でも、当事者の立場、困っている手続き、今止まりそうな生活の面は具体化しろ。
```

## Improvement 4: Mid-Story Activation Gate

The same story-generation logic must run during play, not only at new-game start.

Trigger this gate when the player:

- actively contacts another organization, department, window, faction, or institution
- declares investigation, negotiation, infiltration, exposure, protection, escape, bargaining, or sabotage
- ignores the active case and enters a new location or pressure source
- brings a background hook to the foreground
- causes a personal issue to expand into a system / organization / faction issue
- makes a recurring NPC or major contact important enough to need continuity

Proposed rule:

```md
### Mid-Story Activation Gate

When a player actively engages a new pressure source, organization, faction, department, location, or major NPC, decide whether this is:

- an existing story_spine branch
- a new story branch
- a local case
- a background case becoming active
- a new organization / faction contact surface

Then create or update:

- related organization / faction / window
- relationship to existing organizations
- 1-3 major NPCs or contact persons
- active case or background case placement
- short goal
- handles
- if ignored
- next visible change
- heroine / protagonist life stake
```

## Improvement 5: Organization Relation Ledger

When multiple organizations appear, they need relationship consistency. Otherwise each new institution becomes a one-off abstract window.

Proposed structure:

```md
## Organization Relation Ledger

- organization:
- public role:
- hidden / suspected role:
- relation to existing organizations:
- contact surface:
- what they want:
- what they protect:
- what they can stop:
- what they cannot do:
- major NPCs:
- leverage against them:
- leverage they hold:
- linked case:
- if ignored:
```

This can live in `design/organization_cast.md`, `design/story_spine.md`, or a future dedicated organization ledger if the structure grows.

## Improvement 6: Active / Background / Branch Switching

When the player branches, do not let all hooks compete equally.

Rules to add or strengthen:

- only one active case should lead the current scene
- old active case can become background if the player leaves it
- background cases still move via `if ignored`
- a new local case can be created for travel, detours, or a new organization
- active case must always expose `short goal` or `handles`
- story_spine must be updated when a branch changes the main question, organization pressure, or heroine tie

## Best Implementation Order

1. Update Q6 question and examples.
2. Add Visible Request Gate.
3. Add Truth Hiding Boundary.
4. Add Mid-Story Activation Gate.
5. Add Organization Relation Ledger / relation section.
6. Add active/background/branch switching rule if not already sufficient.
7. Run `python scripts/liria_prompt_auditor.py --root .`.
8. Check whether warnings are acceptable or need scoped follow-up.

## Expected Result

The GM can still hide the truth, but the scene should no longer hide the request.

At new-game start or mid-story branch, the GM should quickly know:

- whose life is affected
- what concrete thing is wrong
- what organization or contact surface is involved
- what the protagonist is being asked to do first
- what object / person / place / record can be touched now
- what happens if the player ignores it

This should reduce vague dialogue, abstract organization talk, and scenes where the player has to ask "what is the problem?" before they can play.
