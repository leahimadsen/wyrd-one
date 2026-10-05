"""
Planet positions from NASA JPL's DE440 via Skyfield — free, open source,
and the same JPL data Swiss Ephemeris is compressed from.

Conventions, chosen to match what Swiss Ephemeris and Jyotish software return:
  * tropical longitudes are apparent geocentric, on the true ecliptic of date
  * Lahiri ayanamsa from its definition (23 deg 15' 00.658" at 21 Mar 1956,
    carried by IAU 2006 general precession), plus nutation so that
    sidereal = tropical - ayanamsa agrees with apparent positions
  * Rahu is the mean node, as in the console; Ketu is opposite
"""
import math
from functools import lru_cache

from skyfield.api import Loader
from skyfield.framelib import ecliptic_frame

try:                                         # Skyfield >= 1.31
    from skyfield.nutationlib import iau2000a_radians as _nutation
except ImportError:                          # older Skyfield
    from skyfield.nutationlib import iau2000a as _iau2000a
    def _nutation(t):
        dpsi, deps = _iau2000a(t.tt)         # tenths of a micro-arcsecond
        k = 1e-7 / 3600.0 * math.pi / 180.0
        return dpsi * k, deps * k

D2R, R2D = math.pi / 180, 180 / math.pi
norm = lambda d: ((d % 360) + 360) % 360

LAHIRI_T0 = 2435553.5                        # 1956 Mar 21, 0h TT
LAHIRI_AY0 = 23.250182778 - 0.004658035      # mean ayanamsa at T0, degrees

def _precession_arcsec(jd_tt):
    """IAU 2006 general precession in longitude since J2000, arcseconds."""
    T = (jd_tt - 2451545.0) / 36525.0
    return (5028.796195 * T + 1.1054348 * T**2 + 0.00007964 * T**3
            - 0.000023857 * T**4 - 0.0000000383 * T**5)

def _mean_obliquity_deg(jd_tt):
    T = (jd_tt - 2451545.0) / 36525.0
    return (84381.406 - 46.836769 * T - 0.0001831 * T**2 + 0.00200340 * T**3
            - 0.000000576 * T**4 - 0.0000000434 * T**5) / 3600.0

NAMES = {
    "Sun": ["sun"], "Moon": ["moon"],
    "Mercury": ["mercury", "mercury barycenter"], "Venus": ["venus", "venus barycenter"],
    "Mars": ["mars barycenter", "mars"], "Jupiter": ["jupiter barycenter"],
    "Saturn": ["saturn barycenter"], "Uranus": ["uranus barycenter"],
    "Neptune": ["neptune barycenter"], "Pluto": ["pluto barycenter"],
}

class Ephemeris:
    def __init__(self, data_dir, bsp="de440s.bsp"):
        load = Loader(data_dir)
        self.ts = load.timescale()
        self.kernel = load(bsp)
        self.earth = self.kernel["earth"]
        self.bodies = {}
        for name, keys in NAMES.items():
            for k in keys:
                try:
                    self.bodies[name] = self.kernel[k]; break
                except KeyError:
                    continue
            else:
                raise RuntimeError(f"{bsp} has no segment for {name}")

    def _t(self, jd_ut):
        return self.ts.ut1_jd(jd_ut)

    def _lon(self, t, body):
        lat, lon, _ = self.earth.at(t).observe(self.bodies[body]).apparent().frame_latlon(ecliptic_frame)
        return lon.degrees % 360

    @lru_cache(maxsize=4096)
    def sun_lon(self, jd_ut):
        return self._lon(self._t(jd_ut), "Sun")

    @lru_cache(maxsize=1024)
    def positions(self, jd_ut):
        t = self._t(jd_ut)
        p = {b: self._lon(t, b) for b in NAMES}
        p["Rahu"] = self._mean_node(t.tt)
        p["Ketu"] = norm(p["Rahu"] + 180)
        return p

    @staticmethod
    def _mean_node(jd_tt):
        T = (jd_tt - 2451545.0) / 36525.0
        return norm(125.0445479 - 1934.1362891 * T + 0.0020754 * T * T
                    + T ** 3 / 467441 - T ** 4 / 60616000)

    @lru_cache(maxsize=1024)
    def ayanamsa(self, jd_ut):
        t = self._t(jd_ut)
        mean = LAHIRI_AY0 + (_precession_arcsec(t.tt) - _precession_arcsec(LAHIRI_T0)) / 3600.0
        dpsi, _ = _nutation(t)
        return mean + float(dpsi) * R2D

    def angles(self, jd_ut, lat, lon_e):
        """Tropical Ascendant and Midheaven on the true ecliptic of date."""
        t = self._t(jd_ut)
        _, deps = _nutation(t)
        eps = _mean_obliquity_deg(t.tt) + float(deps) * R2D
        ramc = norm(t.gast * 15.0 + lon_e)
        s, c = math.sin, math.cos
        asc = math.atan2(c(ramc * D2R),
                         -(s(ramc * D2R) * c(eps * D2R) + math.tan(lat * D2R) * s(eps * D2R))) * R2D
        mc = math.atan2(s(ramc * D2R), c(ramc * D2R) * c(eps * D2R)) * R2D
        return norm(asc), norm(mc)
