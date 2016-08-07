__author__ = 'sam.royston'
import numpy as np
from geopy.distance import great_circle
from random import randint
import pandas as pd


def create_production_rates(nodes):
    try:
        return nodes.net.values
    except AttributeError:
        return nodes.NET.values


def create_entrance_rates(nodes):
    try:
        return nodes.entries.values
    except AttributeError:
        return nodes.ENTRIES.values


def create_exit_rates(nodes):
    try:
        return nodes.exits.values
    except AttributeError:
        return nodes.EXITS.values


def create_bounds(edges, nodes):
    bounds = []
    for edge in edges.iterrows():
        entries = nodes.entries[nodes.parent_station == edge[1].Source].values[0]
        bounds.append((0.00*entries, None))
    return bounds


def create_edges_vector(edges):
    try:
        sources = edges.Source.values
        targets = edges.Target.values
    except AttributeError:
        sources = edges.source.values
        targets = edges.target.values
    ev = np.vstack((sources, targets))
    nix = np.logical_not(np.all(ev == ev[0, :], axis=0))
    return ev[:, nix]


def create_cost_vector(edges):
    return edges.travel_time.values


def create_ids_vector(nodes):
    return nodes.parent_station.values


def add_transfer_nodes(nodes, edges):
    pass


def switch_src_target(df):
    df.source[len(df)/2:] = df.target[len(df)/2:]
    df.target[len(df)/2:] = df.source[:len(df)/2]
    return df


def build_connections(ids):
    source = ids[1]
    edges = []
    wait_constant = 5.0
    average_human_walking_speed_mm = 83.3333333
    for idx in ids[0]:
        if idx[0] != source:
            edges.append((source, idx[0], wait_constant + idx[1] / average_human_walking_speed_mm, idx[1], 1))
    if len(edges) > 0:
        complete_chunk = pd.DataFrame(edges, columns=['source', 'target', 'travel_time', 'distances', 'is_transfer'])
    else:
        return None
    return complete_chunk


def add_transfer_edges(nodes, edges):
    new_edges = edges

    def d(x):
        def lines_in_common(y):
            return sum(y.LINENAME.count(c) for c in x.trains) / float(max(len(y.LINENAME), len(x.trains)))
        line_ds = nodes.apply(lines_in_common, axis=1)
        same_trains = nodes[line_ds > 0.6]
        ds = same_trains.apply(lambda y: great_circle((y.stop_lat, y.stop_lon), (x.stop_lat, x.stop_lon)).meters, axis=1)
        if ds.empty:
            return []

        return zip(same_trains.Id[ds < 400].values.tolist(), ds[ds < 400].values.tolist()), x.Id

    ids = nodes.apply(d, axis=1).values.tolist()
    for idx in ids:
        if len(idx) > 1:
            clique = build_connections(idx)
            if clique is not None:
                new_edges = pd.concat((new_edges, clique))
    return new_edges.drop_duplicates(subset=["source", "target"])


def balance(prod_rates, dispersion=1000):
    new_pr = prod_rates
    delta = np.sum(prod_rates)
    for i in xrange(dispersion):
        new_pr[randint(0, len(prod_rates)-1)] -= delta / float(dispersion)
    return new_pr


def package_input(nodes, edges):
    es = create_edges_vector(edges)
    vs = create_ids_vector(nodes)
    costs = create_cost_vector(edges)
    pr = balance(create_production_rates(nodes))
    er = create_entrance_rates(nodes)
    exr = create_exit_rates(nodes)
    return es, vs, costs, pr, er, exr