import os
import uuid
import json
import logging

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient
from shared.messengers.messenger import Messenger, BlobMessengerSetting

class DundaaBlobClient(Messenger):
    def __init__(self, connection_string: str,logger=None):
        if logger is None:
            logger = logging.getLogger(__name__)

        self.logger = logger
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)


    def get_container_client(self, container_name: str):
        return self.blob_service_client.create_container(container_name)

    def __create_container(self, container_name: str):
        try:
            new_container = self.blob_service_client.create_container(container_name)
            properties = new_container.get_container_properties()
        except ResourceExistsError:
            self.logger.info("Container already exists.")


    def write(self, data: iter, container_name: str, folder=None):
        # Create a local directory to hold blob data
        local_path = "/tmp/.data"
        try:
            os.mkdir(local_path)
        except FileExistsError as exc:
            pass

        # Create a file in the local data directory to upload and download
        local_file_name = str(uuid.uuid4()) + ".json"
        upload_file_path = os.path.join(local_path, local_file_name)

        # Write text to the file
        with open(upload_file_path, 'w') as outfile:
            json.dump(data, outfile)

        # Create a blob client using the local file name as the name for the blob
        self.logger.info("attempting to create container %s" % container_name)
        self.__create_container(container_name)
        if folder is None:
            blob_file_name = local_file_name
        else:
            blob_file_name = "%s/%s" % (folder, local_file_name)
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_file_name)

        self.logger.info("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

        # Upload the created file
        with open(upload_file_path, "rb") as data:
            blob_client.upload_blob(data)


    def send_message(self, messenger_setting: BlobMessengerSetting, data: iter):
        self.write(container_name=messenger_setting.container_name, folder=messenger_setting.key ,data=data)
