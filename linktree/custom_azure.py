from storages.backends.azure_storage import AzureStorage
from dotenv import load_dotenv
import os
load_dotenv()

AZURE_ACCOUNT_NAME = os.getenv("AZURE_ACCOUNT_NAME")
AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")


class AzureMediaStorage(AzureStorage):
    account_name = AZURE_ACCOUNT_NAME
    account_key = AZURE_ACCOUNT_KEY
    azure_container = 'media'
    expiration_secs = None


class AzureStaticStorage(AzureStorage):
    account_name = AZURE_ACCOUNT_NAME
    account_key = AZURE_ACCOUNT_KEY
    azure_container = 'static'
    expiration_secs = None
