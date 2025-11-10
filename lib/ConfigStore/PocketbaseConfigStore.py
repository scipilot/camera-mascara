from pocketbase import PocketBase, PocketBaseError, FileUpload
from pocketbase.models.dtos import RealtimeEvent
from lib.Pocketbase.Connector import Connector
from lib.PiConfig import ConfigStore # interface

COLLECTION_NAME = "cameras"


# Strategy : store in Pocketbase 
class PocketbaseConfigStore: #(CofnigStore)
    def __init__(self, connector: Connector):
        self.connector = connector 
    
    async def store(self, ID, PGA, SPS):
        pb = await self.connector.connect()
        collection = pb.collection(COLLECTION_NAME)

        record = await collection.update(
            record_id=ID,
            params={
                #"created": datetime.now(),
                "ADC_PGA": PGA,
                "ADC_SPS": SPS,
            }
        )

