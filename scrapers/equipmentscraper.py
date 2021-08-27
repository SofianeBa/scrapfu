from .scraper import Scraper
import time
from helpers import db
from psycopg2.extras import NumericRange
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
        self.keywords = {
            'AP Parry': 'ap_parry','AP Reduction': 'ap_reduction',"MP Parry": 'mp_parry',
            "MP Reduction": 'mp_reduction','Air Damage': 'air_damage','Water Damage': 'water_damage',
            'Fire Damage': 'fire_damage', "Earth Damage": 'earth_damage',"Neutral Damage": 'neutral_damage',
            "Trap Damage": 'trap_damage',"Pushback Damage": 'pushback_damage',"Critical Damage": 'critical_damage',
            "Damage Reflected": 'damage_reflected',"Critical Resistance": 'critical_res',"Pushback Resistance": 'pushback_res', 
            "% Neutral Resistance": 'percent_neutral_res',"% Critical": 'percent_critical',"% Melee Resistance": 'percent_melee_res',
            "% Earth Resistance": 'percent_earth_res',"% Fire resistance": 'percent_fire_res',"% Air Resistance": 'percent_air_res',
            "% Water Resistance": 'percent_water_res',"% Ranged Resistance": 'percent_ranged_res',"% Ranged Damage": 'percent_ranged_damage', 
            "% Spell Damage": 'percent_spell_damage',"% Weapon Damage": 'percent_weapon_damage',
            "% Melee Damage": 'percent_melee_damage',"Strength": 'strength', 'Intelligence': 'intelligence','Chance': 'chance','Agility': 'agility',"Wisdom": 'wisdom',
            'Vitality': 'vitality',"Pods": 'pods',"Damage": 'damage',"Dodge": 'dodge',"Heals": 'heals',"Initiative": 'initiative', 
            "Lock": 'lock', "MP": 'mp','AP': 'ap','Prospecting': 'prospecting',"Summons": 'summons',"Range": 'range' }
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

    def reverse_min_max_values(self, min, max):
        new_min = max
        new_max = min
        return (new_min, new_max)

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
            if begin > end:
                begin, end = self.reverse_min_max_values(begin, end)
        else:
            begin = ''.join(re.findall('[-,0-9]',rangeText[0]))
            begin_is_int = isinstance(begin, int)
            if begin_is_int == False:
                begin = 1
            end = begin
        return (begin, end)

    def scrape_effect_fields(self, effect_fields):
        scraped_fields = {}
        expression = '$|'.join(keyword for keyword in self.keywords.keys())
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
                ingredient_id_tag = ingredient_row.find('a')
                ingredient_id = self.get_id(ingredient_id_tag['href'])
                is_equipment_id = self.session.query(exists().where(Equipment.id == ingredient_id)).scalar()
                if not is_equipment_id:
                    ingredient = Ingredient(resource_id=ingredient_id, quantity=amount)
                else:
                    ingredient = Ingredient(equipment_id=ingredient_id, quantity=amount)
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
                            setattr(equipment, self.keywords[keyword],NumericRange(lower=min_value, upper=max_value, bounds='[]', empty=False))
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