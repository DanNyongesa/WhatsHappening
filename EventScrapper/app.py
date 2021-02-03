import logging

from EventScrapper.scrapper.amqp_sdk import DundaaAMQPSDK
from EventScrapper.scrapper.ticket_sasa import ScrapTicketSasa
from EventScrapper.scrapper.utils import run_extractor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
    # load amqp sdk
    amqp_url = (
        "amqp://qprfemrn:P__TkhouA0w9w2-GBbQcgBpw0Wg3sVav@shrimp.rmq.cloudamqp.com/qprfemrn"
    )
    amqp = DundaaAMQPSDK(amqp_url=amqp_url)

    # prepare selenium driver
    chrome_options = set_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)

    # load extractors
    ticket_sasa_extractor = ScrapTicketSasa(amqp_client=amqp)
    # mookh_extractor = ScrapMookh(amqp_client=amqp, driver=driver)
    extractors = []
    # extractors.append(mookh_extractor)
    extractors.append(ticket_sasa_extractor)
    # run
    for extractor in extractors:
        run_extractor(extractor)


if __name__ == "__main__":
    run()
