from psycopg2.extras import NumericRange
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
    def __init__(self,blob_service_client, driver, options, queue, update):
        super().__init__(blob_service_client=blob_service_client, driver=driver, options=options, queue=queue)
        self.keywords = {
        '% Air Resistance': 'percent_air_res','% Earth Resistance': 'percent_earth_res','% Fire Resistance': 'percent_fire_res',
        '% Neutral Resistance': 'percent_neutral_res','% Water Resistance': 'percent_water_res','% Ranged Resistance': 'percent_ranged_res',
        '% Weapon Damage':'percent_weapon_damage','% Ranged Damage': 'percent_ranged_damage','% Spell Damage': 'percent_spell_damage',
        '% Critical': 'percent_crit','Critical Damage': 'crit_damage','Critical Resistance': 'crit_res','Vitality': 'vitality','Agility': 'agility',
        'Air Damage': 'air_damage','Air Resistance': 'air_res','Strength': 'strength','Earth Damage': 'earth_damage','Earth Resistance': 'earth_Res',
        'Intelligence': 'intelligence','Fire Damage': 'fire_damage','Fire Resistance': 'fire_res','Wisdom': 'wisdom','Neutral Damage': 'neutral_damage',
        'Neutral Resistance': 'neutral_res','Chance': 'chance','Water Damage': 'water_damage','Water Resistance': 'water_Res','Damage': 'damage',
        'AP': 'ap','AP Parry': 'ap_parry','AP Reduction': 'ap_reduction','Hunting weapon': 'is_hunting_weapon','Summons': 'summons','MP': 'mp','MP Parry': 'mp_parry',
        'MP Reduction': 'mp_reduction','Dodge': 'dodge','Heals': 'heals','Initiative': 'initiative','Lock': 'lock','Range': 'range','Prospecting': 'prospecting',
        'Pushaback Damage': 'pushback_damage','Pushback Resistance': 'pushback_res','Power': 'power','Power [(]traps[)]': 'trap_power','Trap Damage': 'trap_damage',
        'kamas': 'steals_kamas','[(]Neutral damage[)]': 'attack_neutral_damage','[(]Fire damage[)]': 'attack_fire_damage','[(]Water damage[)]': 'attack_water_damage',
        '[(]Earth damage[)]': 'attack_earth_damage','[(]Air damage[)]': 'attack_air_damage','[(]Neutral steal[)]': 'attack_neutral_steal','[(]Fire steal[)]': 'attack_fire_steal',
        '[(]Water steal[)]': 'attack_water_steal','[(]Earth steal[)]': 'attack_earth_steal','[(]Air steal[)]': 'attack_air_steal',"[(]HP restored[)]": 'attack_hp_steal'
        }
        self.found_keywords = []
        self.Session = db.create_session()
        self.session = self.Session()
        self.update = update

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
              begin, end = self.reverse_min_max_values(begin,end)
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
                if keyword != 'Hunting weapon':
                    min_value, max_value = self.get_min_max_values(effect_field.text)
                    scraped_fields[keyword] = (min_value,max_value)
                elif keyword == 'Hunting weapon':
                    scraped_fields[keyword] = (0,0)
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

    def set_found_attributes(self,weapon, keywords, scraped_fields):
        for keyword in keywords:
            min_value, max_value = scraped_fields[keyword]
            if '(' in keyword:
                keyword = str.replace(keyword, '(', '[(]')
                keyword = str.replace(keyword, ')', '[)]')
            if keyword != 'Hunting weapon':
                pass
                setattr(weapon, self.keywords[keyword], NumericRange(lower=min_value,upper=max_value,bounds='[]',empty=False))
            elif keyword == 'Hunting weapon':
                setattr(weapon, self.keywords[keyword], True)

    def get_weapon_info(self, url):
        
        id = self.get_id(url)
        weapon_exists = self.session.query(exists().where(Weapon.id == id)).scalar()

        if not weapon_exists and not self.update:
            weapon = Weapon()
            weapon = Recipe()
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
                    min_effective_range, max_effective_range = self.get_characteristic(characteristics_divs, 'effective_range')
                    weapon.effective_range = NumericRange(lower=min_effective_range,upper=max_effective_range,bounds='[]', empty=False)
                    weapon.conditions = self.get_conditions(soup)
                    weapon.description = self.get_description(soup)
                    equipment_image_link = self.get_image_link(soup)
                    effect_fields = self.find_effect_fields(soup)
                    scraped_fields = self.scrape_effect_fields(effect_fields)
                    keywords = scraped_fields.keys()
                    self.set_found_attributes(weapon,keywords,scraped_fields)
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
        elif weapon_exists and self.update:
            print('hoozah!')
            weapon = self.session.get(Weapon, id)
            time.sleep(5)
            driver = self.dr.create_driver(self.options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'lxml')
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
                min_effective_range, max_effective_range = self.get_characteristic(characteristics_divs, 'effective_range')
                weapon.effective_range = NumericRange(lower=min_effective_range,upper=max_effective_range,bounds='[]', empty=False)
                weapon.conditions = self.get_conditions(soup)
                weapon.description = self.get_description(soup)
                effect_fields = self.find_effect_fields(soup)
                scraped_fields = self.scrape_effect_fields(effect_fields)
                keywords = scraped_fields.keys()
                self.set_found_attributes(weapon,keywords,scraped_fields)
                driver.quit()
            except Exception as e: 
                driver.quit()
                self.failed_urls[url] = e
                print(e)
            self.session.commit()
        else:
            self.skipped_urls[url] = "Weapon found in db. Skipping"
            return None