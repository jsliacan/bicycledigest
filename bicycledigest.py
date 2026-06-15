#!/usr/bin/python3
"""
bicycledigest.py

Package for processing data collected with the bicycle logger.
"""

import argparse
import logging
import os

import matplotlib.pyplot as plt
import pandas as pd

from event import *
from session import BicycleSession

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
file_handler = logging.FileHandler("digest.log")
file_handler.setLevel(logging.DEBUG)

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)s %(message)s",
    encoding="utf-8",
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[stream_handler, file_handler],  # logging to console as well
)


def tracking_density(s: BicycleSession) -> None:
    """
    CURRENTLY NOT USED.

    Experimental scoring of each latdist reading based on proximity of other
    readings to it.
    """

    for _, e in enumerate(s.events):
        eps = pd.Timedelta(milliseconds=150)
        delta = 40
        running_score = []
        print(len(e.distance))
        for i in range(len(e.distance)):
            score = 0
            window = e.loc[(e["time"] > e.time.iloc[i] - eps) & (e["time"] < e.time.iloc[i] + eps)]
            print("latdist_i =", e.distance.iloc[i])
            print(window)
            score = sum([1 if abs(x - e.distance.iloc[i]) < delta else 0 for x in window["distance"]])
            running_score.append(score)

        plt.scatter(range(len(running_score)), running_score)
        plt.show()


def main() -> None:

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--OutputDir", help="Path to the output directory.", default="out")
    parser.add_argument("-b", "--ButtonFile", help="Path of the button file.")
    parser.add_argument("-g", "--GPSFile", help="Path of the GPS file.")
    parser.add_argument("-l", "--LidarFile", help="Path of the lidar file.")
    args = parser.parse_args()

    if args.ButtonFile and args.GPSFile and args.LidarFile:  # either all files passed in commandline
        source_files = {"button_file": args.ButtonFile, "gps_file": args.GPSFile, "lidar_file": args.LidarFile}
        s = BicycleSession(sources=source_files, output_dir=args.OutputDir)
    else:  # or all files come from config
        s = BicycleSession(output_dir=args.OutputDir)

    s.print_info()

    # plt.clf()
    # for _, event in enumerate(s.events):
    #
    #     plt.ylim(0, 500)
    #     plt.plot(event.ld_list)
    #
    # plt.savefig(os.path.join("out", "all_ots.png"))


if __name__ == "__main__":

    main()
