"""
bicycledigest.py

Package for processing data collected with the bicycle logger.
"""

import argparse
import logging

from transform.session import BicycleSession

# --------------------- LOGGING

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


# --------------------- MAIN


def main() -> None:

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--ButtonFile", help="Path of the button file relative to repository dir.")
    parser.add_argument("-g", "--GPSFile", help="Path of the GPS file relative to repository dir.")
    parser.add_argument("-l", "--LidarFile", help="Path of the lidar file relative to repository dir.")
    parser.add_argument("-r", "--RadarFile", help="Path of the radar file relative to repository dir.")
    args = parser.parse_args()

    if args.ButtonFile and args.GPSFile and args.LidarFile:  # either all files passed in commandline
        source_files = {
            "button_file": args.ButtonFile,
            "gps_file": args.GPSFile,
            "lidar_file": args.LidarFile,
            "radar_file": args.RadarFile,
        }
        BicycleSession(sources=source_files)
    else:  # or all files come from config
        BicycleSession()

    # s.print_info()


# ---------------------- RUNNING DIRECTLY

if __name__ == "__main__":

    main()
