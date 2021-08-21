from decimal import DivisionByZero
from sqlalchemy.sql.sqltypes import Numeric
from .scraper import Scraper
import time
import re
from models.profession import Profession
from models.ingredient import Ingredient
from models.weapon import Weapon
from models.recipe import Recipe
from bs4 import BeautifulSoup
from sqlalchemy import select
from helpers import db
from math import floor
from sqlalchemy import exists

class Weaponscraper(Scraper):
    def __init__(self,blob_service_client, driver, options, queue):
        super().__init__(blob_service_client=blob_service_client, driver=driver, options=options, queue=queue)
        self.keywords = ['% Air Resistance','% Earth Resistance','% Fire Resistance','% Neutral Resistance','% Water Resistance','% Ranged Resistance','% Weapon Damage',
        '% Ranged Damage','% Spell Damage','% Critical','Critical Damage','Critical Resistance','Vitality',
        'Agility','Air Damage','Air Steal','Air Resistance','Strength','Earth Damage','Earth Steal','Earth Resistance','Intelligence','Fire Damage',
        'Fire Steal','Fire Resistance','Wisdom','Neutral Damage','Neutral Steal','Neutral Resistance','Chance','Water Damage','Water Steal',
        'Water Resistance','Damage','AP','AP Parry','AP Reduction','Hunting Weapon','Summons','MP','MP Parry','MP Reduction','Dodge','Heals',
        'Initiative','Lock','Range','Prospecting','Pushaback Damage','Pushback Resistance','Power','Power (traps)','Trap Damage','kamas',
        '(Neutral damage)','(Fire damage)','(Water damage)','(Earth damage)','(Air damage)','(Neutral steal)','(Fire steal)','(Water steal)',
        '(Earth steal)','(Air steal)','(HP restored)']
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
                ingredient_id_tag = ingredient_row.find('a')
                ingredient_id = self.get_id(ingredient_id_tag['href'])
                is_weapon_id = self.session.query(exists().where(Weapon.id == ingredient_id)).scalar()
                if not is_weapon_id:
                    ingredient = Ingredient(resource_id=ingredient_id, quantity=amount)
                else:
                    ingredient = Ingredient(weapon_id=ingredient_id, quantity=amount)
                recipe.ingredients.append(ingredient)
            return recipe
        else:
            return None
    
    def find_characteristics(self, soup):
        titles = soup.findAll('div', {'class':'ak-panel-title'})
        for title in titles:
            if str.strip(title.text) == 'Characteristics':
                sibling = title.findNext('div')
                return sibling.findAll('div', {'class':'ak-title'})

    def get_characteristic(self,characteristics_divs, characteristic):
        for div in characteristics_divs:
            stat_label = str.strip(div.text)
            stat_value = div.find('span')
            stat_value = stat_value.text
            split_values = str.split(stat_value, '(')
            if stat_label.startswith('AP:') and characteristic == 'ap_cost':
                    return ''.join(re.findall('[0-9]',split_values[0]))
            elif stat_label.startswith('AP:') and characteristic == 'use_per_turn':
                    return ''.join(re.findall('[0-9]',split_values[1]))
            elif stat_label.startswith('Range:') and characteristic == 'effective_range':
                min_effective_range, max_effective_range = self.get_min_max_values(stat_value)
                return (min_effective_range, max_effective_range)
            elif stat_label.startswith('CH:') and characteristic == 'crit_hit_chance':
                    num_denom = str.split(split_values[0], '/')
                    numerator = ''.join(re.findall('[0-9]', num_denom[0]))
                    denom = ''.join(re.findall('[0-9]', num_denom[1]))
                    numerator = int(numerator)
                    denom = int(denom)
                    if denom == 0:
                        return 1
                    else:
                        crit_chance = int(numerator)/int(denom) * 100
                    return floor(crit_chance)
            elif stat_label.startswith("CH:") and characteristic == 'crit_hit_bonus':
                    if len(split_values)>1:
                        return ''.join(re.findall('[0-9]',split_values[1]))
                    else:
                        return None

    def get_conditions(self,soup):
        titles = soup.findAll('div', {'class':'ak-panel-title'})
        for title in titles:
            if str.strip(title.text) == 'Conditions':
                sibling = title.findNext('div')
                content = sibling.find('div', {'class':'ak-title'})
                return str.strip(content.text)

    def get_weapon_info(self, url):
        weapon = Weapon()
        recipe = Recipe()
        id = self.get_id(url)
        if not self.session.query(exists().where(Weapon.id == id)).scalar():
            time.sleep(5)
            driver = self.dr.create_driver(self.options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            if soup.find('div', {'class': 'ak-404'}) == None:
                try:
                    weapon.id = id
                    weapon.type = self.get_type(soup)
                    weapon.level = self.get_level(soup)
                    weapon.name =  self.get_name(soup)
                    characteristics_divs = self.find_characteristics(soup)
                    weapon.ap_cost = self.get_characteristic(characteristics_divs, 'ap_cost')
                    weapon.use_per_turn = self.get_characteristic(characteristics_divs, 'use_per_turn')
                    weapon.crit_hit_chance = self.get_characteristic(characteristics_divs, 'crit_hit_chance')
                    weapon.crit_hit_bonus = self.get_characteristic(characteristics_divs, 'crit_hit_bonus')
                    weapon.min_effective_range, weapon.max_effective_range = self.get_characteristic(characteristics_divs, 'effective_range') 
                    weapon.conditions = self.get_conditions(soup)
                    weapon.description = self.get_description(soup)
                    equipment_image_link = self.get_image_link(soup)
                    effect_fields = self.find_effect_fields(soup)
                    scraped_fields = self.scrape_effect_fields(effect_fields)
                    keywords = scraped_fields.keys()
                    for keyword in keywords:
                        min_value, max_value = scraped_fields[keyword]
                        if keyword == '% Air Resistance':
                            weapon.min_percent_air_res = min_value
                            weapon.max_percent_air_res = max_value
                        if keyword == '% Earth Resistance':
                            weapon.min_percent_earth_res = min_value
                            weapon.min_percent_earth_res = max_value
                        if keyword == '% Fire Resistance':
                            weapon.min_percent_fire_res = min_value
                            weapon.max_percent_fire_res = max_value
                        if keyword == '% Neutral Resistance':
                            weapon.min_percent_neutral_res = min_value
                            weapon.max_percent_neutral_res = max_value
                        if keyword == '% Water Resistance':
                            weapon.min_percent_water_res = min_value
                            weapon.max_percent_water_res = max_value
                        if keyword == '% Ranged Resistance':
                            weapon.min_percent_ranged_res = min_value
                            weapon.max_percent_ranged_res = max_value
                        if keyword == '% Weapon Damage':
                            weapon.min_percent_weapon_damage = min_value
                            weapon.max_percent_weapon_damage = max_value
                        if keyword == '% Ranged Damage':
                            weapon.min_percent_ranged_damage = min_value
                            weapon.max_percent_ranged_damage = max_value
                        if keyword == '% Spell Damage':
                            weapon.min_percent_spell_damage = min_value
                            weapon.max_percent_spell_damage = max_value
                        if keyword == '% Critical':
                            weapon.min_percent_crit = min_value
                            weapon.max_percent_crit = max_value
                        if keyword == 'Critical Damage':
                            weapon.min_crit_damage = min_value
                            weapon.max_crit_damage = max_value
                        if keyword == 'Critical Resistance':
                            weapon.min_crit_res = min_value
                            weapon.max_crit_res = max_value
                        if keyword == 'Vitality':
                            weapon.min_vitality = min_value
                            weapon.max_vitality = max_value
                        if keyword == 'Agility':
                            weapon.min_agility = min_value
                            weapon.max_agility = max_value
                        if keyword == 'Air Damage':
                            weapon.min_air_damage = min_value
                            weapon.max_air_damage = max_value
                        if keyword == 'Air Steal':
                            weapon.min_air_steal = min_value
                            weapon.max_air_steal = max_value
                        if keyword == 'Air Resistance':
                            weapon.min_air_res = min_value
                            weapon.max_air_res = max_value
                        if keyword == 'Strength':
                            weapon.min_strength = min_value
                            weapon.max_strength = max_value
                        if keyword == 'Earth Damage':
                            weapon.min_earth_damage = min_value
                            weapon.max_earth_damage = max_value
                        if keyword == 'Earth Steal':
                            weapon.min_earth_steal = min_value
                            weapon.max_earth_steal = max_value
                        if keyword == 'Earth Resistance':
                            weapon.min_earth_Res = min_value
                            weapon.max_earth_Res = max_value
                        if keyword == 'Intelligence':
                            weapon.min_intelligence = min_value
                            weapon.max_intelligence = max_value
                        if keyword == 'Fire Damage':
                            weapon.min_fire_damage = min_value
                            weapon.max_fire_damage = max_value
                        if keyword == 'Fire Steal':
                            weapon.min_fire_steal = min_value
                            weapon.max_fire_steal = max_value
                        if keyword == 'Fire Resistance':
                            weapon.min_fire_res = min_value
                            weapon.max_fire_res = max_value
                        if keyword == 'Wisdom':
                            weapon.min_wisdom = min_value
                            weapon.max_wisdom = max_value
                        if keyword == 'Neutral Damage':
                            weapon.min_neutral_damage = min_value
                            weapon.max_neutral_damage = max_value
                        if keyword == 'Neutral Steal':
                            weapon.min_neutral_steal = min_value
                            weapon.max_neutral_steal = max_value
                        if keyword == 'Neutral Resistance':
                            weapon.min_neutral_res = min_value
                            weapon.max_neutral_res = max_value
                        if keyword == 'Chance':
                            weapon.min_chance = min_value
                            weapon.max_chance = max_value
                        if keyword == 'Water Damage':
                            weapon.min_water_damage = min_value
                            weapon.max_water_damage = max_value
                        if keyword == 'Water Steal':
                            weapon.min_water_steal = min_value
                            weapon.max_water_steal = max_value
                        if keyword == 'Water Resistance':
                            weapon.min_water_Res = min_value
                            weapon.max_water_Res = max_value
                        if keyword == 'Damage':
                            weapon.min_damage = min_value
                            weapon.max_damage = max_value
                        if keyword == 'AP':
                            weapon.min_ap = min_value
                            weapon.max_ap = max_value
                        if keyword == 'AP Parry':
                            weapon.min_ap_parry = min_value
                            weapon.max_ap_parry = max_value
                        if keyword == 'AP Reduction':
                            weapon.min_ap_reduction = min_value
                            weapon.max_ap_reduction = max_value
                        if keyword == 'Hunting Weapon':
                            weapon.is_hunting_weapon = True
                        if keyword == 'Summons':
                            weapon.min_summons = min_value
                            weapon.max_summons = max_value
                        if keyword == 'MP':
                            weapon.min_mp = min_value
                            weapon.max_mp = max_value
                        if keyword == 'MP Parry':
                            weapon.min_mp_parry = min_value
                            weapon.max_mp_parry = max_value
                        if keyword == 'MP Reduction':
                            weapon.min_mp_reduction = min_value
                            weapon.max_mp_reduction = max_value
                        if keyword == 'Dodge':
                            weapon.min_dodge = min_value
                            weapon.max_dodge = max_value
                        if keyword == 'Heals':
                            weapon.min_heals = min_value
                            weapon.max_heals = max_value
                        if keyword == 'Initiative':
                            weapon.min_initiative = min_value
                            weapon.max_initiative = max_value
                        if keyword == 'Lock':
                            weapon.min_lock = min_value
                            weapon.max_lock = max_value
                        if keyword == 'Range':
                            weapon.min_range = min_value
                            weapon.max_range = max_value
                        if keyword == 'Prospecting':
                            weapon.min_prospecting = min_value
                            weapon.max_prospecting = max_value
                        if keyword == 'Pushaback Damage':
                            weapon.min_pushback_damage = min_value
                            weapon.max_pushback_damage = max_value
                        if keyword == 'Pushback Resistance':
                            weapon.min_pushback_res = min_value
                            weapon.max_pushback_res = max_value
                        if keyword == 'Power':
                            weapon.min_power = min_value
                            weapon.max_power = max_value
                        if keyword == 'Power (traps)':
                            weapon.min_trap_power = min_value
                            weapon.max_trap_power = max_value
                        if keyword == 'Trap Damage':
                            weapon.min_trap_damage = min_value
                            weapon.max_trap_damage = max_value
                        if keyword == 'kamas':
                            weapon.min_steals_kamas = min_value
                            weapon.max_steals_kamas = max_value
                        if keyword == '(Neutral damage)':
                            weapon.min_attack_neutral_damage = min_value
                            weapon.max_attack_neutral_damage = max_value
                        if keyword == '(Fire damage)':
                            weapon.min_attack_fire_damage = min_value
                            weapon.max_attack_fire_damage = max_value
                        if keyword == '(Water damage)':
                            weapon.min_attack_water_damage = min_value
                            weapon.max_attack_water_damage = max_value
                        if keyword == '(Earth damage)':
                            weapon.min_attack_earth_damage= min_value
                            weapon.max_attack_earth_damage = max_value
                        if keyword == '(Air damage)':
                            weapon.min_attack_air_damage = min_value
                            weapon.max_attack_air_damage = max_value
                        if keyword == '(Neutral steal)':
                            weapon.min_attack_neutral_steal = min_value
                            weapon.max_attack_neutral_steal = max_value
                        if keyword == '(Fire steal)':
                            weapon.min_attack_fire_steal = min_value
                            weapon.max_attack_fire_steal = max_value
                        if keyword == '(Water steal)':
                            weapon.min_attack_water_steal = min_value
                            weapon.max_attack_water_steal = max_value
                        if keyword == '(Earth steal)':
                            weapon.min_attack_earth_steal = min_value
                            weapon.max_attack_earth_steal = max_value
                        if keyword == '(Air steal)':
                            weapon.min_attack_air_steal = min_value
                            weapon.max_attack_air_steal = max_value
                        if keyword == '(HP restored)':
                            weapon.min_attack_hp_steal = min_value
                            weapon.max_attack_hp_steal = max_value
                    recipe = self.get_recipe(soup, recipe)
                    weapon.recipe = recipe
                    self.save_image(equipment_image_link, weapon.name)
                    driver.quit()
                    return weapon
                except Exception as e: 
                    driver.quit()
                    self.failed_urls[url] = e
                    print(e)
            else:
                self.skipped_urls[url] = "404 found. Skipping"
                driver.quit()
        else:
            self.skipped_urls[url] = "Weapon found in db. Skipping"
            return None