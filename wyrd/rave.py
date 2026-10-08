"""The rave's centres and channels, as on the harmonic body (static/body.js),
so the reading can say what a rave defines."""
CENTRES = {
    "head":   ("Head",   [64, 61, 63]),
    "ajna":   ("Ajna",   [47, 24, 4, 17, 43, 11]),
    "throat": ("Throat", [62, 23, 56, 35, 12, 45, 33, 8, 31, 20, 16]),
    "g":      ("G",      [1, 13, 25, 46, 2, 15, 10, 7]),
    "heart":  ("Heart",  [21, 40, 26, 51]),
    "spleen": ("Spleen", [48, 57, 44, 50, 32, 28, 18]),
    "solar":  ("Solar",  [36, 22, 37, 6, 49, 55, 30]),
    "sacral": ("Sacral", [34, 5, 14, 29, 59, 9, 3, 42, 27]),
    "root":   ("Root",   [53, 60, 52, 19, 39, 41, 58, 38, 54]),
}
CHANNELS = [(1, 8), (2, 14), (3, 60), (4, 63), (5, 15), (6, 59), (7, 31), (9, 52), (10, 20), (10, 34), (10, 57), (11, 56),
            (12, 22), (13, 33), (16, 48), (17, 62), (18, 58), (19, 49), (20, 34), (20, 57), (21, 45), (23, 43), (24, 61),
            (25, 51), (26, 44), (27, 50), (28, 38), (29, 46), (30, 41), (32, 54), (34, 57), (35, 36), (37, 40), (39, 55),
            (42, 53), (47, 64)]
CENTRE_OF = {g: k for k, (_, gates) in CENTRES.items() for g in gates}


def gates(rave):
    return {v["gate"] for side in ("personality", "design") for v in rave[side].values()}


def defines(rave):
    """The channels a rave completes and the centres they define, in body order."""
    have = gates(rave)
    live = [c for c in CHANNELS if c[0] in have and c[1] in have]
    centres = {CENTRE_OF[g] for c in live for g in c}
    return live, [CENTRES[k][0] for k in CENTRES if k in centres]
