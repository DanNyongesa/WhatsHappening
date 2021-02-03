import logging
import sys
import copy
import datetime
from dataclasses import dataclass
import json

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)

# codes
SUCCESS = 101
UNKNOWN = 600


