'use strict';
/* ============================================================
   THE FREE WORDS FOR COMPARE: the names of things, never their meaning.
   Edit freely; nothing else needs to change.

   SUKUYO     each of the six relations' title and one-line label
   NAMES      the eleven roles of the sanku ring
   ROLE       what each planet carries, in a word
   FLAVOUR    how a contact runs: fused, flowing, in friction
   HOUSE      the houses, as phases

   The full writing about a bond (each relation's engine and question, every
   planet contact, the houses in words, the higher and lower paths) is paid:
   it lives in lib/bond.json and is only sent inside a reading together.
   ============================================================ */
(() => {
const SUKUYO = {
  "命": { title: "Mei · Life", short: "the mirror" },
  "業胎": { title: "Gyōtai · Karma and Womb", short: "the bond with history" },
  "栄親": { title: "Eishin · Prosperity and Intimacy", short: "the kindest bond" },
  "友衰": { title: "Yūsui · Friendship and Decline", short: "the companions" },
  "安壊": { title: "Ankai · Peace and Destruction", short: "the charged bond" },
  "危成": { title: "Kisei · Danger and Completion", short: "the different ones" },
};
const NAMES = { "命": "Life", "業": "Karma", "胎": "Womb", "栄": "Prosperity", "親": "Intimacy", "友": "Friendship", "衰": "Decline",
  "安": "Peace", "壊": "Destruction", "危": "Danger", "成": "Completion" };
const ROLE = { Sun: "will", Moon: "need", Mercury: "speech", Venus: "affection", Mars: "drive", Jupiter: "faith", Saturn: "duty",
  Rahu: "hunger", Ketu: "the already-known", Uranus: "the sudden", Neptune: "the dissolving", Pluto: "depth" };
const FLAVOUR = { conj: "fused: the two poles share a body", soft: "flowing: each provisions the other", hard: "in friction: each tests the other" };
const HOUSE = ["the self at the gate", "resources and the voice", "craft, siblings, movement", "foundation and root", "creation, children, merit",
  "service, the daily year", "the other, the heart-house", "shared resource, transformation", "the far view, dharma",
  "vocation, authority", "networks, gains, transmission", "dissolution, the hidden, release"];

window.WyrdDynamics = { SUKUYO, NAMES, ROLE, FLAVOUR, HOUSE };
})();
