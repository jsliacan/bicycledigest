"""
bicycledigest.py

Package for processing data collected with the bicycle logger.
"""

import logging

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
    # session.print_info()
