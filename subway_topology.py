__author__ = 'sam.royston'
__author__ = 'sam.royston'
import pandas as pd
import csv
from datetime import datetime as dt
import numpy as np
import editdistance as lev
import jellyfish as fish
import sys
from geopy.distance import great_circle
from station_locations import *

def print_all(x):
    pd.set_option('display.max_rows', len(x))
    print(x.to_csv(None, index=False ))
    pd.reset_option('display.max_rows')

def read_file(filename):
    print "opening " + filename
    data = pd.read_csv(filename)
    return data


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


def clean_stops_file(data):
    print "cleaning stops file"
    getline = lambda x: x[0]
    strsort = lambda x : "".join(sorted(x))
    data["line"] = data.stop_id.map(getline)
    data.line = data.line.map(strsort)
    name_grps = data.groupby(["stop_name"])
    out = name_grps.mean().reset_index()
    codes, agrmt, loc_list = get_code_equivalencies(name_grps, data)
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


def clean_entrances_file(data):
    return data


def get_ids_distance(id1, id2):
    e1 = _data[_data.parent_station == id1]
    e2 = _data[_data.parent_station == id2]
    if not (e1.empty or e2.empty):
        latlng_1 = (e1.stop_lat.values[0], e1.stop_lon.values[0])
        latlng_2 = (e2.stop_lat.values[0], e2.stop_lon.values[0])
        return great_circle(latlng_1, latlng_2).meters
    else:
        return float("inf")


def clean_stoptimes_file(data):
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

    to_mins = lambda x: x.astype('timedelta64[m]').astype(float)
    odd_pairs["travel_time"] = (odd_pairs.source_arrival - odd_pairs.target_arrival).apply(to_mins)
    even_pairs["travel_time"] = (even_pairs.target_arrival - even_pairs.source_arrival).apply(to_mins)
    out = pd.concat([even_pairs, odd_pairs])
    out = out.drop(["source_arrival", "target_arrival"])
    out = out[out.travel_time <= 20]
    out = out[out.travel_time >= 0]
    out = out.groupby(["source", "target"]).mean().reset_index()
    out["distances"] = out.apply(lambda x: get_ids_distance(str(x.source), str(x.target)), axis=1)
    out = out[out.distances < 6500.0]
    out = out[out.distances > 0]
    return out


def merge_stops_entrances(stops):
    print "merging stops and entry point data"
    e_matches = stops.apply(closest_match_latlng, axis=1)
    ms = pd.concat((stops, e_matches), axis=1)
    neq = ms.apply(lambda x: filter(lambda y: str(y)[0] in x.trains, x.related_by_name), axis=1)
    ms["filtered_codes"] = neq
    return ms


def merge_turnstile_info(data):
    print "merging with turnstile info"
    ts_matches = data.apply(lambda x: commuter_matching(x)[0], axis=1)
    ts_similarity = data.apply(lambda x: commuter_matching(x)[1], axis=1)
    md = pd.concat((data, ts_matches), axis=1)
    md["turnstile_matching_similarity"] = ts_similarity
    return md


def cache_connections_data(fn="data/cleaned_connections.csv"):
    print "computing edge topology"
    _stops_data = clean_stoptimes_file(read_file("data/google_transit/stop_times.txt"))
    _stops_data.to_csv("data/cleaned_connections.csv", index=False)


def lat_lng_distances(lat_lng, entrance_data):
    d = lambda x: great_circle(lat_lng, (x.stop_lat, x.stop_lon)).meters
    return _data.apply(d, axis=1)


def closest_match_neighbors(search_name):
    d = lambda x: fish.jaro_winkler(unicode(x.stop_name.lower()),
        unicode(search_name.lower())) + 100 * (x.parent_station[0] in search_name.split("_")[-1])
    distances = _data.apply(d, axis=1)
    i = np.argmax(distances)
    return _data.stop_name[i], _data.stop_lat[i], _data.stop_lon[i], _data.parent_station[i]

_name_key, _data = clean_stops_file(read_file("data/google_transit/stops.txt"))
cache_connections_data()
from totals import commuter_matching
merged = merge_stops_entrances(_data)
final = merge_turnstile_info(merged)
final["Id"] = final.parent_station
final["latitude"] = final.stop_lat
final["longitude"] = final.stop_lon
final["Label"] = final.apply(lambda x: x.stop_name + "_" + x.LINENAME, axis=1)
final.to_csv("data/cleaned_nodes.csv")

