from sqlalchemy.types import Integer, String
from sqlalchemy import Column
from sqlalchemy.orm import relationship
from models.base import Base

# Weapon model class - gathers id, type,level, etc. Gathers all the basic stats for each weapon. Does not currently gather incarnations and other special effects.
class Weapon(Base):
    __tablename__ = 'weapon'
    #identification
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=False)
    type = Column(String, nullable = False)
    level = Column(Integer, nullable = False)
    name = Column(String, nullable = False)
    description = Column(String, nullable = True)
    #characteristics
    ap_cost = Column(Integer, nullable=False)
    min_effective_range = Column(Integer, nullable=False)
    max_effective_range = Column(Integer, nullable = False)
    crit_hit_chance = Column(Integer, nullable = False)
    #Core Effects
    min_percent_air_res= Column(Integer, nullable = True)
    max_percent_air_res= Column(Integer, nullable = True)
    min_percent_earth_res= Column(Integer, nullable = True)
    max_percent_earth_res= Column(Integer, nullable = True)
    min_percent_fire_res= Column(Integer, nullable = True)
    max_percent_fire_res= Column(Integer, nullable = True)   
    min_percent_neutral_res= Column(Integer, nullable = True)
    max_percent_neutral_res= Column(Integer, nullable = True)
    min_percent_water_res= Column(Integer, nullable = True)
    max_percent_water_res= Column(Integer, nullable = True)
    min_percent_ranged_res= Column(Integer, nullable = True)
    max_percent_ranged_res= Column(Integer, nullable= True)
    min_percent_weapon_damage= Column(Integer, nullable = True)
    max_percent_weapon_damage= Column(Integer, nullable = True)
    min_percent_ranged_damage= Column(Integer, nullable = True)
    max_percent_ranged_damage= Column(Integer, nullable = True)
    min_percent_spell_damage= Column(Integer, nullable = True)
    max_percent_spell_damage= Column(Integer, nullable = True)
    min_percent_crit= Column(Integer, nullable = True)
    max_percent_crit= Column(Integer, nullable = True)
    min_crit_damage= Column(Integer, nullable = True)
    max_crit_damage= Column(Integer, nullable = True)
    min_crit_res= Column(Integer, nullable = True)
    max_crit_res= Column(Integer, nullable = True)
    min_vitality= Column(Integer, nullable = True)
    max_vitality= Column(Integer, nullable = True)
    min_agility= Column(Integer, nullable = True)
    max_agility= Column(Integer, nullable = True)
    min_air_damage= Column(Integer, nullable = True)
    max_air_damage= Column(Integer, nullable = True)
    min_air_steal= Column(Integer, nullable = True)
    max_air_steal= Column(Integer, nullable = True)
    min_air_res= Column(Integer, nullable = True)
    max_air_res= Column(Integer, nullable = True)
    min_strength= Column(Integer, nullable = True)
    max_strength= Column(Integer, nullable = True)
    min_earth_damage= Column(Integer, nullable = True)
    max_earth_damage= Column(Integer, nullable = True)
    min_earth_steal= Column(Integer, nullable = True)
    max_earth_steal= Column(Integer, nullable = True)
    min_earth_Res= Column(Integer, nullable = True)
    max_earth_Res= Column(Integer, nullable = True)
    min_intelligence= Column(Integer, nullable = True)
    max_intelligence= Column(Integer, nullable = True)
    min_fire_damage= Column(Integer, nullable = True)
    max_fire_damage= Column(Integer, nullable = True)
    min_fire_steal= Column(Integer, nullable = True)
    max_fire_steal= Column(Integer, nullable = True)
    min_fire_res= Column(Integer, nullable = True)
    max_fire_res= Column(Integer, nullable = True)
    min_wisdom= Column(Integer, nullable = True)
    max_wisdom= Column(Integer, nullable = True)
    min_neutral_damage= Column(Integer, nullable = True)
    max_neutral_damage= Column(Integer, nullable = True)
    min_neutral_steal= Column(Integer, nullable = True)
    max_neutral_steal= Column(Integer, nullable = True)
    min_neutral_res= Column(Integer, nullable = True)
    max_neutral_res= Column(Integer, nullable = True)
    min_chance= Column(Integer, nullable = True)
    max_chance= Column(Integer, nullable = True)
    min_water_damage= Column(Integer, nullable = True)
    max_water_damage= Column(Integer, nullable = True)
    min_water_steal= Column(Integer, nullable = True)
    max_water_steal= Column(Integer, nullable = True)
    min_water_Res= Column(Integer, nullable = True)
    max_water_Res= Column(Integer, nullable = True)
    min_damage= Column(Integer, nullable = True)
    max_damage= Column(Integer, nullable = True)
    min_ap= Column(Integer, nullable = True)
    max_ap= Column(Integer, nullable = True)
    min_ap_parry= Column(Integer, nullable = True)
    max_ap_parry= Column(Integer, nullable = True)
    min_ap_reduction= Column(Integer, nullable = True)
    max_ap_reduction= Column(Integer, nullable = True)
    min_mp= Column(Integer, nullable = True)
    max_mp= Column(Integer, nullable = True)
    min_mp_parry= Column(Integer, nullable = True)
    max_mp_parry= Column(Integer, nullable = True)
    min_mp_reduction= Column(Integer, nullable = True)
    max_mp_reduction= Column(Integer, nullable = True)
    min_dodge= Column(Integer, nullable = True)
    max_dodge= Column(Integer, nullable = True)
    min_heals= Column(Integer, nullable = True)
    max_heals= Column(Integer, nullable = True)
    min_initiative= Column(Integer, nullable = True)
    max_initiative= Column(Integer, nullable = True)
    min_lock= Column(Integer, nullable = True)
    max_lock= Column(Integer, nullable = True)
    min_range= Column(Integer, nullable = True)
    max_range= Column(Integer, nullable = True)
    min_prospecting= Column(Integer, nullable = True)
    max_prospecting= Column(Integer, nullable = True)
    min_pushback_damage= Column(Integer, nullable = True)
    max_pushback_damage= Column(Integer, nullable = True)
    min_pushback_res= Column(Integer, nullable = True)
    max_pushback_res= Column(Integer, nullable = True)
    min_power = Column(Integer, nullable = True)
    max_power = Column(Integer, nullable = True)
    min_trap_power= Column(Integer, nullable = True)
    max_trap_power= Column(Integer, nullable = True)
    min_trap_damage= Column(Integer, nullable = True)
    max_trap_damage= Column(Integer, nullable = True)
    min_steals_kamas= Column(Integer, nullable = True)
    max_steals_kamas= Column(Integer, nullable = True)
    #Relationships
    recipe = relationship('Recipe', back_populates='weapon', uselist=False)