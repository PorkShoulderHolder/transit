__author__ = 'sam.royston'
from optimal_transport import compute, compute_costs
from data_munge.postprocessing import add_transfer_edges, package_input
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from data_munge.subway_topology import get_topology


def switch_src_target(df):
    df.source[len(df)/2:] = df.target[len(df)/2:]
    df.target[len(df)/2:] = df.source[:len(df)/2]
    return df

# 86 mins total
BQX_conns = np.array([
    ["R41", "R36", 12.0, 0, 0],
    ["R36", "231", 21.0, 0, 0],
    ["231", "A40", 6.0, 0, 0],
    ["A40", "F18", 7.0, 0, 0],
    ["F18", "L08", 15.0, 0, 0],
    ["L08", "G26", 6.0, 0, 0],
    ["G26", "F09", 7.0, 0, 0],
    ["F09", "G24", 6.0, 0, 0],
    ["G24", "R04", 6.0, 0, 0]
])
BQX_conns = pd.DataFrame(np.vstack((BQX_conns,BQX_conns)),
                         columns=["source", "target", "travel_time", "distance", "is_transfer"])
BQX_conns = switch_src_target(BQX_conns)
# 98 mins total
TRIBORO_conns = np.array(
[
    ["613", "R01", 12.0, 0, 0],
    ["221", "R01", 11.0, 0, 0],
    ["R01", "G14", 9.0, 0, 0],
    ["G14", "M01", 8.0, 0, 0],
    ["M01", "L20", 8.0, 0, 0],
    ["L20", "L24", 6.0, 0, 0],
    ["L24", "L26", 5.0, 0, 0],
    ["L26", "254", 2.0, 0, 1],
    ["254", "247", 12.0, 0, 0],
    ["247", "D32", 5.0, 0, 0],
    ["D32", "F31", 5.0, 0, 0],
    ["F31", "N04", 6.0, 0, 0],
    ["N04", "B16", 2.0, 0, 1],
    ["B16", "R41", 7.0, 0, 0]
])
TRIBORO_conns = pd.DataFrame(np.vstack((TRIBORO_conns, TRIBORO_conns)),
                             columns=["source", "target", "travel_time", "distance", "is_transfer"])

TRIBORO_conns = switch_src_target(TRIBORO_conns)


def compute_flows(nodes, edges, with_limits=None, directional_bounds=None, bounds=None, record=True):
    es, vs, costs, pr, er, exr = package_input(nodes, edges)
    if with_limits is not None:
        res, constraints = compute(es.transpose(), vs, costs, pr, entries=er,
            exits=exr, move_bounds=directional_bounds, bounds=bounds)
    else:
        res, constraints = compute(es.transpose(), vs, costs, pr, move_bounds=directional_bounds, bounds=bounds)
    if record:
        with open("data/" + constraints + "_log.txt", "w+") as f:
            f.write(str(res) + "\n")
            f.write("flow sum: " + str(np.sum(res.x)) + "\n")
            f.write("flow max: " + str(np.max(res.x)) + "\n")
            f.write("flow dist: " + str(res.x.tolist()))
    return res, constraints


def compute_prices(nodes, edges):
    es, vs, costs, pr, er, exr = package_input(nodes, edges)
    res = compute_costs(es.transpose(), vs, costs, pr)
    return res.x

i = 0


def burn_csvs(with_limits=None, directional_bounds=None, bounds=None, hypo=None):
    nodes, edges = get_topology()

    complete_edges = add_transfer_edges(nodes, edges)
    if hypo is not None:
        complete_edges = pd.concat((complete_edges, hypo))
    complete_edges = complete_edges.drop_duplicates()
    print "computing optimal flows"
    res, constraints = compute_flows(nodes, complete_edges, with_limits, directional_bounds, bounds=bounds)
    flows = res.x
    prices = compute_prices(nodes, complete_edges)
    complete_edges["flow"] = flows
    nodes["prices"] = prices
    print "saving to data/connections_" + constraints + ".csv"
    complete_edges.to_csv("data/connections_" + constraints + str(++i) + ".csv", index=False)
    nodes.to_csv("data/nodes.csv")

    es, vs, costs, pr, er, exr = package_input(nodes, complete_edges)
    costs = costs.astype(float)
    print costs
    print costs * flows

    return flows, prices, constraints, costs




f1, p1, c1, cc = burn_csvs(with_limits=True)
f2, p2, c2, ccc = burn_csvs(with_limits=True, hypo=BQX_conns)
f3, p3, c3, cccc = burn_csvs(with_limits=True, hypo=TRIBORO_conns)
f4, p4, c4, costs = burn_csvs()
f5, p5, c5, costs1 = burn_csvs(hypo=BQX_conns)
f6, p6, c6, costs2 = burn_csvs(hypo=TRIBORO_conns)

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

