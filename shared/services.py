from dataclasses import dataclass

SERVICE_NAME = "DundaaEvents"
SITE_EVENTS_CONTAINER= "site_events"

@dataclass
class Listen():
    exchange: str
    keys: [str]

@dataclass
class ServiceSetting():
    name: str
    key: str
    listen: Listen = None
    delayed_exchange: str = None
    cosmos_container_id: str = "site_events"
    cosmos_database_id: str = "dundaa"

    def __post_init__(self):
        self.delayed_exchange = "x-delayed-%s" % self.name.lower()



event_discovery_setting = ServiceSetting(
    name=SERVICE_NAME,
    key="discovered_events"
)


event_processor_setting = ServiceSetting(
    name=SERVICE_NAME,
    key="processed_events",
    listen=Listen(
        exchange=event_discovery_setting.name,
        keys=[event_discovery_setting.key]
    )
)

web_scrapper_setting = ServiceSetting(
    name=SERVICE_NAME,
    key="web_scrapper",
    listen=Listen(
        exchange=event_discovery_setting.delayed_exchange,
        keys=[event_discovery_setting.key]
    )
)

events_api_setting = ServiceSetting(
    name=SERVICE_NAME,
    key="events_api"
)