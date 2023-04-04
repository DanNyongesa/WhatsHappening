import datetime
import re
import time

from bs4 import BeautifulSoup
from EventScrapper import SUCCESS, UNKNOWN
from EventScrapper.base_extractor import BaseExtractor
from shared.contracts.event_model import Event
from EventScrapper.utils import build_request_response
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ScrapMookh(BaseExtractor):
    def __init__(self, *args, **kwargs):
        driver = kwargs.get("driver")
        if driver is None:
            raise ValueError("Could not instatiate mookh scrpper. Missing value for driver!")
        self.driver = driver
        super().__init__(
            *args,
            **kwargs,
            success_status_codes=[SUCCESS],
            site_name="mookh",
            site_url="https://mookh.com",
            response=None
        )
        self.endpoint = "/events"
        self.event_links = []

    def run(self):
        try:
            self._prepare_driver()
            self._get_all_events()
            self._parse_events()
            self.response = build_request_response(SUCCESS, "requests successful")
        except Exception as exc:
            self.response = build_request_response(UNKNOWN, str(exc))

    def _prepare_driver(self, delay=10):
        if self.response is not None:
            return
        url = self.site_url + self.endpoint
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, delay).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="app"]/div[1]/div[1]/div[2]/div/div[1]/div[2]/div[1]/div/div/h3')
                )
            )
        except Exception as exc:
            self.response = build_request_response(UNKNOWN, f"Timed out while loading page with exception {exc}")

    def _get_all_events(self):
        if self.response is not None:
            return

        h3s = []
        # iterate through all pages, use number of h3 elements found on page to determine end of scrolling
        retry = True
        while True:
            try:
                pagination_button = self.driver.find_element_by_xpath("//*[contains(text(), 'Load More..')]")
                #     pagination_button.click()
                self.driver.execute_script("arguments[0].click();", pagination_button)
            except Exception as exc:  # an exception will be raised if no load more button is found, in that case wait a little bit more and try to get the button again
                time.sleep(10)
                pagination_button = self.driver.find_element_by_xpath("//*[contains(text(), 'Load More..')]")
                #   
                self.driver.execute_script("arguments[0].click();",
                                           pagination_button)  # https://stackoverflow.com/questions/48665001/can-not-click-on-a-element-elementclickinterceptedexception-in-splinter-selen

            time.sleep(5)
            h3s_ = self._get_h3s(self.driver.page_source)
            is_same_page = len(h3s_) == len(h3s)

            if is_same_page and retry is True:
                retry = False
                # page took long to load wait a little bit more and load again
                time.sleep(3)
                continue

            if is_same_page and retry is False:
                self.logger.info("loaded all events")
                retry = True
                break

            h3s = h3s_

        self.event_links = self._extract_event_links(self.driver.page_source)

    def _parse_events(self):
        if self.response is not None:
            return
        for event_link in self.event_links:
            event_html = self._get_event(event_link)
            event = self._parse_event(event_html, event_link)
            self.events.append(event)

    def _get_event(self, url: str, delay=10):
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, delay).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="imageDisplay"]')
                )
            )
            print("Loaded page successfully")
        except Exception as exc:
            self.logger.warning(f"Timed out while loading page with exception {exc}")
        return self.driver.page_source

    def _parse_event(self, event_url, page_source):
        event_soup = BeautifulSoup(page_source, "html.parser")
        event_name = event_soup.find('h4').text
        event_date = event_soup.find('p', class_='eventDate').text
        event_location = event_soup.find('span', class_="location-marker").text
        image_tag = event_soup.find('div', id='imageDisplay')
        banner_url = re.search(r'https://files.mookh.com/uploads/[a-zA-Z0-9./-_]+', image_tag.attrs['style']).group(0)
        event_time = event_soup.find('p', class_='owner').find('span').text
        start_time, end_time = [t.replace(' ', '') for t in event_time.split('-')]
        t_format = '%I:%M%p'
        start_time = datetime.datetime.strptime(start_time, t_format).time()
        end_time = datetime.datetime.strptime(end_time, t_format).time()
        dates = event_date.split("-")
        # print(dates)
        start_date = end_date = dates[0]
        if len(dates) > 1:
            end_date = dates[1]

        start_date = self._parse_date(start_date)
        end_date = self._parse_date(end_date)
        event = Event.create_event(
            event_name,
            event_location,
            start_date,
            end_date,
            start_time,
            end_time,
            banner_url,
            self.site_name,
            event_url,
        )
        return event

    @staticmethod
    def _get_h3s(page_source):
        soup = BeautifulSoup(page_source, "html.parser")
        h3s = soup.find_all("h3", class_=re.compile('^jss[0-9]{3}'))
        return [h3.text for h3 in h3s]

    @staticmethod
    def _extract_event_links(page_source):
        soup = BeautifulSoup(page_source, "html.parser")
        event_links = soup.find_all("a", href=re.compile(r"^/event/[a-zA-Z]*"))
        event_links = [i for i in set([event_link.get('href') for event_link in event_links])]
        return event_links

    @staticmethod
    def _parse_date(dt: str, d_format='%a%b%d%Y') -> datetime.date:
        # remove all formatings and spaces
        dt = re.sub(r'\s+|,|:|st|nd|rd|th', '', dt)
        return datetime.datetime.strptime(dt, d_format).date()
