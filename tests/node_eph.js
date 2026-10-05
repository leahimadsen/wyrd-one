// Test-only: serves the console's built-in ephemeris over stdin/stdout so
// the Python port can be checked against the JavaScript with identical inputs.
const E = require('../lib/engine.js');
require('readline').createInterface({ input: process.stdin }).on('line', l => {
  const q = JSON.parse(l); let r;
  if (q.f === 'positions') r = E.positions(q.jd);
  else if (q.f === 'sun') r = E.sunLon(q.jd);
  else if (q.f === 'ay') r = E.ayanamsa(q.jd);
  else if (q.f === 'angles') r = [E.ascendant(q.jd, q.lat, q.lon), E.midheaven(q.jd, q.lon)];
  else if (q.f === 'cast') r = E.cast(...q.args);
  else if (q.f === 'dasha') { const c = E.cast(...q.args); r = E.dashaFor(c, q.now); }
  process.stdout.write(JSON.stringify(r) + '\n');
});
