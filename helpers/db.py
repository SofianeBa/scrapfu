import os
from sqlalchemy import create_engine
from azure.identity import VisualStudioCodeCredential
from azure.keyvault.secrets import SecretClient


def get_conenction_string():
    try:
        kvName = os.getenv('KV_NAME')
    except OSError:
        print('Error: Please check if the KV_NAME environment variable is present')
    KVUri = f"https://{kvName}.vault.azure.net"
    credentials = VisualStudioCodeCredential(tenant_id="ef604d5f-e334-4691-b1b7-cbcd4104aa23")
    client = SecretClient(vault_url=KVUri, credential=credentials)
    secret = client.get_secret('dbConnectionString')
    return secret

def create_db_engine(dbstring):
    engine = create_engine(dbstring, future=True)
    return engine
