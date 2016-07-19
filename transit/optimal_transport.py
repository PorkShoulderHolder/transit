__author__ = 'sam.royston'
from scipy.optimize import linprog
import numpy as np
np.set_printoptions(threshold=1000)

def construct_grad_matrix(edges, vertices):
    """
    :param edges: a numpy matrix of size |E| x 2 containing (source,target) pairs
    :param nodes: a single numpy vector of length |V| containing vertex ids in the order they should be considered
    :return: the gradient matrix to be used in the optimal transport problem
    """
    grad_matrix = np.zeros((len(edges), len(vertices)))
    for i, edge in enumerate(edges):
        grad_matrix[i][np.where(vertices == edge[0])] = 1
        grad_matrix[i][np.where(vertices == edge[1])] = -1
    return grad_matrix


def construct_io_matrices(edges, vertices):
    grad_matrix = construct_grad_matrix(edges, vertices)
    in_matrix = np.zeros(grad_matrix.shape)
    out_matrix = np.zeros(grad_matrix.shape)
    in_matrix[np.where(grad_matrix == 1)] = 1
    out_matrix[np.where(grad_matrix == -1)] = 1
    return in_matrix, out_matrix


def construct_movement_matrix(edges):
    undirected = np.unique([str(row) for row in np.sort(edges, axis=1)])
    move_matrix = np.zeros((len(edges), len(edges) / 2 + 2))
    sorted_edges = np.array([str(row) for row in np.sort(edges, axis=1)])
    for i, edge in enumerate(sorted_edges):
        ix = np.where(edge == undirected)
        move_matrix[i][ix[0]] = 1
    return move_matrix


def compute(edges, vertices, transport_costs, vertex_production,
            bounds=None, entries=None, exits=None, move_bounds=None):
    io_status = entries is not None and exits is not None
    grad_matrix = construct_grad_matrix(edges, vertices)
    in_matrix, out_matrix = construct_io_matrices(edges, vertices)
    io_matrices = -1 * np.vstack((in_matrix.transpose(), out_matrix.transpose())) if io_status else None
    ub_flows = -1 * np.hstack((entries, exits)) if io_status else None
    constraints = "basic" if not io_status else "eeconstr"
    if move_bounds:
        move_mtx = -1 * construct_movement_matrix(edges)
        bds = -1 * move_bounds * np.ones(len(edges) / 2 + 2)
        bds[np.sum(move_mtx, axis=0) != 2] = 0
        constraints += "_bidir" + str(move_bounds)
        move_mtx = move_mtx.transpose()
    if move_bounds and io_status:
        ub_flows = np.hstack((ub_flows, bds))
        io_matrices = np.vstack((io_matrices, move_mtx))
    elif move_bounds:
        ub_flows = bds
        io_matrices = move_mtx
    if bounds is not None and len(bounds) == 2:
        constraints += "_bounds" + str(bounds)
    elif bounds is not None:
        constraints += "_individualbounds"
    print "optimizing with " + constraints + " constraints"
    res = linprog(transport_costs, A_eq=grad_matrix.transpose(), bounds=bounds, A_ub=io_matrices,
                  b_eq=vertex_production, b_ub=ub_flows, options={"tol": 1e-7, 'maxiter': 10000})
    return res, constraints


def compute_costs(edges, vertices, transport_costs, vertex_production, bounds=None):
    grad_matrix = construct_grad_matrix(edges, vertices)
    res = linprog(vertex_production, A_ub=grad_matrix, b_ub=transport_costs,  bounds=bounds,  options={"tol": 1e-7, 'maxiter': 10000})
    return res




