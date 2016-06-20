import csv
import sys
import numpy as np
from datetime import datetime as dt
from datetime import time as dtime
from datetime import timedelta
import pandas as pd
import datetime
from time import mktime
import matplotlib.pyplot as plt



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
    times =  set(data[:, 7].tolist())
    ts = [(mktime(dt.strptime(d, '%m/%d/%Y').timetuple()), d) for d in dates]
    ts.sort()
    # print sorted(list(times))
    return ts[-1][1]


def get_cdf(data, interval=20):
    s= datetime.datetime(1,1,1,0,0,0)
    output = []
    t = 0
    while (s+timedelta(minutes=t)).day == 1:
        n1 = get_entries(data, s.time(), (s + timedelta(minutes=t)).time(), take_last=True, stds=4)
        output.append(n1.ENTRIES)
        t += interval
    output = np.array(output[4:])
    output = np.vstack((np.zeros(output.shape)[0:4], output))

    return output.transpose()


def get_entries(data, tfrom, tto, take_last=False, stds = 0.01):

    ix = data.index.indexer_between_time(tfrom, tto)
    inrange = data.ix[ix]
    devices = inrange.groupby(["UNIT", "SCP", "STATION", "weekday"])

    print "003"
    diffed = devices.ENTRIES.apply(lambda x: x[-1] - x[0])
    diffed[diffed < 0] = np.nan
    diffed[np.abs(diffed - diffed.mean()) > stds * diffed.std()] = np.nan
    # def replace(x):
    #     print(x)
    #
    #     return x
    # with_nans = diffed.apply(lambda x: replace(x))

    # print "002"
    cleaned = diffed.fillna(method='pad').reset_index()
    # print "004"
    return cleaned.groupby(["STATION"]).sum()

def get_total_entries(data, p=False):
    recent_date = get_recent_elements(data)

    f1 = data[np.where(data[:, 6] == recent_date)]
    permissible_times = list(set(f1[:, 7].tolist()))
    permissible_times.sort()
    def_time = permissible_times[0]
    f2 = f1[np.where(f1[:, 7] == def_time)]

    if p:
        sys.stdout.write(" " + str(len(f2)) + " turnstiles ")
        sys.stdout.flush()
    in_total = np.sum(f2[:, -2].astype(int))
    out_total = np.sum(f2[:, -1].astype(int))
    return in_total, out_total, in_total + out_total, len(f2)

format_date = lambda x: "{0}:{1}:{2}".format(x.hour, x.minute, x.second)


def filter_data_interval(data, t, interval):
    start = dt(1, 1, 1, t.hour, t.minute, t.second)
    end = start + interval
    after = data[np.where(data[: 7] > start)]
    filtered = after[np.where(after[: 7] <= end)]
    assert start.hour <= end.hour
    return filtered

def get_totals_interval(data, start=dtime(5, 0, 0), finish=dtime(16, 0, 0), interval=timedelta(hours=3)):
    """
    :param data : expected to be filtered for a single station already
    :param start : datetime.time object beginning for first (morning) interval
    :param finish: datetime.time object beginning for second (evening) interval
    :param interval: length of interval
    :return: start and finish entrance totals
    """
    dates = set(data[:, 6].tolist())
    for date in dates:
        same_day = data[np.where(data[:, 6] == date)]
        filtered_morning = filter_data_interval(same_day, start, interval)
        filtered_evening = filter_data_interval(same_day, finish, interval)
        in_total_morn = np.sum(filtered_morning[:, -2].astype(int))
        in_total_eve = np.sum(filtered_evening[:, -2].astype(int))

def get_commute_io(data):
    pass


def station_query_format(station, trains):
    sys.stdout.write(station)
    sys.stdout.flush()
    if trains:
        sys.stdout.write(" " + str(trains))
        sys.stdout.flush()


def get_weekly_totals(lines_fin, lines_start, station, trains=None):
    station_query_format(station, trains)
    mw = get_stations(lines_fin, station, trains)
    e1 = get_total_entries(mw)
    mw = get_stations(lines_start, station, trains)
    e2 = get_total_entries(mw)
    if e1[-1] != e2[-1]:
        return "na,na,na"
    return str([float(a) - float(b) for (a, b) in zip(e1[:-1], e2[:-1])]).replace("[", ",").replace("]", "").replace(" ", "")


def get_commute_totals(lines, station, trains=None):
    station_query_format(station, trains)
    lines_for_station = get_stations(lines, station, trains)


    print get_stations(lines, station, trains)

#
# with open(sys.argv[1]) as f:
#     lines_f = np.array([l for l in csv.reader(f)][1:])
#     f.close()
# with open(sys.argv[2]) as f:
#     lines_s = np.array([l for l in csv.reader(f)][1:])
#     f.close()
#

def iter_weekly_stations(lines_f, lines_s):
    station_strs = lines_s[:, 3:5].tolist()

    station_names = list(set([(str(a[0]), str(a[1])) for a in station_strs]))
    station_names.sort()
    visited = {}
    for s in station_names:
        try:
            a = visited[str(sorted(s[1]))]
        except KeyError:
            visited[str(sorted(s[1]))] = True
            print get_weekly_totals(lines_f, lines_s, s[0])


def iter_commute_totals(lines):
    station_strs = lines[:, 3:5].tolist()
    station_names = list(set([(str(a[0]), str(a[1])) for a in station_strs]))
    station_names.sort()
    visited_c = {}
    for s in station_names:
        try:
            a = visited_c[str(sorted(s[1]))]
        except KeyError:
            visited_c[str(sorted(s[1]))] = True
            print get_commute_totals(lines, s[0])


#print("station,entrances,exits,totals")
#

def do_dit():
    data = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else "data/turnstile_160507.txt")
    data.index= pd.to_datetime((data.DATE.apply(str) + "-" + data.TIME.apply(str)).apply(str), format="%m/%d/%Y-%H:%M:%S")
    data["weekday"] = data.index.dayofweek

    a = get_cdf(data, 60)

    for d in a:
        plt.scatter(np.diff(d), np.array(xrange(len(d)-1)), c='k', alpha=0.04)
    m = np.diff(np.mean(a, axis=0))
    plt.bar(m, np.array(xrange(len(m))), alpha=1)
    plt.show()

do_dit()

# if station name is not unique we must also specify the trains that arrive there,
# otherwise we are counting multiple stations

#
# print get_weekly_totals(lines_f, lines_s, "MYRTLE-WYCKOFF")
# print get_weekly_totals(lines_f, lines_s, "DEKALB AV", "L")
# print get_weekly_totals(lines_f, lines_s, "HALSEY ST", "L")
# print get_weekly_totals(lines_f, lines_s, "SENECA AVE")
# print get_weekly_totals(lines_f, lines_s, "KNICKERBOCKER")
# print get_weekly_totals(lines_f, lines_s, "TIMES SQ-42 ST")
# print get_weekly_totals(lines_f, lines_s, "BERGEN ST")
# print get_weekly_totals(lines_f, lines_s, "CARROLL ST")
# print get_weekly_totals(lines_f, lines_s, "JEFFERSON ST")
# print get_weekly_totals(lines_f, lines_s, "CENTRAL AV")
# print get_weekly_totals(lines_f, lines_s, "FOREST AVE")

# iter_weekly_stations(lines_f, lines_s)
#iter_commute_totals(lines_s)
