__author__ = 'sam.royston'
import pandas as pd
import numpy as np
import editdistance as lev
from geopy.distance import great_circle
from utils import default_data_dir


class StationLocationReader(object):
    def __init__(self, data_dir=default_data_dir(), verbose=False):
        self.verbose = verbose
        self.data_dir = data_dir
        self.data = self.clean_file(StationLocationReader.read_file())

    @staticmethod
    def read_file():
        data = pd.read_csv(default_data_dir() + "/StationEntrances.csv")
        return data

    @staticmethod
    def clean_file(data):
        strfix = lambda x : str(x).replace("nan", "").replace(" ", "").replace(".", "").replace("0", "")
        strsort = lambda x : "".join(sorted(x))
        data["trains"] = data.Route_1.map(strfix) + data.Route_2.map(strfix) + data.Route_3.map(strfix) +\
            data.Route_4.map(strfix) + data.Route_5.map(strfix) + data.Route_6.map(strfix) + data.Route_7.map(strfix)+\
            data.Route_8.map(strfix) + data.Route_9.map(strfix)

        data.trains = data.trains.map(strsort)
        data["latlng"] = data.apply(lambda x: (x.Latitude, x.Longitude), axis=1)

        groups = data.groupby(["Station_Name", "trains"])
        data = groups.head(1).reset_index()
        stations_access = groups.apply(lambda x: x.latlng.drop_duplicates().dropna().tolist())
        data["station_access"] = stations_access.values
        return data

    def closest_match_latlng(self, search):
        lat = search.stop_lat
        lng = search.stop_lon
        d = lambda x: great_circle((lat, lng), (x.Station_Latitude, x.Station_Longitude)).km
        distances = self.data.apply(d, axis=1)
        i = np.argmin(distances)
        d1 = distances[i]
        distances[i] = 999999999
        j = np.argmin(distances)
        d2 = distances[j]
        closest = self.data.iloc[[i, j]]
        winners = closest[closest.trains.apply(lambda x: str(search.parent_station)[0] in x) == 1]
        if len(winners) > 0 and d1 > d2 / 2:
            out = winners.head(1)[["Station_Name", "Line", "Station_Latitude", "Station_Longitude",
                                "station_access", "trains", "Free_Crossover", "Division"]].iloc[0]
        else:
            out = self.data.iloc[i][["Station_Name", "Line", "Station_Latitude", "Station_Longitude",
                                    "station_access", "trains", "Free_Crossover", "Division"]]
        return out

    def closest_match_name(self, search_name):
        d = lambda x: lev.eval(x.lower(), search_name.lower())
        distances = self.data.Station_Name.map(d)
        i = np.argmin(distances)
        return self.data.Station_Name[i], self.data.Station_Latitude[i], self.data.Station_Longitude[i]