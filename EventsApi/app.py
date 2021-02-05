from flask import Flask, jsonify
import os
from shared.persistors.cosmos_client import DundaaCosmosClient
from shared.persistors.persistor import PersistorSetting
from shared.services import events_api_setting as service_setting
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from flask.views import MethodView

cosmos_client = DundaaCosmosClient(
        cosmos_endpoint=os.environ.get("COSMOS_ACCOUNT_URI"),
        primary_key=os.environ.get("COSMOS_ACCOUNT_KEY")
    )

persistor_setting = PersistorSetting(
        container_id=service_setting.cosmos_container_id,
        database_id=service_setting.cosmos_database_id,
        partion_key="/site_name"
    )

class EventsAPI(MethodView):

    def get(self):
        events = cosmos_client.query(
            persistor_setting
        )
        return jsonify({
            "events": events
        })

app.add_url_rule(
    '/events/',
    view_func=EventsAPI.as_view('events')
)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000
    )
