from pocketbase import PocketBase, PocketBaseError
from lib.Pocketbase import Connector

COLLECTION_NAME = "cameras"


# Strategy: sends the brightness voltage level to Pockebase, updating a Device record. then a client can subscribe to its changes.
class PocketbaseBrightnessMeter: 
    def __init__(self, connector: Connector):
        self.connector = connector

    async def init(self):
        self.pb = await self.connector.connect()
    
    # brighrness is the current voltage level
    async def record(self, device_id, brightness, clip):
        collection = self.pb.collection(COLLECTION_NAME)

        updated = await collection.update(record_id=device_id, params={"brightness": brightness, "clip":self.mapClip(clip)})
        #print("bright:",brightness,"clip:",clip, self.mapClip(clip))

    # maps clipping value from device values to database field options
    def mapClip(self, c):
        map = {
            None: "no",
            -1: "lo",
            +1: "hi"
        }
        return map[c]

