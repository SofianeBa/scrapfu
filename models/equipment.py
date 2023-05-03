from models.ingredient import Ingredient
from sqlalchemy.dialects.postgresql import INT4RANGE
from .monsterequipment import MonsterEquipment
from models.base import Base
from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Integer, Text

#Equiment model class - gathers identification, effects, and associates to crafting recipe
class Equipment(Base):
    __tablename__ = 'equipment'
    #identification
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=False)
    type = Column(String, nullable = False)
    level = Column(Integer, nullable = False)
    name = Column(String, nullable = False)
    rarity = Column(String, nullable = False)
    image = Column(String, nullable = False)

    description = Column(Text, nullable = True)

    pv = Column(INT4RANGE, nullable=True)
    pa = Column(INT4RANGE, nullable = True)
    pm = Column(INT4RANGE, nullable = True)
    pw = Column(INT4RANGE, nullable = True)
    po = Column(INT4RANGE, nullable = True)
    armure_recu = Column(INT4RANGE, nullable = True)
    armure_donne = Column(INT4RANGE, nullable = True)
    maitrise_eau = Column(INT4RANGE, nullable=True)
    maitrise_air = Column(INT4RANGE, nullable=True)
    maitrise_feu = Column(INT4RANGE, nullable=True)
    maitrise_terre = Column(INT4RANGE, nullable=True)
    resistance_eau = Column(INT4RANGE, nullable=True)
    resistance_air = Column(INT4RANGE, nullable=True)
    resistance_feu = Column(INT4RANGE, nullable=True)
    resistance_terre = Column(INT4RANGE, nullable=True)
    pourcent_critique = Column(INT4RANGE, nullable = True)
    pourcent_parade = Column(INT4RANGE, nullable = True)
    initiative = Column(INT4RANGE, nullable = True)
    esquive = Column(INT4RANGE, nullable = True)
    tacle = Column(INT4RANGE, nullable = True)
    sagesse = Column(INT4RANGE, nullable = True)
    prospection = Column(INT4RANGE, nullable = True)
    controle = Column(INT4RANGE, nullable = True)
    volonte = Column(INT4RANGE, nullable = True)
    maitrise_critique = Column(INT4RANGE, nullable = True)
    resistance_critique = Column(INT4RANGE, nullable = True)
    maitrise_dos = Column(INT4RANGE, nullable = True)
    resistance_dos = Column(INT4RANGE, nullable = True)
    maitrise_melee = Column(INT4RANGE, nullable = True)
    maitrise_distance = Column(INT4RANGE, nullable = True)
    maitrise_monocible = Column(INT4RANGE, nullable = True)
    maitrise_zone = Column(INT4RANGE, nullable = True)
    maitrise_soin = Column(INT4RANGE, nullable = True)
    maitrise_berserk = Column(INT4RANGE, nullable = True)
    maitrise_elem = Column(INT4RANGE, nullable=True)
    maitrise_elem_1= Column(INT4RANGE, nullable=True)
    maitrise_elem_2= Column(INT4RANGE, nullable=True)
    maitrise_elem_3= Column(INT4RANGE, nullable=True)
    resistance_elem = Column(INT4RANGE, nullable=True)
    resistance_elem_1= Column(INT4RANGE, nullable=True)
    resistance_elem_2= Column(INT4RANGE, nullable=True)
    resistance_elem_3= Column(INT4RANGE, nullable=True)
    niv_sort_elem = Column(INT4RANGE, nullable=True)
    niv_sort_air = Column(INT4RANGE, nullable=True)
    niv_sort_terre = Column(INT4RANGE, nullable=True)
    niv_sort_eau = Column(INT4RANGE, nullable=True)
    niv_sort_feu = Column(INT4RANGE, nullable=True)
    quantite_recolte_paysan = Column(INT4RANGE, nullable=True)
    quantite_recolte_forestier = Column(INT4RANGE, nullable=True)
    quantite_recolte_herboriste = Column(INT4RANGE, nullable=True)
    quantite_recolte_mineur = Column(INT4RANGE, nullable=True)
    quantite_recolte_trappeur = Column(INT4RANGE, nullable=True)
    quantite_recolte_pecheur = Column(INT4RANGE, nullable=True)

    #relationships
    recipe = relationship('Recipe', back_populates='equipment', uselist=False)
    ingredients = relationship('Ingredient', back_populates='equipment')
    monsters = relationship("MonsterEquipment", back_populates="equipment")