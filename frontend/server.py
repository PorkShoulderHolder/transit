__author__ = 'sam.royston'
from flask import Flask, send_from_directory, render_template
import csv
import json
app = Flask(__name__)
import os
import platform
import calendar
"""
util file functions
"""

PROC_DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/transport/processed_data"
RAW_DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/mta/mta_data"


def get_connections():
    with open(PROC_DATA_DIR + "/connections_normal_wo_limits.csv") as f:
        fieldnames = ("source", "target", "flow", "travel_time")
        reader = csv.DictReader(f)
        out = [row for row in reader]
        return out


def get_stations():
    with open(PROC_DATA_DIR + "/nodesnormal_wo_limits.csv") as f:
        fieldnames = ("Id", "latitude", "longitude", "Label", "prices")
        reader = csv.DictReader(f)
        out = {}
        for row in reader:
            out[row["Id"]] = row
        return out

def get_readable_date():
    files = filter(lambda x: "turnstile_" in x, os.listdir(RAW_DATA_DIR))
    files_dates = zip(files, [f.split("_")[-1][:6] for f in files])
    files_dates = sorted(files_dates, key=lambda x: x[1], reverse=True)
    active_ts_file = files_dates[0][0]
    day = str(int(active_ts_file[-9:-7]))
    month = calendar.month_name[int(active_ts_file[-11:-9])]
    year = "20" + active_ts_file[-13:-11]
    return "{0} {1}, {2}".format(month, day, year)

def init_cache():
    stations = get_stations()
    lines = get_connections()
    last_update = get_readable_date()
    return json.dumps({"nodes": stations, "edges": lines, "last_updated":last_update})

print "initializing cache"
cache = init_cache()

@app.route("/")
def splash():
    return render_template("index.html")

@app.route("/learn")
def learn():
    return render_template("optimal_transport.html")

@app.route("/map")
def show_map():
    return render_template("map.html")

@app.route("/flowdata")
def flow_data():
    return cache

if __name__ == '__main__':
    debug = True if platform.system() == "Darwin" else False
    app.run(port=5353, debug=debug, host="0.0.0.0")
