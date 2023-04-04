
from dataclasses import dataclass

@dataclass
class PersistorSetting():
    database_id: str
    container_id: str
    partion_key: str

class Persistor():
    def persist(self, persitor_setting: PersistorSetting, data: any):
        raise NotImplementedError