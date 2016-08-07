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
from turnstile_synch import UpdateManager
import sys
from utils import default_data_dir, debug


class TurnstileReader(object):
    def __init__(self, data_dir=None, file_path=None, verbose=False):
        self.verbose = verbose
        data_dir = data_dir if data_dir is not None else default_data_dir()
        self.data_dir = data_dir
        if file_path is None:
            file_path = UpdateManager.get_most_recent(data_dir)
        self.file_path = file_path
        self.data = None
        self.read_data()
        self.commute_data = self.compute_commute()

    @staticmethod
    def get_devices(lines):
        return lines[:, 2]

    @staticmethod
    def get_exits(lines):
        return lines[:, -1]

    @staticmethod
    def get_stations(data, name, trains=None):
        f1 = data[np.where(data[:, 3] == name)]
        if trains is not None:
            f1 = f1[np.where(f1[:, 4] == trains)]
        return f1

    @staticmethod
    def get_recent_elements(self, data):
        dates = set(data[:, 6].tolist())
        ts = [(mktime(dt.strptime(d, '%m/%d/%Y').timetuple()), d) for d in dates]
        ts.sort()
        return ts[-1][1]

    def get_windows(self, data, windows):
        s = datetime.datetime(1, 1, 1, 0, 0, 0)
        output = []
        ts = windows
        for t in ts:
            start = (s + timedelta(minutes=t[0])).time()
            finish = (s + timedelta(minutes=t[1])).time()
            n1 = self.get_entries(start, finish)
            output.append(n1)
        return output

    @staticmethod
    def replace_ids(group):
        mean, std = group.mean(), group.std()
        outliers = (group - mean).abs() > 5 * std
        group[outliers] = np.nan
        return group

    @staticmethod
    def replace(group):
        mean, std = group.mean(), group.std()
        outliers = (group - mean).abs() > 2 * std
        group[outliers] = group[~outliers].mean()
        return group

    def get_entries(self, tfrom, tto):
        ix = self.data.index.indexer_between_time(tfrom, tto)
        inrange = self.data.ix[ix]
        devices = inrange.groupby(["UNIT", "SCP", "STATION", "weekday", "LINENAME", "DIVISION"])
        diffed = devices.ENTRIES.apply(lambda x: x[-1] - x[0])
        diffed[diffed < 0] = np.nan
        new_vals = diffed.reset_index().groupby(["STATION", "LINENAME"]).transform(TurnstileReader.replace)

        for i, k in enumerate(diffed.keys()):
            diffed[k] = new_vals.ENTRIES[i]

        cleaned = diffed.fillna(method='pad')
        out = cleaned.reset_index().groupby(["STATION", "LINENAME"]).sum()
        return out

    def get_total_entries(self, data, p=False):
        recent_date = self.get_recent_elements(data)

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

    def filter_data_interval(self, same_day,  t, interval):
        start = dt(1, 1, 1, t.hour, t.minute, t.second)
        end = start + interval
        after = same_day[np.where(self.data[: 7] > start)]
        filtered = after[np.where(after[: 7] <= end)]
        assert start.hour <= end.hour
        return filtered

    def get_totals_interval(self, data, start=dtime(5, 0, 0), finish=dtime(16, 0, 0), interval=timedelta(hours=3)):
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
            filtered_morning = self.filter_data_interval(same_day, start, interval)
            filtered_evening = self.filter_data_interval(same_day, finish, interval)
            in_total_morn = np.sum(filtered_morning[:, -2].astype(int))
            in_total_eve = np.sum(filtered_evening[:, -2].astype(int))

    @staticmethod
    def station_query_format(station, trains):
        sys.stdout.write(station)
        sys.stdout.write(station)
        sys.stdout.flush()
        if trains:
            sys.stdout.write(" " + str(trains))
            sys.stdout.flush()

    def get_weekly_totals(self, lines_fin, lines_start, station, trains=None):
        self.station_query_format(station, trains)
        mw = self.get_stations(lines_fin, station, trains)
        e1 = self.get_total_entries(mw)
        mw = self.get_stations(lines_start, station, trains)
        e2 = self.get_total_entries(mw)
        if e1[-1] != e2[-1]:
            return "na,na,na"
        differences = str([float(a) - float(b) for (a, b) in zip(e1[:-1], e2[:-1])])
        clean_differences = differences.replace("[", ",").replace("]", "").replace(" ", "")
        return clean_differences

    def get_commute_totals(self, lines, station, trains=None):
        self.station_query_format(station, trains)
        return self.get_stations(lines, station, trains)

    @debug
    def balance(self, lesser, greater):
        lesser_sum = np.sum(lesser.ENTRIES)
        greater_sum = np.sum(greater.ENTRIES)
        count = greater_sum - lesser_sum
        ps = lesser.ENTRIES / lesser_sum
        correction = np.random.multinomial(count, ps, 1)[0]
        lesser.ENTRIES = lesser.ENTRIES + correction
        return lesser

    @debug
    def read_data(self):
        self.data = pd.read_csv(self.file_path, compression="gzip")
        new_dates = self.data.DATE.apply(str) + "-" + self.data.TIME.apply(str)
        self.data.index= pd.to_datetime(new_dates.apply(str), format="%m/%d/%Y-%H:%M:%S")
        self.data["weekday"] = self.data.index.dayofweek
        self.data["LINENAME"] = self.data["LINENAME"].map(lambda x: "".join(sorted(x)))
        return self.data

    @staticmethod
    def clean_data(data):
        data = data[data.DIVISION != "PTH"]
        data = data[data.weekday < 5]
        return data

    def compute_commute(self, plot=False):
        data = self.read_data()
        data = self.clean_data(data)
        interval_data = self.get_windows(data, [(0*60, 17 * 60), (17 * 60, 24 * 60)])
        s = np.sum([interval_data[0].ENTRIES, interval_data[1].ENTRIES], axis=1)
        if s[0] > s[1]:
            interval_data[1] = self.balance(lesser=interval_data[1], greater=interval_data[0])
        else:
            interval_data[0] = self.balance(lesser=interval_data[0], greater=interval_data[1])

        if plot:
            for d in interval_data:
                plt.plot(d.ENTRIES, c='k', alpha=0.4)

        m = np.mean([interval_data[0].ENTRIES, interval_data[1].ENTRIES], axis=1)
        interval_data[0]["EXITS"] = interval_data[1].ENTRIES
        interval_data[0]["NET"] = interval_data[0].ENTRIES - interval_data[1].ENTRIES
        if plot:
            plt.plot(m, alpha=1)
            plt.show()
        commute_data = interval_data[0].reset_index()
        return commute_data

    def commuter_matching(self, search):
        def lines_in_common(x):
            return sum(x.LINENAME.count(c) for c in search.trains) / float(max(len(x.LINENAME), len(search.trains)))

        def d(x):
            stops_name_sim = fish.jaro_winkler(unicode(x.STATION.lower()), unicode(search.stop_name.lower()))
            se_name_sim = fish.jaro_winkler(unicode(x.STATION.lower()), unicode(search.Station_Name.lower()))
            lic = lines_in_common(x)
            return stops_name_sim + se_name_sim + lic

        similarity = self.commute_data.apply(d, axis=1)
        i = np.argmax(similarity)
        return self.commute_data.iloc[i], similarity[i]

