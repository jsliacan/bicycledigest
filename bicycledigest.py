"""
bicycledigest.py

Package for processing data collected with the bicycle logger.
"""

import logging

import igraph as ig
import matplotlib.pyplot as plt
import pandas as pd

from event import Event
from session import BicycleSession

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)s %(message)s",
    encoding="utf-8",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("digest.log"),
        logging.StreamHandler(),  # logging 'info' level to console as well
    ],
)


if __name__ == "__main__":

    s = BicycleSession()

    for k, event in enumerate(s.events):
        e = event.excerpt

        print(event.p)
        print("-" * 10)
        print(event.part)
        print("-" * 40)
        event.plot_event()

        # eps = pd.Timedelta(milliseconds=150)
        # delta = 40
        # running_score = []
        # print(len(e.distance))
        # for i in range(len(e.distance)):
        #     score = 0
        #     window = e.loc[(e["time"] > e.time.iloc[i] - eps) & (e["time"] < e.time.iloc[i] + eps)]
        #     print("latdist_i =", e.distance.iloc[i])
        #     print(window)
        #     score = sum([1 if abs(x - e.distance.iloc[i]) < delta else 0 for x in window["distance"]])
        #     running_score.append(score)
        #
        # plt.scatter(range(len(running_score)), running_score)
        # plt.show()
        # break

    # session.print_info()
