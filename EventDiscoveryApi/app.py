import json
import logging
import os
import sys

from flask import Flask
from flask import jsonify, request, abort

from shared.contracts.Messages import EventBlobCreated, ScrapSite
from shared.messengers.amqp_sdk import DundaaAMQPSDK, MessengerSetting
from shared.services import event_discovery_setting

SCRAPPER_DELAY = 100

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)

app = Flask(__name__)

amqp_messenger = DundaaAMQPSDK(
    amqp_host=os.environ.get("AMQP_HOST"),
    amqp_url=os.environ.get("AMQP_URL")
)


@app.route('/api/NewEvents', methods=["GET", "POST"])
def new_events():
    app.logger.info("request headers %s" % request.headers)
    req_data = request.data.decode()

    req_json = json.loads(req_data)
    try:
        _data = req_json["data"]
        del _data["storageDiagnostics"]
        blob_created_message = EventBlobCreated(**_data)
    except Exception as exc:
        app.logger.error(str(exc))
        abort(400)

    app.logger.info("Sending message %s" % blob_created_message)
    messenger_setting = MessengerSetting(
        service_name=event_discovery_setting.name,
        key=event_discovery_setting.key
    )
    amqp_messenger.send_message(data=blob_created_message.to_json(), messenger_setting=messenger_setting)

    # scheduled scrapper
    app.logger.info("Scheduling web scrapper")
    scheduled_scrap = ScrapSite(
        delay=SCRAPPER_DELAY
    )
    delayed_messenger_setting = MessengerSetting(
        service_name=event_discovery_setting.delayed_exchange,
        key=event_discovery_setting.key
    )
    amqp_messenger.send_message(
        data=scheduled_scrap.to_json(),
        messenger_setting=delayed_messenger_setting,
        delay=SCRAPPER_DELAY
    )

    return jsonify({
        "message": "Accepted"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
