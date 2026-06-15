"""
leidenalg docs:     https://leidenalg.readthedocs.io/en/latest/
leidenalg repo:     https://github.com/vtraag/leidenalg
"""

import hashlib
import logging
import os
from datetime import datetime

import igraph as ig
import leidenalg as la
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

pd.options.mode.chained_assignment = None  # default='warn'


def make_vertices(excerpt_df: pd.DataFrame) -> dict:
    """
    Create a dict of vertices: {i: (t_i, d_i)}_i.

    INPUT:

    excerpt_df:     data frame with lidar excerpt based on a button press (event.excerpt)
    """
    logging.debug("Constructing vertices/nodes.")

    excerpt_df["vertex"] = list(zip(excerpt_df.time.values, excerpt_df.distance.values))
    V = {i: excerpt_df["vertex"].iloc[i] for i in range(len(excerpt_df["vertex"]))}

    return V


def make_edges(vertices: dict, delta: float, epsilon: int) -> dict:
    """
    Create a dict of edges with weights: {(i,j): w_ij}

    INPUT:

    vertices:       dict {vertex_index: (timestamp, latdist)}; ordered latdist readings from the lidar
    delta:          two latdists this close in distance can have an edge between them
    epsilon:        two latdists this close in time can have edge between them
    """
    logging.debug("Constructing edges and weights.")

    n = len(vertices)
    edges = {}

    if n < 2:
        logging.error("Not enough vertices in the graph: n = %d", n)
    logging.debug("Constructing edges.")

    for i in range(1, n):
        ti, di = vertices[i]
        for j in range(i - 1, 0, -1):
            tj, dj = vertices[j]
            diff_d = abs(di - dj)
            diff_t = abs(ti - tj)

            if diff_d < delta and diff_t < np.timedelta64(epsilon, "ms"):
                edges[(j, i)] = 1
            elif diff_d < delta and diff_t > np.timedelta64(epsilon, "ms"):
                for k in range(j + 1, i):
                    if (k, i) in edges:
                        # not sure if need next 2 lines (only consider
                        # vertices k which are close enough to j -- though
                        # in practice the first one will be like that)
                        tk, _ = vertices[k]
                        if abs(tk - tj) < np.timedelta64(epsilon, "ms"):
                            edges[(j, i)] = 1
                            break
    return edges


def make_graph(vertices: dict, delta: float, epsilon: int) -> ig.Graph:
    """
    Construct a weighted graph based on the excerpt.

    INPUT:

    vertices:       dict {vertex_index: (timestamp, latdist)}; ordered latdist readings from the lidar
    delta:          two latdists this close in distance can have an edge between them
    epsilon:        two latdists this close in time can have edge between them
    """
    logging.debug("Constructing the graph.")
    edges = make_edges(vertices, delta, epsilon)

    return ig.Graph(edges.keys(), directed=False)  # only get keys (x,y) edges, ignore weights for now


def find_partition(g: ig.Graph, num_iters: int) -> la.ModularityVertexPartition:
    """
    Run leidenalg on the graph and save partitions.

    INPUT:

    g:              graph representing our excerpt
    num_iters:      leidenalg uses randomness in heuristics; higher num_iters
                    makes it converge more
    """
    logging.debug("Partitioning the graph.")

    return la.find_partition(g, la.ModularityVertexPartition, n_iterations=num_iters)


