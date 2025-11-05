"""
leidenalg docs:     https://leidenalg.readthedocs.io/en/latest/
leidenalg repo:     https://github.com/vtraag/leidenalg
"""

import logging

import igraph as ig
import leidenalg as la
import pandas as pd


class Event:
    """
    Class holding information on each 'event' (OC/OT).
    """

    def __init__(self, etype: str, ps: pd.Timestamp, excerpt: pd.DataFrame, delta=30, epsilon=0.02) -> None:
        """
        Initialize an instance of Event.

        etype   :       Event type; either 'ot' or 'oc'
        ps      :       Timestamp of the press start (press time minus duration)
        excerpt :       DataFrame holding excerpt from lidar df; based on the button press
        delta   :       Threshold for what we consider close in latdist
        epsilon :       Threshold for what we consider close in time
        """

        self.etype = etype
        self.ps = ps
        self.excerpt = excerpt
        self.delta = delta
        self.epsilon = epsilon

        self.vertices = self.make_vertices()
        self.edges = self.make_edges()
        self.g = self.make_graph()
        self.p = self.find_partition()

    def make_vertices(self) -> dict:
        """
        Create a dict of vertices: {i: (t_i, d_i)}_i.
        """

        edf = self.excerpt
        edf["vertex"] = list(zip(edf.time.values, edf.distance.values))
        V = {i: edf["vertex"].iloc[i] for i in range(len(edf["vertex"]))}

        return V

    def make_edges(self) -> dict:
        """
        Create a dict of edges with weights: {(i,j): w_ij}
        """
        n = len(self.vertices)
        edges = {}

        if n < 2:
            logging.error("Not enough vertices in the graph: n = %d", n)
        logging.info("Constructing edges.")

        for i in range(1, n):
            ti, di = self.vertices[i]
            for j in range(i - 1, -1, 0):
                tj, dj = self.vertices[j]
                diff_d = abs(di - dj)
                diff_t = abs(ti - tj)

                if diff_d < self.delta and diff_t < self.epsilon:
                    edges[(i, j)] = 1
                elif diff_d < self.delta and diff_t > self.epsilon:
                    for k in range(j + 1, i):
                        if edges[(k, i)] == 1:
                            edges[(j, k)] = 1
                        else:
                            break
        return edges

    def make_graph(self) -> ig.Graph:
        """
        Construct a weighted graph based on the excerpt.
        """

        return ig.Graph(self.edges.keys())  # only get keys (x,y) edges, itnore weights for now

    def find_partition(self) -> la.ModularityVertexPartition:
        """
        Run leidenalg on the graph and save partitions.
        """

        return la.find_partition(self.g, la.ModularityVertexPartition)
