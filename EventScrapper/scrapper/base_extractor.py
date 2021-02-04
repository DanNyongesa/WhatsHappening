import logging
import copy

from shared.messengers.messenger import MessengerSetting


class BaseExtractor():
    """Exctractor base class
    Handles:
    1. Adding messages to rabbit
    2. Adding custom run options
    3. formatting the response
    Arguments:
        sevice_settings(dict): Settings for the service
    """
    DEFAULT_OPTIONS = {
        "success_status_codes": [],
        "site_name": "",
        "site_url": "",
        "events": [],
        "response": None,
        "messenger": None,
        "messenger_setting": MessengerSetting(),
        "routing_key": "scrapped_events"
    }

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.default_config = copy.copy(self.DEFAULT_OPTIONS)
        self._add_options(**kwargs)

    def _add_options(self, **options):
        for key in self.default_config:

            if key in options:
                self.__setattr__(key, options.pop(key))
                # setattr(self,key, options.pop(key))
            else:
                self.__setattr__(key, self.default_config[key])
                # setattr(self, key, self.default_config[key])

    def run(self):
        raise NotImplementedError

    def get_result(self):
        if self.response and isinstance(self.response, dict):
            status_code = self.response.get("status_code", -1)
            if status_code in self.success_status_codes:
                self.result = "SUCCESS"
            else:
                self.result = "FAILED"

    def log_response(self):
        if self.result == "SUCCESS":
            self.logger.info(f"extracted {self.site_name} successfully!")
        else:
            self.logger.error(f"Encountered error {self.response['status_code']} : {self.response['status_details']}")

    def send_messages(self):
        self.logger.info("Sending messages to {}".format(self.messenger_setting.key))
        self.logger.info("found %d events" % len(self.events))
        if self.messenger is not None:
            self.messenger.send_message(data=[event.serialize("json") for event in self.events], messenger_setting=self.messenger_setting)