class Event:
    """
    Class holding information on each 'event' (OC/OT).
    """

    def __init__(
        self,
        etype: str,
        output_dir: str,
        button_press: pd.DataFrame,
        lidar_excerpt: pd.DataFrame,
        gps_excerpt: pd.DataFrame,
        delta=30,
        epsilon=200,
    ) -> None:
        """
        Initialize an instance of Event.

        etype           :   Event type; either 'ot' or 'oc'
        ps              :   Timestamp of the press start (press time minus duration)
        lidar_excerpt   :   DataFrame holding excerpt from lidar df; based on the button press
        delta           :   Threshold for what we consider close in latdist
        epsilon         :   Threshold for what we consider close in time
        """
        # input
        self.etype = etype
        self.output_dir = output_dir
        self.ps = button_press["press_start"]
        self.pe = button_press["time"]
        self.pd = button_press["duration"]
        self.delta = delta
        self.epsilon = epsilon
        self.hash = self.get_hash()

        # processing
        self.vertices = make_vertices(lidar_excerpt)
        self.g = make_graph(self.vertices, self.delta, self.epsilon)
        self.p = find_partition(self.g, 5)  # set num_iters to 5; not something user should be changing much

        # output
        self.part = self.select_part()  # indices of vertices (in self.vertices) corresponding to the OT/OC
        self.ld_list = [self.vertices[x][1] for x in self.part]  # latdists corresponding to OT/OC
        self.t_list = [self.vertices[x][0] for x in self.part]  # timestamps corresponding to OT/OC
        self.gps_trace = self.get_gps_trace(gps_excerpt)  # from OT/OC start till start of button press
        self.plot_event()
        self.export_yaml()

    def get_hash(self) -> str:
        """
        Return event's hash (ID) from a button press timestamp (as string).
        """
        logging.debug("Hashing event's timestamp into an ID.")

        h = hashlib.new("sha256")
        h.update(self.pe.strftime("%Y-%m-%d %H:%M:%S.%f").encode())

        return h.hexdigest()

    def select_part(self) -> list:
        """
        Return list of vertices in the part corresponding to the vehicle.

        IDEA:
        Currently just basic: eliminate parts that are too small (at 30+Hz,
        anything under 4 readings is not a car). Then take the lowest of the
        big parts.
        """
        logging.debug("Choosing the part (of the partition) corresponding to the event.")

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

    def get_gps_trace(self, gps_df: pd.DataFrame) -> list:
        """
        Return a list of (long,lat) values for the duration of the OT/OC.

        TODO:
        - Extend to OCs
        """

        if self.etype == "oc":
            logging.error("GPS trace not implemented.")
            return []

        logging.debug("Constructing GPS trace.")

        trace_end = self.ps  # beginning of the button press
        trace_start = pd.to_datetime(self.t_list[0], utc=True)  # first timestamp of the OT
        trace_df = gps_df.loc[(gps_df["time"] > trace_start) & (gps_df["time"] < trace_end)]

        return list(zip(trace_df.latitude.values, trace_df.longitude.values))

    def plot_event(self) -> None:
        """
        Plot detected part against excerpt.
        """

        plt.clf()
        logging.debug("Plotting event and savin figure.")
        verts = list(self.vertices.values())
        unzipped = list(zip(*verts))
        # plt.xlim(0, 150)
        plt.ylim(0, 900)
        plt.scatter(unzipped[0], unzipped[1], color="b")

        part_verts = list([self.vertices[x] for x in self.part])
        part_unzipped = list(zip(*part_verts))
        plt.scatter(part_unzipped[0], part_unzipped[1], color="r")
        plt.savefig(os.path.join(self.output_dir, "detection_" + self.etype + "_" + self.hash + ".png"))

    def export_yaml(self) -> None:
        """
        Export a YAML with Event attributes.
        """
        event_data = {
            "event_hash": self.hash,
            "event_type": self.etype,
            "press_start": str(self.ps),
            "press_end": str(self.pe),
            "press_duration": str(self.pd),
            "parameters": {"delta": self.delta, "epsilon": self.epsilon},
            "lateral_distances": str([float(x) for x in self.ld_list]),
            "ld_timestamps": str([x.astype(datetime) for x in self.t_list]),
            "gps_trace": str([(float(x[0]), float(x[1])) for x in self.gps_trace]),
            "helper_objects": {
                "vertices": str(self.vertices),
                "graph": self.g.summary(1),
                "partition": str(self.p),
                "part": str(self.part),
            },
        }

        with open(os.path.join(self.output_dir, "detection_" + self.etype + "_" + self.hash + ".yaml"), "w") as yamlfile:
            yaml.dump(event_data, yamlfile, default_flow_style=False, sort_keys=False)
