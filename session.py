import logging
import os

# import matplotlib.pyplot as plt
import pandas as pd
import yaml

from event import *


class BicycleSession:
    """
    Class encapsulating the concept of a 'session' (1 ride).
    """

    def __init__(self, config="config.yml", sources={"": ""}, output_dir="out") -> None:

        with open(config, encoding="utf-8", mode="r") as file:
            self.config = yaml.safe_load(file)

        self.threshold = -1
        if self.config["eventType"]["oc"] and self.config["eventType"]["ot"]:
            self.threshold = self.config["eventType"]["threshold"]["value"]

        self.events = []
        
        self.output_dir = output_dir
        self.button_file = self.config["sources"]["button_file"]
        self.lidar_file = self.config["sources"]["lidar_file"]
        self.gps_file = self.config["sources"]["gps_file"]
        if not "" in sources:
            self.button_file = sources["button_file"]
            self.lidar_file = sources["lidar_file"]
            self.gps_file = sources["gps_file"]

        self.delta = self.config["detection"]["delta"]["value"]
        self.epsilon = self.config["detection"]["epsilon"]["value"]

        self.button_df = self.load_button_file()
        self.gps_df = self.load_gps_file()
        self.lidar_df = self.load_lidar_file()
        self.df_ot, self.df_oc = self.decide_otoc()
        self.make_events()

    def print_info(self) -> None:
        """
        Print summary info about the session.
        """
        print()
        print("-" * 20, "SESSION INFO", "-" * 20)
        print("button_file:", self.button_file)
        print("-" * 10)
        print("threshold:", self.threshold)
        print("-" * 10)
        print("dataframe OTs:\n", self.df_ot)
        print("-" * 10)
        print("dataframe OCs:\n", self.df_oc)
        print("-" * 10 + "\n")

    def load_button_file(self) -> pd.DataFrame:
        """
        Read in button file and return a dataframe.
        """

        filename = os.path.basename(self.button_file)

        logging.info("Loading button CSV file: %s", filename)

        df = pd.read_csv(self.button_file, on_bad_lines="skip")
        df = df.loc[df["duration"] > 0.01]
        df = df.assign(time=pd.to_datetime(df["time"]))  # convert string UTC time to pd.DateTime
        df = df.assign(timedelta=pd.to_timedelta(df["duration"], unit="s"))  # timedelta = duration as pd.Timedelta
        df = df.assign(press_start=df["time"] - df["timedelta"])

        return df

    def load_gps_file(self) -> pd.DataFrame:
        """
        Read in GPS file and return a dataframe.
        """

        filename = os.path.basename(self.gps_file)
        logging.info("Loading gps CSV file: %s", filename)

        df = pd.read_csv(self.gps_file, on_bad_lines="skip")
        df = df.assign(time=pd.to_datetime(df["time"]))  # convert string UTC time to pd.DateTime
        df = df.astype({"latitude": float, "longitude": float})  # make sure values are floats

        return df

    def load_lidar_file(self) -> pd.DataFrame:
        """
        Read in lidar file and return a dataframe.
        """

        filename = os.path.basename(self.lidar_file)

        logging.info("Loading lidar CSV file: %s", filename)

        df = pd.read_csv(self.lidar_file, on_bad_lines="skip")
        df = df.assign(time=pd.to_datetime(df["time"]))  # convert strin UTC time to pd.DateTime

        if "distance [cm]" in df.columns:
            logging.info("Removing units from variable names in the header in %s.", filename)
            df.rename(columns={"distance [cm]": "distance"}, inplace=True)

        return df

    def make_events(self) -> None:
        """
        Create an event for each button press.

        TODO:
        - Extend to OCs as well.
        """
        logging.info("Making events.")

        ldf = self.lidar_df
        gpsdf = self.gps_df

        # get excerpts based on button presses
        for _, bp in self.df_ot.iterrows():
            ps = bp["press_start"]

            excerpt_start = ps - pd.to_timedelta("3s")  # 3 seconds look-back
            excerpt_end = ps

            edf_lidar = ldf.loc[(ldf["time"] > excerpt_start) & (ldf["time"] < excerpt_end)]  # excerpt df for lidar
            edf_gps = gpsdf.loc[(gpsdf["time"] > excerpt_start) & (gpsdf["time"] < excerpt_end)]  # excerpt df for lidar
            e = Event(
                etype="ot",
                output_dir=self.output_dir,
                button_press=bp,
                lidar_excerpt=edf_lidar,
                gps_excerpt=edf_gps,
                delta=self.delta,
                epsilon=self.epsilon,
            )
            self.events.append(e)

            # plt.scatter(range(len(excerpt_df["time"])), excerpt_df["distance"])
            # plt.savefig(os.path.join("out", "test" + e.hash + ".png"))
            # plt.clf()

    def decide_otoc(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Return dataframes for OT presses and OC presses based on button press
        lengths.
        """

        logging.info("Classifying OTs and OCs from button presses.")

        OTs = self.button_df.loc[self.button_df["duration"] > self.threshold]
        OCs = self.button_df.loc[self.button_df["duration"] <= self.threshold]

        logging.info("Found %d OTs and %d OCs.", len(OTs), len(OCs))

        return OTs, OCs
