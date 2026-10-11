'use strict';
/* The body map on the free chart: which part of the body each sign and each mansion
   stands for (Kalapurusha, Aries at the head; the mansions from the Brihat Samhita).
   A copy of lib/medical.json's tables; tests/medical_check.py keeps them equal.
   What it means is in the reading (wyrd/medical.py). */
window.WyrdMedical = {
  SIGN: {"Aries": "the head", "Taurus": "the throat", "Gemini": "the shoulders and arms", "Cancer": "the chest and stomach", "Leo": "the heart and back", "Virgo": "the belly", "Libra": "the kidneys and lower back", "Scorpio": "the pelvis", "Sagittarius": "the hips and thighs", "Capricorn": "the knees and bones", "Aquarius": "the calves and ankles", "Pisces": "the feet"},
  NAK: ["the knees", "the head", "the hips", "the shins", "the eyes", "the hair", "the fingers", "the mouth", "the nails", "the nose", "the sexual organs", "the sexual organs", "the hands", "the forehead", "the teeth", "the arms", "the chest", "the neck", "the feet", "the thighs", "the thighs", "the ears", "the back", "the jaw", "the sides", "the sides", "the belly"]
};
