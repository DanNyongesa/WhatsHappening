import json
from dataclasses import dataclass, asdict


@dataclass
class EventBlobCreated():
    """
    "data": {
        "api": "PutBlob",
        "clientRequestId": "11df48ac-676b-11eb-a3c4-0242ac180002",
        "requestId": "77b7a336-701e-008f-7777-fb1e0c000000",
        "eTag": "0x8D8C98EF66A9119",
        "contentType": "application/octet-stream",
        "contentLength": 2822,
        "blobType": "BlockBlob",
        "url": "https://stdundaa.blob.core.windows.net/webscrapper/events/35448797-24f9-4a57-bbe1-9a78b2650147.json",
        "sequencer": "000000000000000000000000000008A5000000000025ee94",
        "storageDiagnostics": {
            "batchId": "c059dcf1-3006-009e-0077-fb704b000000"
        }
    }
    """
    api: str
    clientRequestId: str
    requestId: str
    eTag: str
    contentType: str
    contentLength: int
    blobType: str
    url: str
    sequencer: str

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict())