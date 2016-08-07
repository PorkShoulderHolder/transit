__author__ = 'sam.royston'

import jellyfish as fish
from geopy.distance import great_circle
from station_locations import StationLocationReader
from utils import default_data_dir, debug
import pandas as pd
import numpy as np


class TopologyReader(object):
    def __init__(self, data_dir=default_data_dir(), verbose=False):
        self.verbose = verbose
        self.data_dir = data_dir
        _name_key, _data = self.clean_stops_file(self.read_file(self.data_dir + "/google_transit/stops.txt"))
        self.name_key = _name_key
        self.data = _data
        self.travel_times = self.cache_connections_data()
        self.merged_stops = self.merge_stops_entrances(_data)

    @staticmethod
    def read_file(filename):
        data = pd.read_csv(filename)
        return data

    @staticmethod
    def get_code_equivalencies(groups, data):
        equivalencies = groups.parent_station.apply(lambda x: x.drop_duplicates().dropna().tolist())

        def get_locs(x):
            matches = [data[data.stop_id == i] for i in x]
            lls = np.array([(m.stop_lat.values[0], m.stop_lon.values[0]) for m in matches])
            return lls

        def get_std(x):
            lls = get_locs(x)
            return np.mean(np.std(lls, axis=0))

        std_dev_locs = equivalencies.apply(get_std)
        loc_list = equivalencies.apply(get_locs)
        return equivalencies, std_dev_locs, loc_list

    @debug
    def clean_stops_file(self, data):
        getline = lambda x: x[0]
        strsort = lambda x : "".join(sorted(x))
        data["line"] = data.stop_id.map(getline)
        data.line = data.line.map(strsort)
        name_grps = data.groupby(["stop_name"])
        out = name_grps.mean().reset_index()
        codes, agrmt, loc_list = self.get_code_equivalencies(name_grps, data)
        out["codes_for_name"] = codes.values
        out["location_agreement"] = agrmt.values
        out["locations"] = loc_list.values
        dout = data.groupby(["parent_station"]).last().reset_index()
        f = lambda x: out.codes_for_name[out.codes_for_name.apply(lambda y: x in y) == 1].values[0]

        def remove_staten(x):
            return str(x)[0] == "S" and int(str(x)[1:]) >= 9

        related_by_name = dout.parent_station.apply(f)
        dout["related_by_name"] = related_by_name.values
        dout = dout.drop(dout[dout.parent_station.apply(remove_staten) == 1].index)
        return out, dout

    def get_ids_distance(self, id1, id2):
        e1 = self.data[self.data.parent_station == id1]
        e2 = self.data[self.data.parent_station == id2]
        if not (e1.empty or e2.empty):
            latlng_1 = (e1.stop_lat.values[0], e1.stop_lon.values[0])
            latlng_2 = (e2.stop_lat.values[0], e2.stop_lon.values[0])
            return great_circle(latlng_1, latlng_2).meters
        else:
            return float("inf")

    def clean_stoptimes_file(self, data):
        remove_weird_times = lambda x: "0" + str(int(x[0:2]) - 24) + x[2:] if int(x[0:2]) >= 24 else x
        data.arrival_time = data.arrival_time.apply(remove_weird_times)
        data.departure_time = data.departure_time.apply(remove_weird_times)
        data.arrival_time = pd.to_datetime(data.arrival_time, format="%H:%M:%S")
        data.departure_time = pd.to_datetime(data.departure_time, format="%H:%M:%S")
        get_parent = lambda x: x[:3]
        evens = data.iloc[::2, :].reset_index()
        odds = data.iloc[1::2, :].reset_index()
        evens.rename(columns={'stop_id': 'source'}, inplace=True)
        odds.rename(columns={'stop_id': 'target'}, inplace=True)
        evens.rename(columns={'arrival_time': 'source_arrival'}, inplace=True)
        odds.rename(columns={'arrival_time': 'target_arrival'}, inplace=True)

        evens2 = data.iloc[2::2, :].reset_index()
        odds2 = data.iloc[1:-1:2, :].reset_index()
        evens2.rename(columns={'stop_id': 'source'}, inplace=True)
        odds2.rename(columns={'stop_id': 'target'}, inplace=True)
        evens2.rename(columns={'arrival_time': 'source_arrival'}, inplace=True)
        odds2.rename(columns={'arrival_time': 'target_arrival'}, inplace=True)
        even_pairs = pd.concat([evens.source.map(get_parent), odds.target.map(get_parent),
                                evens.source_arrival, odds.target_arrival], axis=1)
        odd_pairs = pd.concat([odds2.target.map(get_parent), evens2.source.map(get_parent),
                               evens2.source_arrival, odds2.target_arrival], axis=1)

        to_mins = lambda x: x.seconds / 60 if not pd.isnull(x) else np.nan
        odd_pairs["travel_time"] = (odd_pairs.source_arrival - odd_pairs.target_arrival).apply(to_mins)
        even_pairs["travel_time"] = (even_pairs.target_arrival - even_pairs.source_arrival).apply(to_mins)
        out = pd.concat([even_pairs, odd_pairs])
        out = out.drop(["source_arrival", "target_arrival"])
        out = out[out.travel_time <= 20]
        out = out[out.travel_time >= 0]
        out = out.groupby(["source", "target"]).mean().reset_index()
        out["distances"] = out.apply(lambda x: self.get_ids_distance(str(x.source), str(x.target)), axis=1)
        out = out[out.distances < 6500.0]
        out = out[out.distances > 0]
        out["is_transfer"] = np.zeros(len(out))
        return out

    @debug
    def merge_stops_entrances(self, stops):
        stl_reader = StationLocationReader()
        e_matches = stops.apply(lambda x: stl_reader.closest_match_latlng(x), axis=1)
        ms = pd.concat((stops, e_matches), axis=1)
        neq = ms.apply(lambda x: filter(lambda y: str(y)[0] in x.trains, x.related_by_name), axis=1)
        ms["filtered_codes"] = neq
        return ms

    @debug
    def merge_turnstile_info(self, turnstile_reader):
        ts_matches = self.merged_stops.apply(lambda x: turnstile_reader.commuter_matching(x)[0], axis=1)
        ts_similarity = self.merged_stops.apply(lambda x: turnstile_reader.commuter_matching(x)[1], axis=1)
        md = pd.concat((self.merged_stops, ts_matches), axis=1)
        md["turnstile_matching_similarity"] = ts_similarity
        md["Id"] = md.parent_station
        md["latitude"] = md.stop_lat
        md["longitude"] = md.stop_lon
        md["Label"] = md.apply(lambda x: x.stop_name + "_" + x.LINENAME, axis=1)
        return md

    def cache_connections_data(self, fn="data/cleaned_connections.csv"):
        conns_data = self.clean_stoptimes_file(self.read_file(self.data_dir + "/google_transit/stop_times.txt"))
        return conns_data

    def lat_lng_distances(self, lat_lng, entrance_data):
        d = lambda x: great_circle(lat_lng, (x.stop_lat, x.stop_lon)).meters
        return self.data.apply(d, axis=1)

    def closest_match_neighbors(self, search_name):
        line_penalty = lambda x: 100 * (x.parent_station[0] in search_name.split("_")[-1])
        d = lambda x: fish.jaro_winkler(unicode(x.stop_name.lower()), unicode(search_name.lower())) + line_penalty(x)
        distances = self.data.apply(d, axis=1)
        i = np.argmax(distances)
        return self.data.stop_name[i], self.data.stop_lat[i], self.data.stop_lon[i], self.data.parent_station[i]
