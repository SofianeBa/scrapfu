import os
from sqlalchemy import create_engine
from azure.identity import VisualStudioCodeCredential
from azure.keyvault.secrets import SecretClient
import settings as config
from sqlalchemy.orm import sessionmaker, scoped_session

def get_conenction_string():
    KVUri = f"https://{config.kvName}.vault.azure.net"
    credentials = VisualStudioCodeCredential(tenant_id="ef604d5f-e334-4691-b1b7-cbcd4104aa23")
    client = SecretClient(vault_url=KVUri, credential=credentials)
    secret = client.get_secret('dbConnectionString')
    return secret

def create_db_engine(dbstring):
    engine = create_engine(dbstring, future=True)
    return engine

def create_session():
    dbsecret = get_conenction_string()
    engine = create_db_engine(dbsecret.value)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    return Session