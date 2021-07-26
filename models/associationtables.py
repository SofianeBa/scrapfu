from sqlalchemy import Table
from sqlalchemy.sql.schema import Column, ForeignKey
from .base import Base

monster_resource_table = Table('association', Base.metadata,
    Column('monster_id', ForeignKey('monster.id'), primary_key=True),
    Column('resource_id', ForeignKey('resource.id'), primary_key=True)
)