"""
leidenalg docs:     https://leidenalg.readthedocs.io/en/latest/
leidenalg repo:     https://github.com/vtraag/leidenalg
"""

import logging
import os

import igraph as ig
import leidenalg as la
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'


class Event:
    """
    Class holding information on each 'event' (OC/OT).
    """

    def __init__(self, etype: str, press_start: pd.Timestamp, excerpt: pd.DataFrame, delta=30, epsilon=200) -> None:
        """
        Initialize an instance of Event.

        etype   :       Event type; either 'ot' or 'oc'
        ps      :       Timestamp of the press start (press time minus duration)
        excerpt :       DataFrame holding excerpt from lidar df; based on the button press
        delta   :       Threshold for what we consider close in latdist
        epsilon :       Threshold for what we consider close in time
        """

        self.etype = etype
        self.ps = press_start
        self.excerpt = excerpt
        self.delta = delta
        self.epsilon = epsilon

        self.vertices = self.make_vertices()
        self.edges = self.make_edges()
        self.g = self.make_graph()
        self.p = self.find_partition()
        self.part = self.select_part()

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
        # print(n, "vertices")
        # print(self.vertices)
        edges = {}

        if n < 2:
            logging.error("Not enough vertices in the graph: n = %d", n)
        logging.info("Constructing edges.")

        for i in range(1, n):
            ti, di = self.vertices[i]
            for j in range(i - 1, 0, -1):
                tj, dj = self.vertices[j]
                diff_d = abs(di - dj)
                diff_t = abs(ti - tj)

                if diff_d < self.delta and diff_t < np.timedelta64(self.epsilon, "ms"):
                    edges[(j, i)] = 1
                elif diff_d < self.delta and diff_t > np.timedelta64(self.epsilon, "ms"):
                    for k in range(j + 1, i):
                        if (k, i) in edges:
                            # not sure if need next 2 lines (only consider vertices k which are close enough to j -- though in practice the first one will be like that)
                            tk, dk = self.vertices[k]
                            if abs(tk - tj) < np.timedelta64(self.epsilon, "ms"):
                                edges[(j, i)] = 1
                                break
                        else:
                            break
        return edges

    def make_graph(self) -> ig.Graph:
        """
        Construct a weighted graph based on the excerpt.
        """
        return ig.Graph(self.edges.keys(), directed=False)  # only get keys (x,y) edges, ignore weights for now

    def find_partition(self) -> la.ModularityVertexPartition:
        """
        Run leidenalg on the graph and save partitions.
        """

        return la.find_partition(self.g, la.ModularityVertexPartition)

    def select_part(self) -> list:
        """
        Return list of vertices that belong in the part corresponding to the vehicle.
        """

        part_candidates = []
        part_avgs = []
        for pt in self.p:
            if len(pt) < 4:
                continue
            latdists_in_pt = [self.vertices[key][1] for key in pt]
            avg_latdist = sum(d for d in latdists_in_pt) / len(latdists_in_pt)
            part_candidates.append(pt)
            part_avgs.append(avg_latdist)

        return part_candidates[np.argmin(part_avgs)]

    def plot_event(self) -> None:
        """
        Plot detected part against excerpt.
        """

        plt.clf()

        verts = list(self.vertices.values())
        unzipped = list(zip(*verts))
        plt.scatter(unzipped[0], unzipped[1], color="b")

        part_verts = list([self.vertices[x] for x in self.part])
        part_unzipped = list(zip(*part_verts))
        plt.scatter(part_unzipped[0], part_unzipped[1], color="r")
        plt.savefig(os.path.join("out", "detection_" + self.etype + "_" + str(self.ps) + ".png"))
