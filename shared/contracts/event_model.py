import datetime
import json
import time
from dataclasses import dataclass

from shared.contracts import events_pb2


@dataclass(frozen=True)
class Event:
    name: str
    location: str
    start_date: datetime.date
    end_date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    banner_url: str
    site_name: str
    url: str

    @staticmethod
    def to_unix(dt: datetime.datetime) -> float:
        return time.mktime(dt.timetuple())

    def serialize(self, key_="json"):
        if key_ == "proto":
            _event = self._proto()
            return _event.SerializeToString()
        if key_ == "json":
            return self._json()

    def _proto(self):
        start_datetime = datetime.datetime.combine(self.start_date, self.start_time).timestamp()
        end_datetime = datetime.datetime.combine(self.end_date, self.end_time).timestamp()

        return events_pb2.Event(
            name=self.name,
            location=self.location,
            start_date=start_datetime,
            end_date=end_datetime,
            banner_url=self.banner_url,
            site_name=self.site_name,
            url=self.url
        )

    def _json(self):
        start_datetime = datetime.datetime.combine(self.start_date, self.start_time).timestamp()
        end_datetime = datetime.datetime.combine(self.end_date, self.end_time).timestamp()

        return json.dumps(
            {
                "name": self.name,
                "location": self.location,
                "start_date": str(start_datetime),
                "end_date": str(end_datetime),
                "banner_url": self.banner_url,
                "site_name": self.site_name,
                "url": self.url,
            }
        )

    @classmethod
    def create_event(
            cls,
            event_name: str,
            event_location: str,
            start_date: datetime.date,
            end_date: datetime.date,
            start_time: datetime.time,
            end_time: datetime.time,
            banner_url: str,
            site_name: str,
            event_url: str,
    ):
        return cls(
            event_name,
            event_location,
            start_date,
            end_date,
            start_time,
            end_time,
            banner_url,
            site_name,
            event_url,
        )
