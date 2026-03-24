import logging
import os
import time

import osmnx as ox
import overpy
import pandas as pd
from constants import *
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon
from transform import event

# def read_events_file(filename: str) -> pd.DataFrame:
#     """
#     Load events from the 'events.csv' and return the dataframe.
#     """
#
#     events_df = pd.read_csv(filename)
#     return events_df
#
#
# def construct_latlon_list(events_df: pd.DataFrame) -> list:
#     """
#     Take DF with two columns: lat,lon; and return a zipped list of these:
#         [[lat0,lon0], [lat1,lon1], [lat2,lon2],...]
#     """
#
#     latlon_list = events_df[["gps_lon", "gps_lat"]].values.tolist()
#     return latlon_list


def convex_hull_vertices(list_of_gps_pairs: list) -> Polygon:
    """
    From a list of [lat,lon] pairs, construct a convex hull and return a
    sublist of the outer points.
    """

    logging.info("Constructing the convex hull of the gps points.")

    hull = ConvexHull(list_of_gps_pairs)
    # select subset of original pairs that form the convex hull
    outer_vertices = [list_of_gps_pairs[int(x)] for x in hull.vertices]

    return Polygon(outer_vertices)


def get_road_info(list_of_gps_pairs: list, net_type: str) -> list:
    """
    Get road info from (lat,lon) coordinates. Find closest "edge" and print its
    properties.

    net_type    :   what road network to focus on; default is "drive"
    """

    logging.info("Obtaining road information for each event.")

    # get min convex-hull polygon of the gps points
    gps_polygon = convex_hull_vertices(list_of_gps_pairs)

    # Download the road network around the point (50m meter buffer)
    logging.info("Caching map information for the polygon.")
    graph = ox.graph_from_polygon(gps_polygon, network_type=net_type)

    roads = []
    for lon, lat in list_of_gps_pairs:

        # Find the nearest edge (road segment)
        u, v, key = ox.distance.nearest_edges(graph, X=lon, Y=lat)

        # Access the data dictionary for that specific road segment
        edge_data = graph.get_edge_data(u, v, key)

        # Display the results
        # print(f"--- Road Information ---")
        # print(f"Ref:          {edge_data.get('ref', 'Unknown')}")
        # print(f"Highway Type: {edge_data.get('highway', 'Unknown')}")
        # print(f"Speed Limit:  {edge_data.get('maxspeed', 'Not defined in OSM')}")
        # print(f"Oneway:       {edge_data.get('oneway', 'Unknown')}")
        # print(f"Lanes:        {edge_data.get('lanes', 'Unknown')}")
        # print(f"Length:       {edge_data.get('length'):.2f}m")
        # print(f"Width:        {edge_data.get('width','Unknown')}")

        road_info = {
            "ref": edge_data.get("ref", 0),
            "type": edge_data.get("highway", ""),
            "maxspeed": edge_data.get("maxspeed", 0),
            "oneway": edge_data.get("oneway", False),
            "numlanes": edge_data.get("lanes", 0),
            "length": edge_data.get("length"),
            "width": edge_data.get("width", []),
        }
        roads.append(road_info)
    return roads


# ---------- get road info with Overpy ------------
# basically doesn't work;
# def get_road_info(tolerance: int, gps_lat: float, gps_lon: float) -> dict:
#     """
#     Find (snap-to-road) the closest road to the (gps_lat,gps_lon) coordinates.
#     Plus/minus 10m, otherwise return empty JSON.
#
#     tolerance:
#     """
#     api = overpy.Overpass()
#     r = api.query(f'way(around:{tolerance},{gps_lat},{gps_lon})["highway"];out;')
#     print("Sleeping 0.25s.", flush=True)
#     time.sleep(0.5)
#
#     road_info = {}
#     try:
#         road_info = r.ways[0]
#     except:
#         print("Could not retrieve road information.", flush=True)
#
#     return road_info

# return [r.ways[x].tags for x in range(len(r.ways))]
