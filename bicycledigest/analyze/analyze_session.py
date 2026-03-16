import os

import pandas as pd
from constants import *
from transform import event


def events_to_csv(events: list[event.Event]) -> None:
    """
    Load all session events to a dataframe and dump them in a CSV file.

    Return df.
    """

    hashes = []
    types = []
    times = []
    min_lds = []
    gpss = []

    for e in events:
        hashes.append(e.hash)
        types.append(e.etype)
        times.append(float(e.t_list[0]))
        min_lds.append(min(e.ld_list))
        gpss.append(e.gps_trace[0])

    df_events = pd.DataFrame({"hash": hashes, "type": types, "time": times, "min_lat_dist": min_lds, "gps": gpss})

    # do not write the unnemaed index column to CSV
    df_events.to_csv(os.path.join(REPOSITORY_PATH, "out", "events.csv"), index=False)
