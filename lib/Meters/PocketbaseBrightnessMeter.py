from pocketbase import PocketBase, PocketBaseError
from lib.Pocketbase import Connector

COLLECTION_NAME = "cameras"


# Strategy: sends the brightness voltage level to Pockebase, updating a Device record. then a client can subscribe to its changes.
class PocketbaseBrightnessMeter: 
    def __init__(self, connector: Connector):
        self.connector = connector

    # brighrness is the current voltage level
    async def record(self, device_id, brightness):
        self.pb = await self.connector.connect()
        collection = self.pb.collection(COLLECTION_NAME)

        updated = await collection.update(record_id=device_id, params={"brightness": brightness})
        print(updated)


