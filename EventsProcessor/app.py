import json
import logging
import os
import sys

from shared.contracts.Messages import EventBlobCreated
from shared.messengers.amqp_sdk import DundaaAMQPSDK
from shared.messengers.azure_blob import DundaaBlobClient
from shared.messengers.messenger import MessageConsumerSetting
from shared.persistors.cosmos_client import DundaaCosmosClient
from shared.persistors.persistor import PersistorSetting
from shared.services import event_processor_setting as service_setting

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)

logger = logging.getLogger("EventsProcessor")

amqp_messenger = DundaaAMQPSDK(
    amqp_host=os.environ.get("AMQP_HOST"),
    amqp_url=os.environ.get("AMQP_URL"),
    logger=logger
)



def write_cosmos(ch, method, properties, body):
    data = json.loads(body.decode())
    try:
        message = EventBlobCreated(
            **data
        )
    except Exception as exc:
        logger.error("message could not be parsed")
        return -1

    logger.info("received event %s " % message)
    blob_json = get_blob(data=message)

    logger.info("writing %s event items to cosmos" % len(blob_json))

    cosmos_client = DundaaCosmosClient(
        cosmos_endpoint=os.environ.get("COSMOS_ACCOUNT_URI"),
        primary_key=os.environ.get("COSMOS_ACCOUNT_KEY")
    )

    persistor_setting = PersistorSetting(
        container_id=service_setting.cosmos_container_id,
        database_id=service_setting.cosmos_database_id,
        partion_key="/site_name"
    )

    cosmos_client.persist(
        data=blob_json,
        persitor_setting=persistor_setting
    )
    logger.info("Event items processing complete")
    # schedule web scrapper

    return True


def get_blob(data: EventBlobCreated):
    azure_blob_connection_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    azure_blob_client = DundaaBlobClient(
        connection_string=azure_blob_connection_str,
        logger=logger
    )
    container_name, folder, blob = data.url.split("/")[-3:]
    blob_name = "%s/%s" % (folder, blob)

    logger.info("retrieving blob %s" % blob_name)

    json_blob = azure_blob_client.read(
        container_name=container_name,
        blob_path=blob_name
    )
    return json_blob


# listen for blob created events
message_consumer_setting = MessageConsumerSetting(
    service_name=service_setting.listen.exchange,
    listen_keys=service_setting.listen.keys
)

amqp_messenger.consume_messages(
    consumer_settings=message_consumer_setting,
    callback=write_cosmos
)
