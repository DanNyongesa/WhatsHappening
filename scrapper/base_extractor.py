from scrapper.event_model import Event
import logging
import copy

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
        "amqp_client": "",
        "events": [],
        "response": None,
        "amqp_exchange": "dundaa.events",
        "amqp_routing_key": "scrapped.events"
    }

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.default_config = copy.copy(self.DEFAULT_OPTIONS)
        self._add_options(**kwargs)

    def _add_options(self, **options):
        for key in self.default_config:
            if key in options:
                setattr(self,key, options.pop(key))
            else:
                setattr(self, key, self.default_config["key"])

    def run(self): raise NotImplementedError

    def get_result(self):
        if self.response and isinstance(self.response, dict):
            status_code = self.response.get("status_code", -1)
            if status_code in self.success_status_codes:
                self.result = "SUCCESS"

    def send_messages(self):
        self.logger.info("Sending messages")
        if len(self.events) > 0:
            # send messages to rabbit
            for event in self.events:
                self.ampqp_client.publish(exchange_type="direct",
                    routing_key=self.AMQP_ROUTING_KEY,
                    data=event.serialize("proto"),
                    exchange=self.AMQP_EXCHANGE
                )
        else:
            self.logger.info("no messages to send")

