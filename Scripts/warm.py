"""Run at build time: downloads NASA JPL DE440s (~32 MB) into data/ so the
first visitor never waits, then casts one chart to prove the stack works."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from wyrd.ephemeris import Ephemeris
from wyrd import engine
eph = Ephemeris(config.DATA_DIR, config.EPHEMERIS_FILE)
c = engine.cast(eph, 2000, 1, 1, 12, 51.48, 0.0)
print("ephemeris ready · J2000 Sun", round(c["trop"]["Sun"], 4), "· ayanamsa", round(c["ay"], 5))
