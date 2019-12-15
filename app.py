from scrapper.ticket_sasa import ScrapTicketSasa
import logging
from scrapper.amqp_sdk import DundaaAMQPSDK
from scrapper.utils import run_extractor
from selenium import webdriver
from scrapper.mookh import ScrapMookh


# reduce log level
_loggers = ["pika", "asyncio", "urllib3"]
for logger in _loggers:
    logging.getLogger(logger).setLevel(logging.WARNING)

def run(config=None):
    # load amqp sdk
    amqp_url = (
        "amqp://qprfemrn:P__TkhouA0w9w2-GBbQcgBpw0Wg3sVav@shrimp.rmq.cloudamqp.com/qprfemrn"
    )
    amqp = DundaaAMQPSDK(amqp_url=amqp_url)

    # prepare selenium driver
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--headless")
    driver = webdriver.Chrome("chromedriver_win32\chromedriver.exe", options=options)

    # load extractors
    ticket_sasa_extractor = ScrapTicketSasa(amqp_client=amqp)
    mookh_extractor = ScrapMookh(amqp_client=amqp, driver=webdriver)
    extractors = [mookh_extractor, ticket_sasa_extractor]
    # run 
    for extractor in extractors:
        run_extractor(extractor)

if __name__ == "__main__":
    run()