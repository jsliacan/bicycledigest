import os
import pathlib

REPOSITORY_PATH = pathlib.Path(__file__).parents[1]
CONFIG_PATH = os.path.join(REPOSITORY_PATH, "config.yml")
