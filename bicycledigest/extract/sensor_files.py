import logging
import os
from ast import literal_eval

import pandas as pd


def read_button_file(button_file: str) -> pd.DataFrame:
    """
    Read in button file and return a dataframe.
    """

    print("button_file: ", button_file, flush=True)
    filename = os.path.basename(button_file)

    logging.info("Loading button CSV file: %s", filename)

    df = pd.read_csv(button_file, on_bad_lines="skip")
    # TODO: make the threshold below into a parameter
    df = df.loc[df["duration"] > 0.01]
    df = df.assign(time=pd.to_datetime(df["time"]))  # convert string UTC time to pd.DateTime
    df = df.assign(timedelta=pd.to_timedelta(df["duration"], unit="s"))  # timedelta = duration as pd.Timedelta
    df = df.assign(press_start=df["time"] - df["timedelta"])

    return df


def read_gps_file(gps_file: str) -> pd.DataFrame:
    """
    Read in GPS file and return a dataframe.
    """

    filename = os.path.basename(gps_file)
    logging.info("Loading gps CSV file: %s", filename)

    df = pd.read_csv(gps_file, on_bad_lines="skip")
    df = df.assign(time=pd.to_datetime(df["time"]))  # convert string UTC time to pd.DateTime
    df = df.astype({"latitude": float, "longitude": float})  # make sure values are floats

    return df


def read_lidar_file(lidar_file: str) -> pd.DataFrame:
    """
    Read in lidar file and return a dataframe.
    """

    filename = os.path.basename(lidar_file)

    logging.info("Loading lidar CSV file: %s", filename)

    df = pd.read_csv(lidar_file, on_bad_lines="skip")
    df = df.assign(time=pd.to_datetime(df["time"]))  # convert string UTC time to pd.DateTime

    if "distance [cm]" in df.columns:
        logging.info("Removing units from variable names in the header in %s.", filename)
        df.rename(columns={"distance [cm]": "distance"}, inplace=True)

    return df


def read_radar_file(radar_file: str) -> pd.DataFrame:
    """
    Read in raddar file and return a dataframe.
    """

    filename = os.path.basename(radar_file)

    logging.info("Loading radar CSV file: %s", filename)

    df = pd.read_csv(radar_file, on_bad_lines="skip")
    df.assign(time=pd.to_datetime(df["time"]))  # convert string UTC time to pd.DateTime

    # convert lists (as strings) to lists of floats/ints
    df.target_ids = df["target_ids"].apply(lambda x: list(literal_eval(x)))
    df.target_ranges = df["target_ranges"].apply(lambda x: list(literal_eval(x)))
    df.target_speeds = df["target_speeds"].apply(lambda x: list(literal_eval(x)))
    df.target_speeds = df.target_speeds.apply(lambda x: [float(val) * 3.6 for val in x])  # m/s to km/h

    return df
