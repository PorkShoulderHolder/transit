__author__ = 'sam.royston'
from optimal_transport import compute, compute_costs
from mta.postprocessing import add_transfer_edges, package_input
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from mta.subway_topology import TopologyReader
from mta.turnstiles import TurnstileReader
from mta.constants import BQX_conns, TRIBORO_conns
import os

DEFAULT_STORAGE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/processed_data"


def get_topology():
    ts_reader = TurnstileReader(verbose=True)
    topo_reader = TopologyReader()
    final_stops_data = topo_reader.merge_turnstile_info(ts_reader)
    return final_stops_data, topo_reader.travel_times


def compute_flows(nodes, edges, with_limits=None, directional_bounds=None):
    es, vs, costs, pr, er, exr = package_input(nodes, edges)
    if with_limits is not None:
        res, constraints = compute(es.transpose(), vs, costs, pr, entries=er,
            exits=exr, move_bounds=directional_bounds)
    else:
        res, constraints = compute(es.transpose(), vs, costs, pr)
    return res, constraints


def compute_prices(nodes, edges):
    es, vs, costs, pr, er, exr = package_input(nodes, edges)
    res = compute_costs(es.transpose(), vs, costs, pr)
    return res.x


def burn_csvs(nodes, edges, with_limits=None, hypo=None, storage_dir=DEFAULT_STORAGE_DIR, name=""):
    complete_edges = add_transfer_edges(nodes, edges)
    complete_edges = pd.concat((complete_edges, hypo)) if hypo is not None else complete_edges
    complete_edges = complete_edges.drop_duplicates()
    res, constraints = compute_flows(nodes, complete_edges, with_limits)
    flows = res.x
    prices = compute_prices(nodes, complete_edges)
    complete_edges["flow"] = flows
    nodes["prices"] = prices
    complete_edges.to_csv("{0}/connections_{1}".format(storage_dir, name) + ".csv", index=False)
    nodes.to_csv("{0}/nodes{1}.csv".format(storage_dir, name))
    es, vs, costs, pr, er, exr = package_input(nodes, complete_edges)
    costs = costs.astype(float)
    return flows, prices, constraints, costs


def run_opts():
    nodes, edges = get_topology()
    f1, p1, c1, cc = burn_csvs(nodes, edges, with_limits=True, name="normal_w_limits")
    f2, p2, c2, ccc = burn_csvs(nodes, edges, with_limits=True, hypo=BQX_conns, name="BQX_w_limits")
    f3, p3, c3, cccc = burn_csvs(nodes, edges, with_limits=True, hypo=TRIBORO_conns, name="TRIBORO_w_limits")
    f4, p4, c4, costs = burn_csvs(nodes, edges, name="normal_wo_limits")
    f5, p5, c5, costs1 = burn_csvs(nodes, edges, hypo=BQX_conns, name="BQX_wo_limits")
    f6, p6, c6, costs2 = burn_csvs(nodes, edges, hypo=TRIBORO_conns, name="TRIBORO_wo_limits")

    if __name__ == "__main__":
        l = len(np.sort(f1 * cc))
        # plt.semilogy(np.sort(f1)[:l],'b--',  label="with flow constraints")
        #plt.semilogy(np.sort(f2 * ccc)[:l], 'g--', label="BQX plan, with flow ee constraints")
        #plt.semilogy(np.sort(f3 * cccc)[:l],'r--', label="Triboro plan, with flow ee constraints")
        l = len(np.sort(f4 * costs))
        # plt.semilogy(np.sort(f4)[:l], 'b', label="original model")
        #plt.semilogy(np.sort(f5 * costs1)[:l],'g', label="BQX plan")
        #plt.semilogy(np.sort(f6 * costs2)[:l], 'r', label="Triboro plan")
        #plt.legend(loc='lower right')
        # plt.show()
        print np.sum(f4 * costs)
        print np.sum(f5 * costs1)
        print np.sum(f6 * costs2)
        print np.max(f4)
        print np.max(f5)
        print np.max(f6)

        print np.sum(f1 * cc)
        print np.sum(f2 * ccc)
        print np.sum(f3 * cccc)
        print np.max(f1)
        print np.max(f2)
        print np.max(f3)
        # plt.legend(loc='lower right')
        # plt.show()
        # plt.plot(np.sort(p4), label="current subway system")
        # plt.plot(np.sort(p5), label="BQX plan")
        # plt.plot(np.sort(p6), label="Triboro plan")
        # plt.legend()
        # plt.show()