import os
from pocketbase import PocketBase, PocketBaseError
from dotenv import load_dotenv


load_dotenv()
CONNECTION_URL = os.getenv('POCKETBASE_CONNECTION_URL')
SUPERUSER_EMAIL = os.getenv('POCKETBASE_SUPERUSER_EMAIL')
SUPERUSER_PASSWORD = os.getenv('POCKETBASE_SUPERUSER_PASSWORD')


# Connects to Pocketbase and Authenticates, from the ENV VARS
class Connector:
    #def __init(self):

    async def connect(self):
        print (f"Connecting to Pocketbase on {CONNECTION_URL}...")
        # Instantiate the PocketBase connector
        pb = PocketBase(CONNECTION_URL)
        # Authenticate as a superuser
        print (f"Authenticating to Pocketbase as {SUPERUSER_EMAIL}...")
        await pb.collection("_superusers").auth.with_password(SUPERUSER_EMAIL, SUPERUSER_PASSWORD)
        return pb

