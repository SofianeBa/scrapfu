import os
from sqlalchemy import create_engine
#from azure.identity import VisualStudioCodeCredential
#from azure.keyvault.secrets import SecretClient
#import settings as config
from sqlalchemy.orm import sessionmaker, scoped_session


CONNSTR = f'postgresql://postgres:sudo@localhost:5432/scrapfu'


#def get_connection_string():
    #KVUri = f"https://{config.kvName}.vault.azure.net"
    #credentials = VisualStudioCodeCredential(tenant_id="ef604d5f-e334-4691-b1b7-cbcd4104aa23")
    #client = SecretClient(vault_url=KVUri, credential=credentials)
    #secret = client.get_secret('dbConnectionString')
    #return secret

def create_db_engine():
    engine = create_engine(CONNSTR, future=True)
    return engine

def create_session():
    #dbsecret = get_connection_string()
    #engine = create_db_engine(dbsecret.value)
    engine = create_engine(CONNSTR)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    return Session


