'use strict';
/* ============================================================
   THE WRITING FOR COMPARE, in the register's voice.
   Edit freely; nothing else needs to change.

   SUKUYO     the six relations of the sanku method: the engine of the bond,
              how it floods and freezes, and the question it asks
   DISTANCE   near, middle, far
   PAIRS      a contact between two planets: its engine, how it runs fused
              (conjunction), flowing (trine, sextile) and in friction
              (square, opposition), and its question. "The Sun person",
              "the Moon person" are replaced with names on the page.
   ROLE       what each planet carries, for contacts not in PAIRS
   IN_HOUSE   what a planet does when it crosses into another's house
   The houses themselves are named by their phase in viz.js (HOUSES).
   ============================================================ */
(() => {
const SUKUYO = {
  "命": { title: "Mei · Life", short: "the mirror",
    text: "Two people issued under one star. What descends on one descends on the other; what one reaches for, the other was already reaching for. Recognition is immediate, and so is the shared blind spot — neither of you can see past what both of you miss. The bond completes when each keeps one room the other cannot furnish. Flood: the two of you merge until neither can tell whose wanting it is. Freeze: you keep your distance because the other is too exactly yourself.",
    ask: "What do you see in them that you have not yet admitted is yours?" },
  "業胎": { title: "Gyōtai · Karma and Womb", short: "the bond with history",
    text: "The tie that arrives with a past. One of you is the other's Karma — the debt brought forward; the other is the first one's Womb — the life still being carried to term. Familiarity comes before any reason for it, and so does obligation. The bond completes when the account is named out loud: what is owed, what is being taught, and when the teaching is finished. Flood: the old debt paid again and again, with interest no one agreed to. Freeze: the tie refused because it feels like a sentence.",
    ask: "What are you still paying each other for — and has either of you said what it was?" },
  "栄親": { title: "Eishin · Prosperity and Intimacy", short: "the kindest bond",
    text: "The kindest of the six. One brings prosperity, the other brings intimacy, and each house grows richer for the other standing in it. Ease is real here, and early. The risk is only the risk of all good weather: the bond stops being tended because it has never needed tending. Flood: comfort taken as a birthright, the other's gifts no longer seen. Freeze: the ease mistrusted, waited out like a debt that will surely be called in.",
    ask: "What does this bond give you that you have stopped thanking it for?" },
  "友衰": { title: "Yūsui · Friendship and Decline", short: "the companions",
    text: "Companions from the first meeting: understood without effort, at rest in each other's company. The name carries its own warning. Ease descends; ambition does not ascend. Together you can let the year go soft, and call it peace. The bond completes when the friendship is the ground and the striving is carried out of it, into the world. Flood: two people agreeing each other into stillness. Freeze: the friendship kept shallow so that neither has to admit how much it holds them.",
    ask: "Is this the place you rest — or the place you stopped?" },
  "安壊": { title: "Ankai · Peace and Destruction", short: "the charged bond",
    text: "The most charged of the six: magnetic, unsettling, transforming. One side is named Peace, the other Destruction, and the meeting breaks old forms open — the question is only whether what breaks was meant to. Nothing about this bond is neutral, and little of it is forgettable. It completes when the breaking is done with consent and in the open, as clearing rather than wreckage. Flood: the destruction runs on, past every form that deserved to end, into the ones that did not. Freeze: the pull denied, held at arm's length until it detonates.",
    ask: "What has this person broken open in you — and was it ready to break?" },
  "危成": { title: "Kisei · Danger and Completion", short: "the different ones",
    text: "Different values, different speeds. What descends from one is precisely what the other lacks; what ascends is the friction of receiving it. The meeting stimulates and abrades in the same breath. It completes when both respect the distance between them — the distance is the instrument, not the problem — and then it finishes something neither would finish alone. Flood: every difference fought as a betrayal. Freeze: the difference never risked, the bond kept polite and unfinished.",
    ask: "What can you only finish with someone who does not see it your way?" },
};
const DISTANCE = {
  near: "At near distance the bond lands at once and at full strength.",
  middle: "At middle distance it works steadily — neither overwhelming nor faint.",
  far: "At far distance it works slowly, underground, and is mostly seen in hindsight.",
};
const NAMES = { "命": "Life", "業": "Karma", "胎": "Womb", "栄": "Prosperity", "親": "Intimacy", "友": "Friendship", "衰": "Decline",
  "安": "Peace", "壊": "Destruction", "危": "Danger", "成": "Completion" };

/* key: the two planets in the order Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Rahu, Ketu */
const PAIRS = {
  "Sun-Sun": { core: "Two wills run through one light. Each is lit by the same fire, and each wants to be seen by it.",
    conj: "Fused, it is kinship — and competition for the one stage.", soft: "Flowing, the two purposes run side by side: each can be seen without the other dimming.", hard: "In friction, each purpose reads the other as a correction — be someone else.",
    ask: "Can you both be seen at once, or only in turn?" },
  "Sun-Moon": { core: "Will run through need: the oldest sign of two lives that fit. What descends from the Sun person is direction; what ascends from the Moon person is what direction must carry to be bearable.",
    conj: "Fused, purpose and inner life share a body. This is the contact that feels like home.", soft: "Flowing, what the Sun person sets out to do, the Moon person instinctively provisions — and the Sun person sees the Moon person whole.", hard: "In friction, the Sun person's drive tramples what the Moon person needs to feel safe, and the Moon person's weather reads as a brake. Worth the work: it is still the contact of two lives that matter to each other.",
    ask: "When the Sun person moves, does the Moon person feel carried — or left behind?" },
  "Sun-Mercury": { core: "Identity run through speech. The Mercury person gives the Sun person words for what the Sun person is.",
    conj: "Fused, you talk the same self into being.", soft: "Flowing, the Mercury person helps the Sun person say exactly what they mean.", hard: "In friction, being described slides into being corrected.",
    ask: "Does the naming free them — or fix them?" },
  "Sun-Venus": { core: "Will run through affection. What descends is the Sun person's presence; what ascends is the Venus person's delight in it.",
    conj: "Fused, the Venus person simply likes the Sun person, and says so.", soft: "Flowing, appreciation and shared taste; time together costs nothing.", hard: "In friction, the affection is real but on different terms — what one treasures, the other shrugs at.",
    ask: "Is the admiration for who they are, or for how they shine?" },
  "Sun-Mars": { core: "Will run through drive: two engines in one room.",
    conj: "Fused, heat — desire and argument from the same spark.", soft: "Flowing, a team for getting things done; the Mars person fuels the Sun person's aims.", hard: "In friction, two engines revving against each other — competitive, provoking, sometimes combative.",
    ask: "Is the heat building something, or only proving something?" },
  "Sun-Jupiter": { core: "Will run through faith. The Jupiter person believes in the Sun person before the Sun person does.",
    conj: "Fused, the Sun person grows in the Jupiter person's company.", soft: "Flowing, generosity and good humour; each enlarges the other's world.", hard: "In friction, encouragement tips into excess — the promise outruns the ground.",
    ask: "What has this faith made possible — and what has it let you avoid?" },
  "Sun-Saturn": { core: "Will run through duty: the contact of commitment. What descends from the Saturn person is the test; what ascends from the Sun person is what survives it.",
    conj: "Fused, the Saturn person steadies, measures and sometimes restricts the Sun person. Serious, durable, rarely light.", soft: "Flowing, the Saturn person gives the Sun person's aims structure and staying power. This one lasts.", hard: "In friction, the Saturn person becomes the judge and the Sun person the burden; respect has to be earned on both sides, slowly.",
    ask: "Is the weight between you a frame — or a ceiling?" },
  "Sun-Rahu": { core: "Will run through hunger. The Rahu person is drawn to the Sun person's light as to something they were born missing.",
    conj: "Fused, fascination — the bond feels fated and new at once.", soft: "Flowing, the Sun person lights the way toward what the Rahu person is reaching for.", hard: "In friction, the pull outruns the wisdom; wanting becomes the whole of the bond.",
    ask: "What is the hunger for — the person, or what they stand next to?" },
  "Sun-Ketu": { core: "Will run through the already-known. Something here was finished before it started.",
    conj: "Fused, an uncanny familiarity — and the Ketu person's quiet step back from the Sun person's light.", soft: "Flowing, ease without effort: an old understanding.", hard: "In friction, detachment where warmth was hoped for.",
    ask: "What are you recognising — and is it still alive?" },
  "Moon-Moon": { core: "Two inner lives run through one tide.",
    conj: "Fused, you feel the same things in the same way — deep comfort, and moods that swing together.", soft: "Flowing, your rhythms fit; you know how to look after each other without being told.", hard: "In friction, you need different things to feel safe, and each feels misunderstood exactly when it matters.",
    ask: "When you are both low, who holds whom?" },
  "Moon-Mercury": { core: "Feeling run through speech. The Mercury person puts words where the Moon person only had weather.",
    conj: "Fused, the feeling is named as it arrives.", soft: "Flowing, talk is easy and caring.", hard: "In friction, the feeling is analysed when it wanted holding.",
    ask: "Do the words hold the feeling — or handle it?" },
  "Moon-Venus": { core: "Need run through affection: one of the tenderest contacts.",
    conj: "Fused, the Venus person soothes the Moon person simply by arriving.", soft: "Flowing, gentle and affectionate; each feels cared for without asking.", hard: "In friction, the affection is real but arrives in a language the other does not take in.",
    ask: "Do you love each other in the way the other can receive?" },
  "Moon-Mars": { core: "Need run through desire. What descends from the Mars person is heat; what ascends from the Moon person is how much heat the inner life can bear.",
    conj: "Fused, strong attraction and strong reaction — the same spark for passion and temper.", soft: "Flowing, warmth with energy; the Mars person guards and enlivens the Moon person.", hard: "In friction, the Mars person's bluntness lands on the Moon person's skin; quarrels flare before either knows why.",
    ask: "Does the heat warm the house, or set it alight?" },
  "Moon-Jupiter": { core: "Need run through faith. The Jupiter person makes the Moon person's world feel larger and safer.",
    conj: "Fused, emotional abundance — generosity offered before it is asked for.", soft: "Flowing, kindness and hope; the bond feels protective.", hard: "In friction, comfort becomes indulgence, or counsel becomes a sermon.",
    ask: "Is the care making the Moon person larger — or keeping them small?" },
  "Moon-Saturn": { core: "Need run through duty: the binding contact. What descends from the Saturn person is constancy; what ascends from the Moon person is whether constancy feels like shelter or like a cell.",
    conj: "Fused, deep loyalty, with weight — the Moon person held, and sometimes held back.", soft: "Flowing, security and dependability; the Saturn person is something to lean on.", hard: "In friction, coolness exactly where warmth is needed — the Moon person feels judged, the Saturn person burdened. Very durable, if worked.",
    ask: "What has the Saturn person promised that the Moon person has not yet felt?" },
  "Moon-Rahu": { core: "Need run through hunger. The bond feels destined, and is rarely restful.",
    conj: "Fused, emotional fascination — often compulsive.", soft: "Flowing, the Moon person makes the Rahu person feel at home in new territory.", hard: "In friction, restlessness and upheaval; neither can settle.",
    ask: "Is this a home, or a fever?" },
  "Moon-Ketu": { core: "Need run through the already-known: kin from somewhere earlier.",
    conj: "Fused, a wordless familiarity, as of old blood.", soft: "Flowing, quiet understanding that asks for nothing.", hard: "In friction, one feels the other left emotionally before anything began.",
    ask: "Are you meeting each other — or a memory?" },
  "Mercury-Mercury": { core: "Two minds run through one conversation.",
    conj: "Fused, you think alike and finish each other's sentences.", soft: "Flowing, good talk, shared humour, plans made easily.", hard: "In friction, different ways of knowing — debate, misreading, talking past each other.",
    ask: "When you disagree, are you hearing the other's mind — or only its errors?" },
  "Mercury-Mars": { core: "Mind run through drive.", conj: "Fused, sharp, fast exchange — stimulating, sometimes heated.", soft: "Flowing, ideas turn quickly into action.", hard: "In friction, sharp words and impatience.",
    ask: "Are the words a tool between you, or a weapon?" },
  "Mercury-Saturn": { core: "Mind run through duty. The Saturn person grounds the Mercury person's ideas — or dampens them.",
    conj: "Fused, serious talk; nothing said lightly.", soft: "Flowing, careful, practical planning.", hard: "In friction, criticism or silence; the Mercury person stops speaking.",
    ask: "Does the Mercury person feel heard, or graded?" },
  "Venus-Venus": { core: "Two ways of valuing run through one taste.",
    conj: "Fused, you love the same things, and each other easily.", soft: "Flowing, shared pleasure; affection flows.", hard: "In friction, different tastes, different languages of love.",
    ask: "What do you each treasure that the other has never asked about?" },
  "Venus-Mars": { core: "Affection run through desire: the classic contact of attraction. What descends is wanting; what ascends is being wanted well.",
    conj: "Fused, strong romantic and physical chemistry.", soft: "Flowing, an attraction that is easy, warm and lasting.", hard: "In friction, chemistry with an edge — desire and irritation in equal measure.",
    ask: "Is the wanting mutual in kind, or only in strength?" },
  "Venus-Jupiter": { core: "Affection run through faith.", conj: "Fused, generous, celebratory; life is enjoyed together.", soft: "Flowing, ease, kindness and good fortune.", hard: "In friction, too much of a good thing — indulgence, and hopes that outgrow the ground.",
    ask: "What would this bond look like with less, and would it still be good?" },
  "Venus-Saturn": { core: "Affection run through duty: the contact of lasting bonds. Love is offered on a timetable — and kept.",
    conj: "Fused, love that is serious and loyal, and sometimes restrained.", soft: "Flowing, steady, committed affection that ages well.", hard: "In friction, one withholds and the other feels unloved; the ledger is kept but never read aloud.",
    ask: "What is the love waiting for permission to say?" },
  "Venus-Rahu": { core: "Affection run through hunger.", conj: "Fused, intoxicating attraction, often unconventional.", soft: "Flowing, novelty and delight in each other.", hard: "In friction, infatuation that outruns the person in front of you.",
    ask: "Do you love them, or the strangeness they bring?" },
  "Venus-Ketu": { core: "Affection run through the already-known: a love that feels remembered rather than found.",
    conj: "Fused, old tenderness, instantly.", soft: "Flowing, ease without effort.", hard: "In friction, the affection drifts, detaches, goes quiet.",
    ask: "Is the tenderness here, or still back where it began?" },
  "Mars-Mars": { core: "Two drives run through one field.", conj: "Fused, equal energy — you act together and fight together.", soft: "Flowing, you work and play well side by side.", hard: "In friction, competition and clashes of will.",
    ask: "When you both push, what gives?" },
  "Mars-Jupiter": { core: "Drive run through faith.", conj: "Fused, enthusiasm and shared ventures.", soft: "Flowing, bold plans that work.", hard: "In friction, over-confidence; the ground left behind.",
    ask: "Who keeps the venture honest?" },
  "Mars-Saturn": { core: "Drive run through duty: the accelerator and the brake.",
    conj: "Fused, discipline and frustration together — very productive, or very blocked.", soft: "Flowing, energy given shape; good for long work.", hard: "In friction, one pushes and the other blocks; resentment grows unless the roles are named.",
    ask: "Have you said out loud which of you is the brake?" },
};
const ROLE = { Sun: "will", Moon: "need", Mercury: "speech", Venus: "affection", Mars: "drive", Jupiter: "faith", Saturn: "duty",
  Rahu: "hunger", Ketu: "the already-known", Uranus: "the sudden", Neptune: "the dissolving", Pluto: "depth" };
const FLAVOUR = { conj: "fused: the two poles share a body", soft: "flowing: each provisions the other", hard: "in friction: each tests the other" };
const IN_HOUSE = { Sun: "brings their light into", Moon: "makes a home in", Mercury: "starts conversations in", Venus: "brings warmth into",
  Mars: "stirs the fire in", Jupiter: "widens", Saturn: "sets a weight and a frame in", Rahu: "makes you hungry in", Ketu: "feels long-familiar in" };
/* fallback names for the houses if viz.js is not loaded */
const HOUSE = ["the self at the gate", "resources and the voice", "craft, siblings, movement", "foundation and root", "creation, children, merit",
  "service, the daily year", "the other, the heart-house", "shared resource, transformation", "the far view, dharma",
  "vocation, authority", "networks, gains, transmission", "dissolution, the hidden, release"];

window.WyrdDynamics = { SUKUYO, DISTANCE, NAMES, PAIRS, ROLE, FLAVOUR, HOUSE, IN_HOUSE };
})();
