from .scraper import Scraper
import time
from helpers import db
import re
from bs4 import BeautifulSoup
from models.equipment import Equipment
from models.recipe import Recipe
from models.ingredient import Ingredient
from models.profession import Profession
from sqlalchemy import select


class Equipmentscraper(Scraper):
    def __init__(self,blob_service_client, driver, options, queue):
        super().__init__(blob_service_client=blob_service_client, driver=driver, options=options, queue=queue)
        self.keywords = ['AP', 'AP Parry', 'AP Reduction', 'Agility', 'Air Damage',
        "% Air Resistance", 'Chance', 'Water Damage', "% Water Resistance", 'Prospecting',
        'Intelligence','Fire Damage', "% Fire resistance", "Strength", "Earth Damage",
        "% Earth Resistance", "Pods", "Wisdom", "Neutral Damage", "% Neutral Resistance", 
        "Damage", "Damage Reflected", "Critical Damage", "Critical Resistance", "% Critical",
        "Pushback Damage", "Pushback Resistance", "Dodge", "Heals", "Initiative", "Lock", "MP",
        "MP Parry", "MP Reduction", "% Melee Damage", "% Melee Resistance", "% Ranged Damage", 
        "% Ranged Resistance", "% Spell Damage", "% Weapon Damage", "Summons", "Trap Damage", "Range", "Vitality"]
        self.found_keywords = []
        self.equipment = Equipment()
        self.Session = db.create_session()
        self.session = self.Session()
        self.recipe = Recipe()

    def find_effect_fields(self, soup):
        titles = soup.findAll('div', {'class': 'ak-panel-title'})
        for title in titles:
            if str.strip(title.text) == 'Effects':
                effects_parent = title.parent
                effects_list = effects_parent.findAll('div',{'class':'ak-title'})
                return effects_list

    def get_min_max_values(self, effect_field):
        rangeText = str.split(effect_field, sep='to')
        if len(rangeText) > 1:
            begin = ''.join(re.findall('[-,0-9]',rangeText[0]))
            end = ''.join(re.findall('[-,0-9]',rangeText[1]))
            try:
                begin = int(str.strip(begin))
            except:
                begin = end
            try:
                end = int(str.strip(end))
            except:
                end = begin
        else:
            begin = ''.join(re.findall('[-,0-9]',rangeText[0]))
            begin_is_int = isinstance(begin, int)
            if begin_is_int == False:
                begin = 1
            end = begin
        return (begin, end)

    def scrape_effect_fields(self, effect_fields):
        for effect_field in effect_fields:
            expression = '|'.join(keyword for keyword in self.keywords)
            match = re.search(expression, effect_field.text)
            if match:
                keyword = match.group(0)
                min_value, max_value = self.get_min_max_values(effect_field.text)
                if keyword =='AP':
                    self.equipment.min_ap = min_value
                    self.equipment.max_ap = max_value
                if keyword =='AP Parry':
                    self.equipment.min_ap_parry = min_value
                    self.equipment.max_ap_parry = max_value
                if keyword =='AP Reduction':
                    self.equipment.min_ap_reduction = min_value
                    self.equipment.max_ap_reduction = max_value
                if keyword =='Agility': 
                    self.equipment.min_agility = min_value
                    self.equipment.max_agility = max_value
                if keyword =='Air Damage':
                    self.equipment.min_air_damage = min_value
                    self.equipment.max_air_damage = max_value
                if keyword =='% Air Resistance':
                    self.equipment.min_percent_air_res = min_value
                    self.equipment.max_percent_air_res = max_value
                if keyword =='Chance':
                    self.equipment.min_chance = min_value
                    self.equipment.max_chance = max_value
                if keyword =='Water Damage':
                    self.equipment.min_water_damage = min_value
                    self.equipment.max_water_damage = max_value
                if keyword =='% Water Resistance':
                    self.equipment.min_percent_water_res = min_value
                    self.equipment.max_percent_water_res = max_value
                if keyword =='Prospecting':
                    self.equipment.min_prospecting = min_value
                    self.equipment.max_prospecting = max_value
                if keyword =='Intelligence':
                    self.equipment.min_intelligence = min_value
                    self.equipment.max_intelligence = max_value
                if keyword =='Fire Damage' :
                    self.equipment.min_fire_damage = min_value
                    self.equipment.max_fire_damage = max_value
                if keyword =='% Fire resistance':
                    self.equipment.min_percent_fire_res = min_value
                    self.equipment.max_percent_fire_res = max_value
                if keyword =='Strength' :
                    self.equipment.min_strength = min_value
                    self.equipment.max_strength = max_value
                if keyword =='Earth Damage':
                    self.equipment.min_earth_damage = min_value
                    self.equipment.max_earth_damage = max_value
                if keyword =='% Earth Resistance': 
                    self.equipment.min_percent_earth_res = min_value
                    self.equipment.max_percent_earth_res = max_value
                if keyword =='Pods' :
                    self.equipment.min_pods = min_value
                    self.equipment.max_pods = max_value
                if keyword =='Wisdom':
                    self.equipment.min_wisdom = min_value
                    self.equipment.max_wisdom = max_value
                if keyword =='Neutral Damage':
                    self.equipment.min_neutral_damage = min_value
                    self.equipment.max_neutral_damage = max_value
                if keyword =='% Neutral Resistance':
                    self.equipment.min_percent_neutral_res = min_value
                    self.equipment.max_percent_neutral_res = max_value
                if keyword =='Damage':
                    self.equipment.min_damage = min_value
                    self.equipment.max_damage = max_value
                if keyword =='Damage Reflected':
                    self.equipment.min_damage_reflected = min_value
                    self.equipment.max_damage_reflected = max_value
                if keyword =='Critical Damage':
                    self.equipment.min_critical_damage = min_value
                    self.equipment.max_critical_damage = max_value
                if keyword =='Critical Resistance':
                    self.equipment.min_critical_res = min_value
                    self.equipment.max_critical_res = max_value
                if keyword =='% Critical':
                    self.equipment.min_percent_critical = min_value
                    self.equipment.max_percent_critical = max_value
                if keyword =='Pushback Damage':
                    self.equipment.min_pushback_damage = min_value
                    self.equipment.max_pushback_damage = max_value
                if keyword =='Pushback Resistance':
                    self.equipment.min_pushback_res = min_value
                    self.equipment.max_pushback_res = max_value
                if keyword =='Dodge':
                    self.equipment.min_dodge = min_value
                    self.equipment.max_dodge = max_value
                if keyword =='Heals':
                    self.equipment.min_heals = min_value
                    self.equipment.max_heals = max_value
                if keyword =='Initiative':
                    self.equipment.min_initiative = min_value
                    self.equipment.max_initiative = max_value
                if keyword =='Lock' :
                    self.equipment.min_lock = min_value
                    self.equipment.max_lock = max_value
                if keyword =='MP':
                    self.equipment.min_mp = min_value
                    self.equipment.max_mp = max_value
                if keyword =='MP Parry':
                    self.equipment.min_mp_parry = min_value
                    self.equipment.max_mp_parry = max_value
                if keyword =='MP Reduction':
                    self.equipment.min_mp_reduction = min_value
                    self.equipment.max_mp_reduction = max_value
                if keyword =='% Melee Damage': 
                    self.equipment.min_percent_melee_damage = min_value
                    self.equipment.max_percent_melee_damage = max_value
                if keyword =='% Melee Resistance':
                    self.equipment.min_percent_melee_res = min_value
                    self.equipment.max_percent_melee_res = max_value
                if keyword =='% Ranged Damage' :
                    self.equipment.min_percent_ranged_damage = min_value
                    self.equipment.max_percent_ranged_damage = max_value
                if keyword =='% Ranged Resistance':
                    self.equipment.min_percent_ranged_res = min_value
                    self.equipment.max_percent_ranged_res = max_value
                if keyword =='% Spell Damage' :
                    self.equipment.min_percent_spell_damage = min_value
                    self.equipment.max_percent_spell_damage = max_value
                if keyword =='% Weapon Damage':
                    self.equipment.min_percent_weapon_damage = min_value
                    self.equipment.max_percent_weapon_damage = max_value
                if keyword =='Summons':
                    self.equipment.min_summons = min_value
                    self.equipment.max_summons = max_value
                if keyword =='Trap Damage': 
                    self.equipment.min_range = min_value
                    self.equipment.max_range = max_value
                if keyword =='Range':
                    self.equipment.min_range = min_value
                    self.equipment.max_range = max_value
                if keyword =='Vitality':
                    self.equipment.min_vitality = min_value
                    self.equipment.max_vitality = max_value

    def get_level(self, soup):
        level_tag = soup.find('div', {'class':'ak-encyclo-detail-level col-xs-6 text-right'})
        level_value = ''.join(re.findall('[0-9]', level_tag.text))
        return level_value
    
    def get_description(self, soup):
        titles = soup.findAll('div', {'class': 'ak-panel-title'})
        for title in titles:
            if str.strip(title.text) == 'Description':
                title_parent = title.parent
                description_value = title_parent.find('div', {'class':'ak-panel-content'})
                return str.strip(description_value.text)

    def get_type(self, soup):
        strong_tags = soup.findAll('strong')
        for strong_tag in strong_tags:
            if str.strip(strong_tag.text) == 'Type':
                parent = strong_tag.parent
                strong_value = parent.find('span')
                return strong_value.text

    def get_recipe(self, soup):
        recipe_section =  soup.find('div',{'class':'ak-container ak-panel ak-crafts'})
        profession_section = recipe_section.find('div', {'class':'ak-panel-intro'})
        profession_values = str.split(profession_section.text, 'Level')
        profession_level = str.strip(profession_values[1])
        profession_result = self.session.execute(select(Profession.id).where(Profession.name == str.strip(profession_values[0]))).one()
        ingredient_list = recipe_section.findAll('div', {'class': 'ak-list-element'})
        self.recipe.level = profession_level
        self.recipe.profession = profession_result.id
        for ingredient_row in ingredient_list:
            amount_tag = ingredient_row.find('div', {'class':'ak-front'})
            amount = ''.join(re.findall('[0-9]',amount_tag.text))
            resource_id_tag = ingredient_row.find('a')
            resource_id = self.get_id(resource_id_tag['href'])
            ingredient = Ingredient(resource_id=resource_id, quantity=amount)
            self.recipe.ingredients.append(ingredient)
        self.equipment.recipe = self.recipe
        

    def get_equipment_info(self, url):
        time.sleep(5)
        driver = self.dr.create_driver(self.options)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        if soup.find('div', {'class': 'ak-404'}) == None:
            try:
                self.equipment.id = self.get_id(url)
                self.equipment.type = self.get_type(soup)
                self.equipment.level = self.get_level(soup)
                self.equipment.name =  self.get_name(soup)
                self.equipment.description = self.get_description(soup)
                equipment_image_link = self.get_image_link(soup)
                effect_fields = self.find_effect_fields(soup)
                self.scrape_effect_fields(effect_fields)
                self.get_recipe(soup)
                self.save_image(equipment_image_link, self.equipment.name)
                driver.quit()
                return self.equipment
            except Exception as e: 
                driver.quit()
                print(e)
        else:
            driver.quit()