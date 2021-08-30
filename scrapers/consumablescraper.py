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
    def __init__(self, blob_service_client, driver, options, queue):
        super().__init__(blob_service_client, driver, options, queue)
        Session = db.create_session()
        self.session = Session()
        self.keywords = {
            'Agility':'agility', 
            'Chance':'chance' ,
            'Intelligence':'intelligence',
            'Strength':'strength' ,
            'Wisdom':'wisdom' ,
            'HP':'hp' ,
            'energy points':'energy',
            'professions':'profession_bonus',
            'experience bonus': 'xp_bonus' ,
        }

    def find_effect_fields(self, soup):
            try:
                titles = soup.findAll('div', {'class': 'ak-panel-title'})
                if titles != None:
                    for title in titles:
                        if str.strip(title.text) == 'Effects':
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
                    ingredient = Ingredient(resource_id=ingredient_id, quantity=amount)
                    recipe.ingredients.append(ingredient)
                return recipe
            else:
                return None

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

        if not consumable_exists:
            
            consumable = Consumable()
            recipe = Recipe()
            
            time.sleep(5)
            driver = self.dr.create_driver(self.options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            if soup.find('div', {'class': 'ak-404'}) == None:
                try:
                    consumable.id = id
                    consumable.name = self.get_name(soup)

                    image_link = self.get_image_link(soup)
                    self.save_image(image_link, consumable.name)
                    
                    consumable.type = self.get_type(soup)
                    consumable.level = self.get_level(soup)
                    consumable.description = self.get_description(soup)
                    consumable.conditions = self.get_conditions(soup)
                    
                    found_effects = self.find_effect_fields(soup)
                    
                    if found_effects != None:
                        scraped_values = self.scrape_effect_fields(found_effects)
                        self.set_found_attributes(consumable, scraped_values)

                    recipe = self.get_recipe(soup, recipe)
                    consumable.recipe = recipe

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
        else:
            self.skipped_urls[url] = "Weapon found in db. Skipping"
            return None
        



