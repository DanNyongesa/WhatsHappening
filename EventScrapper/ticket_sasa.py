import asyncio
import re
from datetime import datetime as dt

import bs4
import requests as req
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from EventScrapper import SUCCESS
from EventScrapper.base_extractor import BaseExtractor
from shared.contracts.event_model import Event
from EventScrapper.utils import build_request_response

class ScrapTicketSasa(BaseExtractor):
    def run(self):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._load_page_parse_events())
            # wait for all sessions to close
            loop.run_until_complete(asyncio.sleep(0.250))
            loop.close()
            self.response = build_request_response(SUCCESS, "requests successful")

        except Exception as exc:
            self.response = build_request_response(500, str(exc))

    async def _fetch_html_async(
        self, url: str, session: ClientSession, encoding="utf-8", **kwargs
    ) -> str:
        resp = await session.request(
            method="GET", url=url, raise_for_status=True, **kwargs
        )
        html_doc = await resp.text(encoding)
        return html_doc

    @staticmethod
    def _parse_time(time_str: str, _format="%I:%S %p") -> dt.time:
        return dt.strptime(time_str, _format).time()

    @staticmethod
    def _parse_end_date(date_tag: bs4.element.Tag, _format="%A%d%B%Y") -> dt.date:
        date_string = list(date_tag.find("li").strings)[-1]
        # remove all white spaces or unneccessary strings from date
        date_string = re.sub(r"\s+|,|:|st|nd|rd|th", "", date_string)
        try:
            return dt.strptime(date_string, _format).date()
        except Exception:
            return None

    @staticmethod
    def _parse_start_date(
        date_tag: bs4.element.Tag, _format="%Y-%m-%dT%H:%M"
    ) -> dt.date:
        date_str = date_tag.get("content")
        return dt.strptime(date_str, _format).date()

    async def _parse_event(
        self, banner_url: str, url: str, session: ClientSession, **kwargs
    ):
        # fetch html
        try:
            html_doc = await self._fetch_html_async(url=url, session=session, **kwargs)
        except Exception as exc:
            html_doc = await self._fetch_html_async(
                url=url, session=session, encoding="ISO-8859-1", **kwargs
            )
        # parse the page
        soup = BeautifulSoup(html_doc, "html.parser")
        event_name_contents = soup.find("h1", attrs={"itemprop": "name"}).strings
        event_name = list(event_name_contents)[0]

        location_tag = soup.find("span", attrs={"itemprop": "location"})
        event_location = location_tag.find("span", attrs={"itemprop": "name"}).text

        # parse event date and times
        event_times = soup.find("div", attrs={"class": "date-times"})
        _start, _end = map(lambda x: x.string, event_times.find_all("span"))
        event_start_time = self._parse_time(_start)
        event_end_time = self._parse_time(_end)
        start_date_html = soup.find("div", attrs={"itemprop": "startDate"})
        event_start_date = self._parse_start_date(start_date_html)
        end_date_html = soup.find("ul", attrs={"class": "evt-specs"})
        event_end_date = self._parse_end_date(end_date_html)
        if event_end_date is None:
            event_end_date = event_start_date

        # load event object
        event = Event.create_event(
            event_name=event_name.strip(),
            event_location=event_location.strip(),
            start_date=event_start_date,
            end_date=event_end_date,
            start_time=event_start_time,
            end_time=event_end_time,
            banner_url=banner_url.strip(),
            event_url=url,
            site_name=self.site_name,
        )
        self.events.append(event)

    async def _load_page_parse_events(self, **kwargs) -> None:

        base_url = self.site_url
        url = base_url + "/events"
        html_doc = req.get(url).content

        soup = BeautifulSoup(html_doc, "html.parser")

        events_html = soup.select('div[itemtype="http://schema.org/Event"]')

        tasks = []
        async with ClientSession() as session:
            for event_html in events_html:
                # print(each)
                event_banner_tag = event_html.find("img")
                event_banner = event_banner_tag["src"]
                event_dt = event_html.select_one(".date-box")
                event_endpoint = event_dt.get("href")
                url = base_url + event_endpoint

                tasks.append(
                    self._parse_event(
                        banner_url=event_banner, url=url, session=session, **kwargs
                    )
                )

            await asyncio.gather(*tasks)
