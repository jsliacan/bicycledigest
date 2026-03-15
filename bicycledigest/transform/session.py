import logging

import pandas as pd
import yaml
from constants import CONFIG_PATH, REPOSITORY_PATH
from extract.sensor_files import *
from transform.event import *


class BicycleSession:
    """
    Class encapsulating the concept of a 'session' (1 ride).
    """

    def __init__(self, config=CONFIG_PATH, sources={"": ""}) -> None:

        with open(config, encoding="utf-8", mode="r") as config_file:
            self.config = yaml.safe_load(config_file)

        # SOURCE FILES
        self.button_file = os.path.join(REPOSITORY_PATH, self.config["sources"]["button_file"])
        self.lidar_file = os.path.join(REPOSITORY_PATH, self.config["sources"]["lidar_file"])
        self.gps_file = os.path.join(REPOSITORY_PATH, self.config["sources"]["gps_file"])
        self.radar_file = os.path.join(REPOSITORY_PATH, self.config["sources"]["radar_file"])
        if not "" in sources:
            self.button_file = os.path.join(REPOSITORY_PATH, sources["button_file"])
            self.lidar_file = os.path.join(REPOSITORY_PATH, sources["lidar_file"])
            self.gps_file = os.path.join(REPOSITORY_PATH, sources["gps_file"])
            self.radar_file = os.path.join(REPOSITORY_PATH, sources["radar_file"])

        # DETECTION PARAMETERS
        self.threshold = -1
        if self.config["eventType"]["oc"] and self.config["eventType"]["ot"]:
            self.threshold = self.config["eventType"]["threshold"]["value"]
        self.delta = self.config["detection"]["delta"]["value"]
        self.epsilon = self.config["detection"]["epsilon"]["value"]

        self.button_df = read_button_file(self.button_file)
        self.gps_df = read_gps_file(self.gps_file)
        self.lidar_df = read_lidar_file(self.lidar_file)
        self.radar_df = read_radar_file(self.radar_file)

        self.df_ot, self.df_oc = self.decide_otoc()

        self.events = []
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
