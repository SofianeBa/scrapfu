from models.equipment import Equipment
from models.weapon import Weapon
from .scraper import Scraper
from helpers import db
from models.consumable import Consumable
from models.recipe import Recipe
from bs4 import BeautifulSoup
import time, re
from sqlalchemy import exists, select
from models.ingredient import Ingredient
from models.profession import Profession

class Consumablescraper(Scraper):
    def __init__(self, driver, options, queue, update=False):
        super().__init__(driver, options, queue)
        Session = db.create_session()
        self.session = Session()
        self.update = update

    def find_effect_fields(self, soup):
            try:
                titles = soup.findAll('div', {'class': 'ak-panel-title'})
                if titles != None:
                    for title in titles:
                        if str.strip(title.text) == 'Effets':
                            effects_parent = title.parent
                            effects_list = effects_parent.findAll('div',{'class':'ak-title'})
                            return effects_list
                else: 
                    return None
            except Exception as e:
                print(e)
                return None


    def scrape_effect_fields(self, effect_fields):
        scraped_fields = {}
        expression = '$|'.join(keyword for keyword in self.keywords.keys())
        for effect_field in effect_fields:
            match = re.search(expression, str.strip(effect_field.text))
            if match:
                keyword = match.group(0)
                if keyword != 'professions' and keyword != 'energy_points':
                    value = self.get_value(effect_field.text)
                    scraped_fields[keyword] = value
                elif keyword == 'professions' or keyword == 'energy_points':
                    bonus, bonus_duration = self.get_multi_value()
                    scraped_fields[keyword] = (bonus, bonus_duration)         
        return scraped_fields
    
    def get_value(self, effect_field):
        value = ''.join(re.findall('[-,0-9]', effect_field))
        return value
    
    def get_multi_value(self, effect_field):
        split_string = str.split(effect_field, sep='for')
        bonus = ''.join(re.findall('[-,0-9]', split_string[0]))
        duration = ''.join(re.findall('[-,0-9]', split_string[1]))
        return (bonus, duration)


    def set_found_attributes(self, consumable, scraped_fields):
        for keyword in scraped_fields.keys():
            if keyword == 'professions' or keyword == 'energy_points':
                bonus, bonus_duration = scraped_fields[keyword]
                setattr(consumable, self.keywords[keyword],bonus)
                consumable.bonus_duration = bonus_duration
            else:
                value = scraped_fields[keyword]
                setattr(consumable, self.keywords[keyword], value)

    def get_conditions(self,soup):
        titles = soup.findAll('div', {'class':'ak-panel-title'})
        for title in titles:
            if str.strip(title.text) == 'Conditions':
                sibling = title.findNext('div')
                content = sibling.find('div', {'class':'ak-title'})
                return str.strip(content.text)
    
    def get_consumable_info(self,url):
        id = self.get_id(url)
        consumable_exists = self.session.query(exists().where(Consumable.id == id)).scalar()

        if not consumable_exists and not self.update:
            
            consumable = Consumable()
                        
            time.sleep(5)
            driver = self.dr.create_driver(self.options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            if soup.find('div', {'class': 'ak-404'}) == None:
                try:
                    consumable.id = id
                    consumable.name = self.get_name(soup)
                    consumable.image = self.get_image_link(soup)
                    consumable.rarity = self.get_rarity(soup)
                    consumable.type = self.get_type(soup)
                    consumable.level = self.get_level(soup)
                    consumable.description = self.get_description(soup)
                    
                    found_effects = self.find_effect_fields(soup)                    
                    if found_effects != None:
                        effet = ""
                        for effect in found_effects:
                            effet += effect.text.strip()
                            effet += ' '
                        effet = effet.rstrip(effet[-1])
                        consumable.effets = effet
                    recipes = self.get_recipe(soup)
                    if len(recipes) > 0:
                        for recipe in recipes:
                            consumable.recipes.append(recipe)
                    driver.quit()

                    return consumable

                except Exception as e:
                    driver.quit()
                    self.failed_urls[url] = e
                    print(e)
                    return None
            else:
                self.skipped_urls[url] = "404 found. Skipping"
                driver.quit()
                return None
        elif consumable_exists and self.update:
            Session = db.create_session()
            update_session = Session()
            consumable = update_session.get(Consumable, id)
            time.sleep(5)
            driver = self.dr.create_driver(self.options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            if soup.find('div', {'class': 'ak-404'}) == None:
                try:
                    consumable.image = self.get_image_link(soup)
                    driver.quit()
                except Exception as e: 
                    driver.quit()
                    self.failed_urls[url] = e
                    print(e)
            else:
                self.skipped_urls[url] = "404 found. Skipping"
                driver.quit()
                return None
            update_session.commit()
            update_session.close()
        
        else:
            self.skipped_urls[url] = "Consumable found in db. Skipping"
            return None
        



