import sys
import numpy as np
from datetime import datetime as dt
from datetime import time as dtime
from datetime import timedelta
import pandas as pd
import datetime
from time import mktime
import jellyfish as fish
import matplotlib.pyplot as plt


def get_devices(lines):
    return lines[:, 2]


def get_exits(lines):
    return lines[:, -1]


def get_stations(data, name, trains=None):
    f1 = data[np.where(data[:, 3] == name)]
    if trains is not None:
        f1 = f1[np.where(f1[:, 4] == trains)]
    return f1


def get_recent_elements(data):
    dates = set(data[:, 6].tolist())
    ts = [(mktime(dt.strptime(d, '%m/%d/%Y').timetuple()), d) for d in dates]
    ts.sort()
    return ts[-1][1]


def get_windows(data, windows):
    s = datetime.datetime(1, 1, 1, 0, 0, 0)
    output = []
    ts = windows
    for t in ts:
        start = (s + timedelta(minutes=t[0])).time()
        finish = (s + timedelta(minutes=t[1])).time()
        n1 = get_entries(data, start, finish, take_last=True, stds=4)
        output.append(n1)
    return output


def replace_ids(group):
    mean, std = group.mean(), group.std()
    outliers = (group - mean).abs() > 5 * std
    group[outliers] = np.nan
    return group


def replace(group):
    mean, std = group.mean(), group.std()
    outliers = (group - mean).abs() > 2 * std
    group[outliers] = group[~outliers].mean()
    return group


def get_entries(data, tfrom, tto, take_last=False, stds=0.01):
    ix = data.index.indexer_between_time(tfrom, tto)
    inrange = data.ix[ix]
    devices = inrange.groupby(["UNIT", "SCP", "STATION", "weekday", "LINENAME", "DIVISION"])
    diffed = devices.ENTRIES.apply(lambda x: x[-1] - x[0])
    diffed[diffed < 0] = np.nan
    new_vals = diffed.reset_index().groupby(["STATION", "LINENAME"]).transform(replace)

    for i, k in enumerate(diffed.keys()):
        diffed[k] = new_vals.ENTRIES[i]

    cleaned = diffed.fillna(method='pad')
    out = cleaned.reset_index().groupby(["STATION", "LINENAME"]).sum()
    return out


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


def station_query_format(station, trains):
    sys.stdout.write(station)
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
    differences = str([float(a) - float(b) for (a, b) in zip(e1[:-1], e2[:-1])])
    clean_differences = differences.replace("[", ",").replace("]", "").replace(" ", "")
    return clean_differences


def get_commute_totals(lines, station, trains=None):
    station_query_format(station, trains)
    print get_stations(lines, station, trains)


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


def balance(lesser, greater):
    lesser_sum = np.sum(lesser.ENTRIES)
    greater_sum = np.sum(greater.ENTRIES)
    count = greater_sum - lesser_sum
    ps = lesser.ENTRIES / lesser_sum
    correction = np.random.multinomial(count, ps, 1)[0]
    lesser.ENTRIES = lesser.ENTRIES + correction
    return lesser


def read_data():
    print "reading turnstile data"
    data = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else "data/turnstile_160507.txt")
    new_dates = data.DATE.apply(str) + "-" + data.TIME.apply(str)
    data.index= pd.to_datetime(new_dates.apply(str), format="%m/%d/%Y-%H:%M:%S")
    data["weekday"] = data.index.dayofweek
    data["LINENAME"] = data["LINENAME"].map(lambda x: "".join(sorted(x)))
    return data


def clean_data(data):
    data = data[data.DIVISION != "PTH"]
    data = data[data.weekday < 5]
    return data


def compute_commute(plot=False):
    data = read_data()
    data = clean_data(data)
    interval_data = get_windows(data, [(0*60, 17 * 60), (17 * 60, 24 * 60)])
    s = np.sum([interval_data[0].ENTRIES, interval_data[1].ENTRIES], axis=1)
    if s[0] > s[1]:
        interval_data[1] = balance(lesser=interval_data[1], greater=interval_data[0])
    else:
        interval_data[0] = balance(lesser=interval_data[0], greater=interval_data[1])

    if plot:
        for d in interval_data:
            plt.plot(d.ENTRIES, c='k', alpha=0.4)

    m = np.mean([interval_data[0].ENTRIES, interval_data[1].ENTRIES], axis=1)
    interval_data[0]["EXITS"] = interval_data[1].ENTRIES
    interval_data[0]["NET"] = interval_data[0].ENTRIES - interval_data[1].ENTRIES
    if plot:
        plt.plot(m, alpha=1)
        plt.show()
    return interval_data[0].reset_index()


def main():
    commute_data = compute_commute()
    return commute_data

_commute_data = main()


def commuter_matching(search):
    def lines_in_common(x):
        return sum(x.LINENAME.count(c) for c in search.trains) / float(max(len(x.LINENAME), len(search.trains)))

    def d(x):
        stops_name_sim = fish.jaro_winkler(unicode(x.STATION.lower()), unicode(search.stop_name.lower()))
        se_name_sim = fish.jaro_winkler(unicode(x.STATION.lower()), unicode(search.Station_Name.lower()))
        lic = lines_in_common(x)
        return stops_name_sim + se_name_sim + lic

    similarity = _commute_data.apply(d, axis=1)
    i = np.argmax(similarity)
    return _commute_data.iloc[i], similarity[i]

