"""Prove the Python engine equals the console's JavaScript engine.
Both are fed the console's own planet positions; every output field must match."""
import json, subprocess, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wyrd import engine

class NodeEph:
    def __init__(self):
        self.p = subprocess.Popen(['node', os.path.join(os.path.dirname(__file__), 'node_eph.js')],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    def q(self, **k):
        self.p.stdin.write(json.dumps(k) + '\n'); self.p.stdin.flush()
        return json.loads(self.p.stdout.readline())
    def positions(self, jd): return self.q(f='positions', jd=jd)
    def sun_lon(self, jd):   return self.q(f='sun', jd=jd)
    def ayanamsa(self, jd):  return self.q(f='ay', jd=jd)
    def angles(self, jd, lat, lon): return tuple(self.q(f='angles', jd=jd, lat=lat, lon=lon))

def compare(a, b, path=''):
    bad = []
    if isinstance(a, dict):
        if set(a) != set(b): bad.append(f'{path}: keys {sorted(set(a)^set(b))}')
        for k in a:
            if k in b: bad += compare(a[k], b[k], f'{path}.{k}')
    elif isinstance(a, (int, float)) and not isinstance(a, bool):
        if abs(a - b) > 1e-9: bad.append(f'{path}: {a} vs {b}')
    elif a != b: bad.append(f'{path}: {a!r} vs {b!r}')
    return bad

if __name__ == '__main__':
    eph = NodeEph()
    NOW = engine.julian_day(2026, 10, 4, 12)
    cases = [[1984,6,15,14.5,43.615,-116.2023],[1970,1,1,0,51.5,-0.12],[1999,12,31,23.9,-33.86,151.2],
             [2005,3,20,6.25,28.6,77.2],[1955,8,8,17,40.71,-74.0],[1991,11,2,3.75,64.15,-21.94],
             [1962,2,28,21.1,-22.9,-43.2],[2012,7,7,9.9,35.68,139.69]]
    fails = 0
    for c in cases:
        js = eph.q(f='cast', args=c + [NOW])
        py = json.loads(json.dumps(engine.cast(eph, *c, now_jd=NOW)))
        bad = compare(js, py)
        jd_d = eph.q(f='dasha', args=c + [NOW], now=NOW)
        py_d = json.loads(json.dumps(engine.dasha_tree(py, NOW)))
        bad += compare(jd_d, py_d, 'dasha')
        if bad: fails += 1; print('MISMATCH', c, bad[:5])
    print(f'{len(cases) - fails}/{len(cases)} charts match the console (chart + dasha tree)')
    sys.exit(1 if fails else 0)
