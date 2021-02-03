import time
from time import sleep
import logging

while True:
    logging.info("{} App is running".format(time.time()))
    sleep(10)