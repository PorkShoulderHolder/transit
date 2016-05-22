import csv
import sys
import numpy as np
from datetime import datetime as dt
from time import mktime


def get_devices(lines):
    return lines[:, 2]


def get_exits(lines):
    return lines[:, -1]


def get_entries(lines):
    return lines[:, -2]


def get_stations(data, name, trains=None):
    f1 = data[np.where(data[:, 3] == name)]
    if trains is not None:
        f1 = f1[np.where(f1[:, 4] == trains)]
    return f1


def get_datetime(line):
    pass


def get_recent_elements(data):
    dates = set(data[:, 6].tolist())
    ts = [(mktime(dt.strptime(d, '%m/%d/%Y').timetuple()), d) for d in dates]
    ts.sort()
    return ts[-1][1]


def get_total_entries(data, p=False):
    recent_date = get_recent_elements(data)
    permissible_times = list(set(data[:, 7].tolist()))
    permissible_times.sort()
    # print "permissible times: " + str(permissible_times)
    def_time = permissible_times[0]
    f1 = data[np.where(data[:, 6] == recent_date)]
    f2 = f1[np.where(f1[:, 7] == def_time)]
    assert len(f2) > 0
    if p:
        sys.stdout.write(" " + str(len(f2)) + " turnstiles ")
        sys.stdout.flush()
    in_total = np.sum(f2[:, -2].astype(int))
    out_total = np.sum(f2[:, -1].astype(int))
    return in_total, out_total, in_total + out_total


def get_totals(station, trains=None):
    e1 = 0
    e2 = 0
    sys.stdout.write(station)
    sys.stdout.flush()
    with open(sys.argv[1]) as f:
        lines = np.array([l for l in csv.reader(f)])
        mw = get_stations(lines, station, trains)
        e1 = get_total_entries(mw)
        f.close()
    with open(sys.argv[2]) as f:
        lines = np.array([l for l in csv.reader(f)])
        mw = get_stations(lines, station, trains)
        e2 = get_total_entries(mw)
        f.close()
    return str([a - b for (a, b) in zip(e1, e2)]).replace("[", ",").replace("]", "").replace(" ", "")

print("station,entrances,exits,totals")
print get_totals("MYRTLE-WYCKOFF")

# if station name is not unique we must also specify the trains that arrive there,
# otherwise we are counting multiple stations
print get_totals("DEKALB AV", "L")
print get_totals("HALSEY ST", "L")
print get_totals("SENECA AVE")
print get_totals("KNICKERBOCKER")
print get_totals("TIMES SQ-42 ST")
print get_totals("BERGEN ST")
print get_totals("CARROLL ST")
print get_totals("JEFFERSON ST")
print get_totals("CENTRAL AV")
print get_totals("FOREST AVE")

