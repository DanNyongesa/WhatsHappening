import logging
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from EventScrapper.scrapper.ticket_sasa import ScrapTicketSasa
from EventScrapper.scrapper.utils import run_extractor
from shared.messengers.azure_blob import DundaaBlobClient
from shared.messengers.messenger import BlobMessengerSetting

# reduce log level
_loggers = []
_loggers.append("pika")
_loggers.append("asyncio")
_loggers.append("urlib3")
_loggers.append("selenium")
for logger in _loggers:
    logging.getLogger(logger).setLevel(logging.WARNING)


def set_chrome_options() -> Options:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return chrome_options


def run(config=None):
    # prepare selenium driver
    chrome_options = set_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)

    # get blob service client
    azure_blob_connection_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    azure_blob_client = DundaaBlobClient(
        connection_string=azure_blob_connection_str,
        logger=logging.getLogger(__name__).setLevel(logging.WARNING)
    )
    # define how messages from this service are routed
    messenger_setting = BlobMessengerSetting(
        key="events",
        service_name="WebScrapper"
    )
    # load extractors
    ticket_sasa_extractor = ScrapTicketSasa(messenger=azure_blob_client, messenger_setting=messenger_setting)

    extractors = []
    extractors.append(ticket_sasa_extractor)

    # run
    for extractor in extractors:
        run_extractor(extractor)


if __name__ == "__main__":
    run()
