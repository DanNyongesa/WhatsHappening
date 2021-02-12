import logging
import os
import sys
import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from EventScrapper import SUCCESS
from EventScrapper.base_extractor import WebScrapperArgs
from EventScrapper.ticket_sasa import ScrapTicketSasa
from EventScrapper.utils import run_extractor
from shared.messengers.azure_blob import DundaaBlobClient
from shared.messengers.messenger import BlobMessengerSetting, MessageConsumerSetting
from shared.services import web_scrapper_setting
from shared.messengers.amqp_sdk import DundaaAMQPSDK
from shared.contracts.Messages import ScrapSite
from shared.kenya_time import kenyatime


logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)


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


def run(ch, method, properties, body):
    try:
        message = ScrapSite.from_json(
            body.decode()
        )
        logger.info("Received message %s" % message)
    except Exception as exc:
        logger.error("message could not be parsed")
        raise
    td = kenyatime() - kenyatime()
    td = td.total_seconds()
    if td < message.delay:
        logger.error("Time difference %d. message has not reached maturity, Sleeping until function is ready" % td)
        time.sleep(td)
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
        key=web_scrapper_setting.key,
        service_name=web_scrapper_setting.name
    )
    # load extractors
    ticket_sasa_extractor_args = WebScrapperArgs(
        messenger_setting=messenger_setting,
        messenger=azure_blob_client,
        success_status_codes=[SUCCESS],
        site_name="ticketsasa",
        site_url="https://www.ticketsasa.com"
    )
    ticket_sasa_extractor = ScrapTicketSasa(args=ticket_sasa_extractor_args)

    extractors = []
    extractors.append(ticket_sasa_extractor)

    # run
    for extractor in extractors:
        run_extractor(extractor)


if __name__ == "__main__":
    # consume for delayed queue
    # listen for blob created events
    logger = logging.getLogger("webScrapper")

    amqp_messenger = DundaaAMQPSDK(
        amqp_host=os.environ.get("AMQP_HOST"),
        amqp_url=os.environ.get("AMQP_URL"),
        logger=logger
    )

    message_consumer_setting = MessageConsumerSetting(
        service_name=web_scrapper_setting.listen.exchange,
        listen_keys=web_scrapper_setting.listen.keys

    )

    amqp_messenger.consume_messages(
        consumer_settings=message_consumer_setting,
        callback=run
    )