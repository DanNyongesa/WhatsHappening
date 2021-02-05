from dataclasses import dataclass

SERVICE_NAME = "DundaaEvents"
SITE_EVENTS_CONTAINER= "site_events"

@dataclass
class ServiceSetting():
    name: str
    key: str
    listen: [str]
    cosmos_container_id: str = "site_events"
    cosmos_database_id: str = "dundaa"


event_discovery_setting = ServiceSetting(
    name=SERVICE_NAME,
    key="discovered_events",
    listen=[]
)



web_scrapper_setting = ServiceSetting(
    name=SERVICE_NAME,
    key="web_scrapper",
    listen=[]
)


event_processor_setting = ServiceSetting(
    name=SERVICE_NAME,
    key="processed_events",
    listen=[
        event_discovery_setting.key
    ]
)

events_api_setting = ServiceSetting(
    name=SERVICE_NAME,
    key="events_api",
    listen=[
        "http"
    ]
)