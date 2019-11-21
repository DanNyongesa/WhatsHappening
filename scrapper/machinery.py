import logging
import sys
import copy
import datetime
from dataclasses import dataclass
import json


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

    def to_json(self):
        return json.dumps(
            {
                "name": self.name,
                "location": self.location,
                "start_date": self.start_date,
                "end_date": self.end_date,
                "start_time": self.start_time,
                "end_time": self.end_time,
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


class BaseAction(object):
    """Action base class
    Handles:
    1. Adding messages to rabbit
    2. Adding custom run options
    3. formatting the response
    Arguments:
        sevice_settings(dict): Settings for the service
    """

    DEFAULT_OPTIONS = {"success_status_codes": []}

    def __init__(self, payload: dict, **kwargs):
        """
        Setups the action class. Options have to be setup in the `DEFAULT_OPTIONS`
        class variable dictionary firts.
        Argumennts:
            payload(dict): object to be processed by this action.
        """
        self.payload = payload
        self.response = None
        self.success_status_codes = []
        self.result = "FAILED"
        self.logger = logging.getLogger(self.__class__.__name__)
        self.default_config = copy.copy(self.DEFAULT_OPTIONS)
        self._add_options(**kwargs)

    def _add_options(self, **options):
        for key in self.default_config:
            if key in options:
                setattr(self, key, options.pop(key))
            else:
                setattr(self, key, self.default_config[key])

    def run(self):
        return NotImplementedError

    def get_result(self):
        """
        get and set result of this action
        """
        if self.response and isinstance(self.response, dict):
            status_code = self.response.get("status_code", -1)
            if status_code in self.success_status_codes:
                self.result = "SUCCESS"

    def log_response(self):
        """
        Log response based on status code returned
        """
        if self.result == "SUCCESS":
            self.logger.info(self.response)
        else:
            self.logger.error(self.response)

    def send_messages(self):
        return NotImplementedError


class ActionEventManager(object):
    """
    Action event manager
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __enter__(self):
        return self.class_instance

    def __exit__(self, *exc):
        self.class_instance.send_messages()
        self.class_instance.get_result()
        self.class_instance.log_response()


def run_action_class(class_instance, entry_function="run"):
    with ActionEventManager(class_instance=class_instance):
        action = getattr(class_instance, entry_function)
        action()
    return class_instance


def build_request_response(status_code, status_details=None):
    """
    Build a response for a validation request.
    Arguments:
        status_code(int).
        status_lookup(dict): k-v pairs of code and description. 
        status_details(string): Optional details to add.
    Returns:
        dictionary.
    """
    response = {"status_code": status_code, "status_details": status_details}
    return response
