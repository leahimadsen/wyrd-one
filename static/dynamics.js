'use strict';
/* ============================================================
   THE WRITING FOR COMPARE
   Everything Compare says about the dynamic between people lives here,
   so it can be rewritten in your own voice without touching the code.
   DRAFTED FOR SAGA DEVI TO EDIT.

   SUKUYO     the six relations of the sanku method, and the three distances
   PAIRS      what a contact between two planets is about, and how it plays
              when fused (conjunction), flowing (trine, sextile) or in friction
              (square, opposition). Written "the Sun person / the Moon person";
              the page puts in the names.
   ROLE       what each planet is, for contacts with no entry in PAIRS
   IN_HOUSE   what a planet does when it lands in someone's house
   HOUSE      what each house is
   ============================================================ */
(() => {
const SUKUYO = {
  "命": { title: "Mei · Life", short: "the mirror",
    text: "You were born under the same shuku. This is the mirror bond: instant recognition, the same instincts, the same blind spots. It can feel like meeting yourself, which is a comfort and sometimes a strain, because neither of you sees past what both of you miss. It goes best when each keeps something of their own." },
  "業胎": { title: "Gyōtai · Karma and Womb", short: "the bond with history",
    text: "Sukuyō's tie of past and future lives: one of you is the other's Karma (業), the other the first one's Womb (胎). Expect a familiarity that arrives before any reason for it, a sense of something owed or something being taught, and a bond that is hard to walk away from even when it is hard to be in." },
  "栄親": { title: "Eishin · Prosperity and Intimacy", short: "the kindest bond",
    text: "The kindest of the relations. One brings the other prosperity, the other brings intimacy and trust, and each tends to make the other's life go better simply by being in it. Ease comes early and lasts. Its only risk is taking that ease for granted." },
  "友衰": { title: "Yūsui · Friendship and Decline", short: "the companions",
    text: "Companions. Easy to be with, quick to understand each other, comfortable from the first meeting. The warning is in the name: comfort can soften you both, and together you may let ambition slide. Good for rest, friendship and home; set goals outside the bond." },
  "安壊": { title: "Ankai · Peace and Destruction", short: "the charged bond",
    text: "The most charged of the relations: magnetic, unsettling, transforming. One side is called Peace and the other Destruction, and the pull between them breaks old patterns open, for better or worse. It is rarely neutral and rarely forgettable. It asks for care and honesty, and repays them." },
  "危成": { title: "Kisei · Danger and Completion", short: "the different ones",
    text: "Different values, different speeds. The meeting is stimulating and can be abrasive; each shows the other what they lack. It works when both respect the distance between them, and then it completes something neither would finish alone." },
};
const DISTANCE = {
  near: "At near distance the relation is felt at once and at full strength.",
  middle: "At middle distance it works steadily, neither overwhelming nor faint.",
  far: "At far distance it works slowly and gently, and is often seen only in hindsight.",
};
const NAMES = { "命": "Life", "業": "Karma", "胎": "Womb", "栄": "Prosperity", "親": "Intimacy", "友": "Friendship", "衰": "Decline",
  "安": "Peace", "壊": "Destruction", "危": "Danger", "成": "Completion" };

/* key: the two planets in this order */
const PAIRS = {
  "Sun-Sun": { core: "Two wills, two ways of shining.", conj: "You are lit by the same things and want to be seen for the same things; that is kinship, and also competition for the same light.", soft: "Your purposes run alongside each other: you can cheer each other on without either dimming.", hard: "Your purposes pull in different directions, and each can feel the other asks them to be someone else." },
  "Sun-Moon": { core: "The classic contact of two lives that fit: one person's will meets the other's needs.", conj: "The Sun person's purpose and the Moon person's inner life sit in the same place. This is the oldest sign of a bond that feels like home.", soft: "What the Sun person sets out to do, the Moon person instinctively supports, and the Sun person sees the Moon person clearly.", hard: "The Sun person's drive can trample what the Moon person needs to feel safe; the Moon person's moods can feel like a brake. Worth the work: it is still the contact of two lives that matter to each other." },
  "Sun-Mercury": { core: "Identity meets mind.", conj: "The Mercury person puts words to who the Sun person is; conversation comes easily and often.", soft: "You think well together, and the Mercury person helps the Sun person say what they mean.", hard: "The Mercury person's reading of the Sun person can feel like criticism; talk easily turns to correction." },
  "Sun-Venus": { core: "Will meets affection.", conj: "The Venus person simply likes the Sun person, and shows it; the Sun person feels admired.", soft: "Warmth, appreciation and shared taste. Easy to spend time together.", hard: "Affection is there, but on different terms: what one values, the other shrugs at." },
  "Sun-Mars": { core: "Will meets drive.", conj: "Energy and heat: you push each other to act, and can spark both desire and argument.", soft: "You make a good team for getting things done; the Mars person energises the Sun person's aims.", hard: "Two engines that rev against each other: competitive, provoking, sometimes combative." },
  "Sun-Jupiter": { core: "Will meets faith.", conj: "The Jupiter person believes in the Sun person, and the Sun person grows in their company.", soft: "Generosity and good humour; each makes the other's world larger.", hard: "Big promises and over-reach: encouragement can tip into excess or preaching." },
  "Sun-Saturn": { core: "Will meets duty: the contact of commitment.", conj: "The Saturn person steadies, tests and sometimes restricts the Sun person. Serious, durable and not always light.", soft: "The Saturn person gives the Sun person's aims structure and staying power; this bond lasts.", hard: "The Saturn person can feel like a judge and the Sun person like a burden. Respect has to be earned on both sides." },
  "Sun-Rahu": { core: "Will meets hunger.", conj: "Fascination: the Rahu person is drawn to the Sun person's light, and the bond feels fated and new.", soft: "The Sun person helps the Rahu person grow toward something they reach for.", hard: "Obsession or overreach: the pull is strong and not always wise." },
  "Sun-Ketu": { core: "Will meets the already-known.", conj: "An uncanny familiarity, as if you had met before; the Ketu person may also quietly withdraw from the Sun person's light.", soft: "Ease without effort: an old understanding.", hard: "Something in the bond feels finished before it starts; detachment where warmth was hoped for." },
  "Moon-Moon": { core: "Two inner lives, two ways of needing.", conj: "You feel the same things in the same way. Deep comfort, and shared moods that can swing together.", soft: "Your emotional rhythms fit: you know how to look after each other without being told.", hard: "You need different things to feel safe, and each can feel misunderstood at the moments that matter most." },
  "Moon-Mercury": { core: "Feeling meets mind.", conj: "The Mercury person can put the Moon person's feelings into words.", soft: "Talk is easy and caring; you understand each other's moods.", hard: "Feelings get analysed when they want holding; words land harder than intended." },
  "Moon-Venus": { core: "Need meets affection: one of the tenderest contacts.", conj: "Tenderness, comfort and liking. The Venus person soothes the Moon person.", soft: "Gentle, affectionate and easy: you make each other feel cared for.", hard: "Affection is real, but expressed in ways the other doesn't quite take in." },
  "Moon-Mars": { core: "Need meets desire.", conj: "Strong attraction and strong reactions: the Mars person stirs the Moon person, for passion and for temper.", soft: "Warmth with energy: the Mars person protects and enlivens the Moon person.", hard: "The Mars person's bluntness wounds the Moon person's feelings; quarrels flare fast." },
  "Moon-Jupiter": { core: "Need meets faith.", conj: "Generosity and emotional abundance; the Jupiter person makes the Moon person feel safe and hopeful.", soft: "Kindness and optimism; the bond feels protective.", hard: "Comfort can become indulgence, or the Jupiter person's advice can feel like a lecture." },
  "Moon-Saturn": { core: "Need meets duty: the binding contact.", conj: "Deep loyalty, with weight: the Saturn person is steady, and the Moon person can feel held or held back.", soft: "Security and dependability. The Saturn person gives the Moon person something to lean on.", hard: "Coolness where warmth is needed; the Moon person can feel judged, the Saturn person burdened. Very durable if worked." },
  "Moon-Rahu": { core: "Need meets hunger.", conj: "Intense emotional fascination, often compulsive; the bond feels destined.", soft: "The Moon person helps the Rahu person feel at home in new territory.", hard: "Restlessness and emotional upheaval; hard to settle." },
  "Moon-Ketu": { core: "Need meets the already-known.", conj: "Deep, wordless familiarity, as of old kin.", soft: "Quiet understanding without effort.", hard: "One feels the other has emotionally left before anything began." },
  "Mercury-Mercury": { core: "Two minds.", conj: "You think alike and finish each other's sentences.", soft: "Good conversation, shared humour, easy plans.", hard: "Different ways of thinking: debates, misreadings, talking past each other." },
  "Mercury-Mars": { core: "Mind meets drive.", conj: "Sharp, fast exchanges: stimulating, sometimes heated.", soft: "Ideas turn quickly into action.", hard: "Arguments, sharp words, impatience." },
  "Mercury-Saturn": { core: "Mind meets duty.", conj: "Serious talk; the Saturn person grounds the Mercury person's ideas, or dampens them.", soft: "Practical, careful planning together.", hard: "Criticism, silence or feeling unheard." },
  "Venus-Venus": { core: "Two ways of loving and valuing.", conj: "You love the same things and like each other easily.", soft: "Shared taste and pleasure; affection flows.", hard: "Different tastes and different love languages." },
  "Venus-Mars": { core: "Affection meets desire: the classic contact of attraction.", conj: "Strong romantic and physical chemistry.", soft: "Attraction that is easy, warm and lasting.", hard: "Chemistry with friction: desire and irritation in equal measure." },
  "Venus-Jupiter": { core: "Affection meets faith.", conj: "Generous, warm, celebratory; you enjoy life together.", soft: "Ease, kindness and good fortune together.", hard: "Too much of a good thing: indulgence and unrealistic hopes." },
  "Venus-Saturn": { core: "Affection meets duty: the contact of lasting bonds.", conj: "Love that is serious and loyal, and sometimes restrained.", soft: "Steady, committed affection that ages well.", hard: "One withholds and the other feels unloved; love on a timetable." },
  "Venus-Rahu": { core: "Affection meets hunger.", conj: "Intoxicating attraction, often unconventional.", soft: "Novelty and delight in each other.", hard: "Infatuation that outruns reality." },
  "Venus-Ketu": { core: "Affection meets the already-known.", conj: "A love that feels remembered rather than found.", soft: "Easy, old tenderness.", hard: "Affection that drifts or detaches." },
  "Mars-Mars": { core: "Two drives.", conj: "Equal energy: you act together, and fight together.", soft: "You work and play well side by side.", hard: "Competition and clashes of will." },
  "Mars-Jupiter": { core: "Drive meets faith.", conj: "Enthusiasm and shared ventures.", soft: "Bold plans that work out.", hard: "Over-confidence, running ahead of sense." },
  "Mars-Saturn": { core: "Drive meets duty: the accelerator and the brake.", conj: "Discipline and frustration together; a very productive or very blocked pairing.", soft: "Energy given useful shape; good for long work.", hard: "One pushes, the other blocks. Resentment unless the roles are named." },
};
const ROLE = { Sun: "will and identity", Moon: "feeling and need", Mercury: "mind and speech", Venus: "affection and taste", Mars: "drive and desire",
  Jupiter: "faith and growth", Saturn: "duty and limits", Rahu: "hunger for the new", Ketu: "the already-known", Uranus: "the sudden and the free",
  Neptune: "dream and dissolving", Pluto: "depth and power" };
const FLAVOUR = { conj: "fused: the two are felt as one thing", soft: "flowing: they help each other", hard: "in friction: they test each other" };

const HOUSE = ["self and body", "money, values and voice", "talk, siblings and the near world", "home and roots", "romance, play and children",
  "daily work and health", "partnership and the other", "intimacy, shared resources and change", "beliefs, teaching and travel",
  "career and reputation", "friends, groups and hopes", "the hidden, solitude and release"];
const IN_HOUSE = { Sun: "lights up", Moon: "feels at home in", Mercury: "gets you talking about", Venus: "brings warmth to", Mars: "stirs up",
  Jupiter: "expands", Saturn: "brings weight and structure to", Rahu: "makes you hungry for", Ketu: "feels oddly familiar in" };

window.WyrdDynamics = { SUKUYO, DISTANCE, NAMES, PAIRS, ROLE, FLAVOUR, HOUSE, IN_HOUSE };
})();
