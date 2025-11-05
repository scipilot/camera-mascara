import numpy as np
import asyncio
import os
from datetime import datetime
import io
from pocketbase import PocketBase, PocketBaseError, FileUpload
from pocketbase.models.dtos import RealtimeEvent
from dotenv import load_dotenv
from lib.ImageRender import ImageRender

load_dotenv()

#CONNECTION_URL = "http://10.200.72.143:8090"
#SUPERUSER_EMAIL = "admin@pocketbase.local"
#SUPERUSER_PASSWORD = "pocketbasepassword"
COLLECTION_NAME = "posts"

CONNECTION_URL = os.getenv('POCKETBASE_CONNECTION_URL')
SUPERUSER_EMAIL = os.getenv('POCKETBASE_SUPERUSER_EMAIL')
SUPERUSER_PASSWORD = os.getenv('POCKETBASE_SUPERUSER_PASSWORD')
print(f"# env {CONNECTION_URL} {SUPERUSER_EMAIL}  {SUPERUSER_PASSWORD}")

COLLECTION_NAME = "images"


# Strategy : Numpy save NPZ file 
class PocketbaseImageStore:   # (ImageStore)
    #def __init(self):

    # ouput is the image data array
    async def store(self, output, dims, title, stats):
        pb = await self.connect()
        
        # Get the collection instance we can work with
        collection = pb.collection("images")

        # Add a new record.
        #await collection.create(params={"data": output, "title": title})
      
        # encode in NPZ format for compat with direct-file method
        npz = io.BytesIO()
        np.savez(npz, output0=output)

        ren = ImageRender()
        img = io.BytesIO()
        ren.render(output, dims, img)

        # Upload a file
        # Note that FileUpload takes _tuples_, this is because you can have
        # fields that take multiple files. They are structed as:
        #   tuple(filename, content) or tuple(filename, content, mimetype)
        # Content can be anything file-like such as bytes, a string, a file descriptor from
        # open() or any io stream object. It uses httpx under the hood.
        record = await collection.create(
            params={
                "created": datetime.now(),
                "title": title,
                "stats": stats,
                "data": FileUpload((f"{title}.npz", npz )),
                "image": FileUpload((f"{title}.png", img )),
            }
        )

    # connects to Pocketbase and Authenticates
    async def connect(self):
        # Instantiate the PocketBase connector
        pb = PocketBase(CONNECTION_URL)
        # Authenticate as a superuser
        await pb.collection("_superusers").auth.with_password(SUPERUSER_EMAIL, SUPERUSER_PASSWORD)
        return pb

    # once-off - set up the database structure
    async def setup(self):
        pb = await self.connect()

        # TODO first remove an existing collection
        #collection = pb.collection("images")
        #await pb.collections.delete(collection["id"])

        # Create a collection to s"tore records in
        # It is a base collection (not "view" or "auth") with one column "content"
        # and it will have the regular "id" column.
        try:
            await pb.collections.create(
                {
                    "name": "images",
                    "type": "base",
                    "fields": [
                        {
                            "name": "created",
                            "type": "date",
                            "required": True,
                        },
                        {
                            "name": "title",
                            "type": "text",
                            "required": True,
                        },
                        {
                            "name": "stats",
                            "type": "text",
                            "required": False,
                        },
                        {
                            "name": "data",
                            "type": "file",
                            "required": True,
                        },
                        {
                            "name": "image",
                            "type": "file",
                            "required": False,
                        },

                    ],
                }
            )
        except PocketBaseError:
            # You probably ran this example before, and the collection already exists!
            # No problem, we'll continue as normal :)
            pass


