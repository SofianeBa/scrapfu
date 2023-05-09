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

    pv = Column(Integer, nullable=True)
    pa = Column(Integer, nullable = True)
    pm = Column(Integer, nullable = True)
    pw = Column(Integer, nullable = True)
    po = Column(Integer, nullable = True)
    armure_recu = Column(Integer, nullable = True)
    armure_donne = Column(Integer, nullable = True)
    maitrise_eau = Column(Integer, nullable=True)
    maitrise_air = Column(Integer, nullable=True)
    maitrise_feu = Column(Integer, nullable=True)
    maitrise_terre = Column(Integer, nullable=True)
    resistance_eau = Column(Integer, nullable=True)
    resistance_air = Column(Integer, nullable=True)
    resistance_feu = Column(Integer, nullable=True)
    resistance_terre = Column(Integer, nullable=True)
    pourcent_critique = Column(Integer, nullable = True)
    pourcent_parade = Column(Integer, nullable = True)
    initiative = Column(Integer, nullable = True)
    esquive = Column(Integer, nullable = True)
    tacle = Column(Integer, nullable = True)
    sagesse = Column(Integer, nullable = True)
    prospection = Column(Integer, nullable = True)
    controle = Column(Integer, nullable = True)
    volonte = Column(Integer, nullable = True)
    maitrise_critique = Column(Integer, nullable = True)
    resistance_critique = Column(Integer, nullable = True)
    maitrise_dos = Column(Integer, nullable = True)
    resistance_dos = Column(Integer, nullable = True)
    maitrise_melee = Column(Integer, nullable = True)
    maitrise_distance = Column(Integer, nullable = True)
    maitrise_monocible = Column(Integer, nullable = True)
    maitrise_zone = Column(Integer, nullable = True)
    maitrise_soin = Column(Integer, nullable = True)
    maitrise_berserk = Column(Integer, nullable = True)
    maitrise_elem = Column(Integer, nullable=True)
    maitrise_elem_1= Column(Integer, nullable=True)
    maitrise_elem_2= Column(Integer, nullable=True)
    maitrise_elem_3= Column(Integer, nullable=True)
    resistance_elem = Column(Integer, nullable=True)
    resistance_elem_1= Column(Integer, nullable=True)
    resistance_elem_2= Column(Integer, nullable=True)
    resistance_elem_3= Column(Integer, nullable=True)
    niv_sort_elem = Column(Integer, nullable=True)
    niv_sort_air = Column(Integer, nullable=True)
    niv_sort_terre = Column(Integer, nullable=True)
    niv_sort_eau = Column(Integer, nullable=True)
    niv_sort_feu = Column(Integer, nullable=True)
    quantite_recolte_paysan = Column(Integer, nullable=True)
    quantite_recolte_forestier = Column(Integer, nullable=True)
    quantite_recolte_herboriste = Column(Integer, nullable=True)
    quantite_recolte_mineur = Column(Integer, nullable=True)
    quantite_recolte_trappeur = Column(Integer, nullable=True)
    quantite_recolte_pecheur = Column(Integer, nullable=True)

    #relationships
    recipes = relationship("Recipe", back_populates="equipment")
    ingredients = relationship("Ingredient", back_populates="equipment")
    monsters = relationship("Monster", secondary="monster_equipment", back_populates="equipments")