__author__ = 'sam.royston'
import pandas as pd
import numpy as np
from postprocessing import switch_src_target

BQX_conns = np.array([
    ["R41", "R36", 12.0, 0, 0],
    ["R36", "231", 21.0, 0, 0],
    ["231", "A40", 6.0, 0, 0],
    ["A40", "F18", 7.0, 0, 0],
    ["F18", "L08", 15.0, 0, 0],
    ["L08", "G26", 6.0, 0, 0],
    ["G26", "F09", 7.0, 0, 0],
    ["F09", "G24", 6.0, 0, 0],
    ["G24", "R04", 6.0, 0, 0]
])
BQX_conns = pd.DataFrame(np.vstack((BQX_conns,BQX_conns)),
                         columns=["source", "target", "travel_time", "distance", "is_transfer"])
BQX_conns = switch_src_target(BQX_conns)
# 98 mins total
TRIBORO_conns = np.array(
[
    ["613", "R01", 12.0, 0, 0],
    ["221", "R01", 11.0, 0, 0],
    ["R01", "G14", 9.0, 0, 0],
    ["G14", "M01", 8.0, 0, 0],
    ["M01", "L20", 8.0, 0, 0],
    ["L20", "L24", 6.0, 0, 0],
    ["L24", "L26", 5.0, 0, 0],
    ["L26", "254", 2.0, 0, 1],
    ["254", "247", 12.0, 0, 0],
    ["247", "D32", 5.0, 0, 0],
    ["D32", "F31", 5.0, 0, 0],
    ["F31", "N04", 6.0, 0, 0],
    ["N04", "B16", 2.0, 0, 1],
    ["B16", "R41", 7.0, 0, 0]
])
TRIBORO_conns = pd.DataFrame(np.vstack((TRIBORO_conns, TRIBORO_conns)),
                             columns=["source", "target", "travel_time", "distance", "is_transfer"])

TRIBORO_conns = switch_src_target(TRIBORO_conns)
