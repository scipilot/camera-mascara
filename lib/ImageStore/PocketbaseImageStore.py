import numpy as np
import asyncio
import os
from datetime import datetime
import io
from pocketbase import PocketBase, PocketBaseError, FileUpload
from pocketbase.models.dtos import RealtimeEvent
from dotenv import load_dotenv
from lib.ImageRender import ImageRender
from lib.Pocketbase.Connector import Connector

COLLECTION_NAME = "images"


# Strategy : Numpy save NPZ file 
class PocketbaseImageStore:   # (ImageStore)
    def __init__(self, connector: Connector):
        self.connector = connector 
    
    # ouput is the image data array
    async def store(self, output, dims, mask, title, stats):
        pb = await self.connector.connect()
        # Get the collection instance we can work with
        collection = pb.collection(COLLECTION_NAME)

        # encode data in NPZ format for compat with direct-file method
        npz = io.BytesIO()
        np.savez(npz, output0=output)

        ren = ImageRender()
        img = io.BytesIO()
        ren.render(output, dims, mask, img)

        # Upload a file
        # Add a new record.
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
                "mask": mask,
                "data": FileUpload((f"{title}.npz", npz )),
                "image": FileUpload((f"{title}.png", img )),
            }
        )

    # once-off - set up the database structure
    async def setup(self):
        pb = await self.connector.connect()

        # TODO first remove an existing collection
        #collection = pb.collection("images")
        #await pb.collections.delete(collection["id"])

        # Create a collection to s"tore records in
        # It is a base collection (not "view" or "auth") with one column "content"
        # and it will have the regular "id" column.
        try:
            await pb.collections.create(
                {
                    "name": COLLECTION_NAME,
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
                            "name": "mask",
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


