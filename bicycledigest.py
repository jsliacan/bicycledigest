import os
import logging
import yaml

import pandas as pd 

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s',
                    encoding='utf-8', 
                    level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler("digest.log"),
                        logging.StreamHandler()     # logging 'info' level to console as well
                        ]
                    )

class BicycleSession:

    def __init__(self, config='config.yml'):

        with open(config, 'r') as file:
            self.config = yaml.safe_load(file)
        self.threshold = self.config['threshold']
        self.button_file = self.config['button_file']

        self.button_df          = self.load_button_file()
        self.df_ot, self.df_oc  = self.decide_otoc()

    def print_info(self):
        """
        Print summary info about the session.
        """
        print()
        print('-'*20, "SESSION INFO", '-'*20)
        print("button_file:", session.button_file)
        print('-'*10)
        print("threshold:", session.threshold)
        print('-'*10)
        print("dataframe OTs:\n", session.df_ot)
        print('-'*10)
        print("dataframe OCs:\n", session.df_oc)
        print('-'*10+"\n")

    def load_button_file(self):
        """
        Read in `filename` and return a dataframe.
        """

        filename = os.path.basename(self.button_file)
        
        logging.info(f"Reading button CSV file: {filename}")
        
        df = pd.read_csv(self.button_file, on_bad_lines='skip')
        
        logging.info(f"Done.")
        
        return df

    def decide_otoc(self):
        """
        Return dataframes for OT presses and OC presses based on button press lengths.
        """
        
        logging.info(f"Classifying OTs and OCs from button presses.")

        OTs = self.button_df.loc[self.button_df['duration'] > self.threshold]
        OCs = self.button_df.loc[self.button_df['duration'] <= self.threshold]
        
        logging.info(f"Found {len(OTs)} OTs and {len(OCs)} OCs.")
        logging.info("Done.")

        return OTs, OCs

if __name__ == "__main__":

    session = BicycleSession()
    session.print_info()
