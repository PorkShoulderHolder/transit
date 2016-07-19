__author__ = 'sam.royston'
from flask import Flask, render_template
import csv
import json

app = Flask(__name__)

"""
util file functions
"""


def get_connections():
    with open("../data/connections_basic.csv") as f:
        fieldnames = ("source", "target", "flow", "travel_time")
        reader = csv.DictReader(f)
        out = [row for row in reader]
        return out


def get_stations():
    with open("../data/cleaned_nodes.csv") as f:
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

@app.route("/map")
def show_map():
    return render_template("map.html")

@app.route("/flowdata")
def flow_data():
    return cache

if __name__ == '__main__':
    app.run(port=5353, debug=True, host="0.0.0.0")