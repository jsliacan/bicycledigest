import matplotlib.pyplot as plt
import pandas as pd
from transform.session import BicycleSession


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
