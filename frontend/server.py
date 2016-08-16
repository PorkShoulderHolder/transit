__author__ = 'sam.royston'
from flask import Flask, send_from_directory, render_template
import csv
import json
app = Flask(__name__)
import os
import platform
"""
util file functions
"""

PROC_DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/transport/processed_data"


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


def init_cache():
    stations = get_stations()
    lines = get_connections()
    return json.dumps({"nodes": stations, "edges": lines})

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
