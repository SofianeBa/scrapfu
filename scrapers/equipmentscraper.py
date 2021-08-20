from .scraper import Scraper
import time
from helpers import db
import re
from sqlalchemy import exists
from bs4 import BeautifulSoup
from models.equipment import Equipment
from models.recipe import Recipe
from models.ingredient import Ingredient
from models.profession import Profession
from sqlalchemy import select


class Equipmentscraper(Scraper):
    def __init__(self,blob_service_client, driver, options, queue):
        super().__init__(blob_service_client=blob_service_client, driver=driver, options=options, queue=queue)
        self.keywords = ['AP Parry','AP Reduction',"MP Parry", "MP Reduction",
        'Air Damage','Water Damage','Fire Damage', "Earth Damage","Neutral Damage",
        "Trap Damage","Pushback Damage","Critical Damage","Damage Reflected","Critical Resistance","Pushback Resistance", 
        "% Neutral Resistance","% Critical","% Melee Resistance","% Earth Resistance","% Fire resistance","% Air Resistance",
        "% Water Resistance","% Ranged Resistance","% Ranged Damage", "% Spell Damage","% Weapon Damage","% Melee Damage",
        "Strength", 'Intelligence','Chance','Agility',"Wisdom","Vitality""Pods","Damage","Dodge","Heals","Initiative", 
        "Lock", "MP",'AP','Prospecting',"Summons","Range" ]
        self.found_keywords = []
        self.Session = db.create_session()
        self.session = self.Session()

    def find_effect_fields(self, soup):
        try:
            titles = soup.findAll('div', {'class': 'ak-panel-title'})
            for title in titles:
                if str.strip(title.text) == 'Effects':
                    effects_parent = title.parent
                    effects_list = effects_parent.findAll('div',{'class':'ak-title'})
                    return effects_list
        except Exception as e:
            print(e)
            return None

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
        scraped_fields = {}
        expression = '$|'.join(keyword for keyword in self.keywords)
        for effect_field in effect_fields:
            match = re.search(expression, str.strip(effect_field.text))
            if match:
                keyword = match.group(0)
                min_value, max_value = self.get_min_max_values(effect_field.text)
                scraped_fields[keyword] = (min_value,max_value)
        return scraped_fields


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

    def get_recipe(self, soup, recipe):
        recipe_section =  soup.find('div',{'class':'ak-container ak-panel ak-crafts'})
        if recipe_section:
            profession_section = recipe_section.find('div', {'class':'ak-panel-intro'})
            profession_values = str.split(profession_section.text, 'Level')
            profession_level = str.strip(profession_values[1])
            profession_result = self.session.execute(select(Profession.id).where(Profession.name == str.strip(profession_values[0]))).one()
            ingredient_list = recipe_section.findAll('div', {'class': 'ak-list-element'})
            recipe.level = profession_level
            recipe.profession = profession_result.id
            for ingredient_row in ingredient_list:
                amount_tag = ingredient_row.find('div', {'class':'ak-front'})
                amount = ''.join(re.findall('[0-9]',amount_tag.text))
                resource_id_tag = ingredient_row.find('a')
                resource_id = self.get_id(resource_id_tag['href'])
                ingredient = Ingredient(resource_id=resource_id, quantity=amount)
                recipe.ingredients.append(ingredient)
            return recipe
        else:
            return None
        

    def get_equipment_info(self, url):
        id = self.get_id(url)
        equipment_exists = self.session.query(exists().where(Equipment.id == id)).scalar()
        if not equipment_exists:
            equipment = Equipment()
            recipe = Recipe()
            time.sleep(5)
            driver = self.dr.create_driver(self.options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            if soup.find('div', {'class': 'ak-404'}) == None:
                try:
                    equipment.id = id
                    equipment.type = self.get_type(soup)
                    equipment.level = self.get_level(soup)
                    equipment.name =  self.get_name(soup)
                    equipment.description = self.get_description(soup)
                    equipment_image_link = self.get_image_link(soup)
                    effect_fields = self.find_effect_fields(soup)
                    if effect_fields:
                        scraped_fields = self.scrape_effect_fields(effect_fields)
                        keywords = scraped_fields.keys()
                        for keyword in keywords:
                            min_value, max_value = scraped_fields[keyword] 
                            if keyword =='AP':
                                equipment.min_ap = min_value
                                equipment.max_ap = max_value
                            if keyword =='AP Parry':
                                equipment.min_ap_parry = min_value
                                equipment.max_ap_parry = max_value
                            if keyword =='AP Reduction':
                                equipment.min_ap_reduction = min_value
                                equipment.max_ap_reduction = max_value
                            if keyword =='Agility': 
                                equipment.min_agility = min_value
                                equipment.max_agility = max_value
                            if keyword =='Air Damage':
                                equipment.min_air_damage = min_value
                                equipment.max_air_damage = max_value
                            if keyword =='% Air Resistance':
                                equipment.min_percent_air_res = min_value
                                equipment.max_percent_air_res = max_value
                            if keyword =='Chance':
                                equipment.min_chance = min_value
                                equipment.max_chance = max_value
                            if keyword =='Water Damage':
                                equipment.min_water_damage = min_value
                                equipment.max_water_damage = max_value
                            if keyword =='% Water Resistance':
                                equipment.min_percent_water_res = min_value
                                equipment.max_percent_water_res = max_value
                            if keyword =='Prospecting':
                                equipment.min_prospecting = min_value
                                equipment.max_prospecting = max_value
                            if keyword =='Intelligence':
                                equipment.min_intelligence = min_value
                                equipment.max_intelligence = max_value
                            if keyword =='Fire Damage' :
                                equipment.min_fire_damage = min_value
                                equipment.max_fire_damage = max_value
                            if keyword =='% Fire resistance':
                                equipment.min_percent_fire_res = min_value
                                equipment.max_percent_fire_res = max_value
                            if keyword =='Strength' :
                                equipment.min_strength = min_value
                                equipment.max_strength = max_value
                            if keyword =='Earth Damage':
                                equipment.min_earth_damage = min_value
                                equipment.max_earth_damage = max_value
                            if keyword =='% Earth Resistance': 
                                equipment.min_percent_earth_res = min_value
                                equipment.max_percent_earth_res = max_value
                            if keyword =='Pods' :
                                equipment.min_pods = min_value
                                equipment.max_pods = max_value
                            if keyword =='Wisdom':
                                equipment.min_wisdom = min_value
                                equipment.max_wisdom = max_value
                            if keyword =='Neutral Damage':
                                equipment.min_neutral_damage = min_value
                                equipment.max_neutral_damage = max_value
                            if keyword =='% Neutral Resistance':
                                equipment.min_percent_neutral_res = min_value
                                equipment.max_percent_neutral_res = max_value
                            if keyword =='Damage':
                                equipment.min_damage = min_value
                                equipment.max_damage = max_value
                            if keyword =='Damage Reflected':
                                equipment.min_damage_reflected = min_value
                                equipment.max_damage_reflected = max_value
                            if keyword =='Critical Damage':
                                equipment.min_critical_damage = min_value
                                equipment.max_critical_damage = max_value
                            if keyword =='Critical Resistance':
                                equipment.min_critical_res = min_value
                                equipment.max_critical_res = max_value
                            if keyword =='% Critical':
                                equipment.min_percent_critical = min_value
                                equipment.max_percent_critical = max_value
                            if keyword =='Pushback Damage':
                                equipment.min_pushback_damage = min_value
                                equipment.max_pushback_damage = max_value
                            if keyword =='Pushback Resistance':
                                equipment.min_pushback_res = min_value
                                equipment.max_pushback_res = max_value
                            if keyword =='Dodge':
                                equipment.min_dodge = min_value
                                equipment.max_dodge = max_value
                            if keyword =='Heals':
                                equipment.min_heals = min_value
                                equipment.max_heals = max_value
                            if keyword =='Initiative':
                                equipment.min_initiative = min_value
                                equipment.max_initiative = max_value
                            if keyword =='Lock' :
                                equipment.min_lock = min_value
                                equipment.max_lock = max_value
                            if keyword =='MP':
                                equipment.min_mp = min_value
                                equipment.max_mp = max_value
                            if keyword =='MP Parry':
                                equipment.min_mp_parry = min_value
                                equipment.max_mp_parry = max_value
                            if keyword =='MP Reduction':
                                equipment.min_mp_reduction = min_value
                                equipment.max_mp_reduction = max_value
                            if keyword =='% Melee Damage': 
                                equipment.min_percent_melee_damage = min_value
                                equipment.max_percent_melee_damage = max_value
                            if keyword =='% Melee Resistance':
                                equipment.min_percent_melee_res = min_value
                                equipment.max_percent_melee_res = max_value
                            if keyword =='% Ranged Damage' :
                                equipment.min_percent_ranged_damage = min_value
                                equipment.max_percent_ranged_damage = max_value
                            if keyword =='% Ranged Resistance':
                                equipment.min_percent_ranged_res = min_value
                                equipment.max_percent_ranged_res = max_value
                            if keyword =='% Spell Damage' :
                                equipment.min_percent_spell_damage = min_value
                                equipment.max_percent_spell_damage = max_value
                            if keyword =='% Weapon Damage':
                                equipment.min_percent_weapon_damage = min_value
                                equipment.max_percent_weapon_damage = max_value
                            if keyword =='Summons':
                                equipment.min_summons = min_value
                                equipment.max_summons = max_value
                            if keyword =='Trap Damage': 
                                equipment.min_range = min_value
                                equipment.max_range = max_value
                            if keyword =='Range':
                                equipment.min_range = min_value
                                equipment.max_range = max_value
                            if keyword =='Vitality':
                                equipment.min_vitality = min_value
                                equipment.max_vitality = max_value
                                
                    recipe = self.get_recipe(soup, recipe)
                    if recipe:
                        equipment.recipe = recipe
                    self.save_image(equipment_image_link, equipment.name)
                    driver.quit()
                    return equipment
                except Exception as e: 
                    driver.quit()
                    self.failed_urls[url] = e
                    return None
            else:
                driver.quit()
                self.skipped_urls[url] = 'skipped url due to 404'
                return None
        else:
            self.skipped_urls[url] = 'Already present in db. Skipping'