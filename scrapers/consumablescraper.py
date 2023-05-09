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
    def __init__(self, driver, options, queue):
        super().__init__(driver, options, queue)
        Session = db.create_session()
        self.session = Session()

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



    def get_recipe(self, soup):
        recipes = []
        titles = soup.findAll('div', {'class':'ak-panel-title'},recursive=True)
        for title in titles:
            text = str.strip(title.text)
            if text == 'Recette':
                content = title.find_next_sibling('div')
                recipe_lines = content.findAll('div',{'class':'ak-panel-content'})
                for recipe_line in recipe_lines:
                    recipe = Recipe()
                    profession_section = recipe_line.find('div', {'class':'ak-panel-intro'})
                    #Si c'est vide, alors ce n'est pas une recette pour craft la ressource, mais une recette où la ressource est utilisée
                    if profession_section is None:
                        return None
                    profession_values = str.split(profession_section.text, '- Niveau')
                    profession_level = str.strip(profession_values[1])
                    profession_result = self.session.execute(select(Profession.id).where(Profession.name == str.strip(profession_values[0]).strip().lower())).one()
                    recipe.level = profession_level
                    recipe.profession_id = profession_result.id
                    ingredient_list = recipe_line.findAll('div', {'class': 'ak-list-element'})
                    for ingredient_row in ingredient_list:
                        amount_tag = ingredient_row.find('div', {'class':'ak-front'})
                        amount = ''.join(re.findall('[0-9]',amount_tag.text))
                        ingredient_id_tag = ingredient_row.find('a')
                        ingredient_id = self.get_id(ingredient_id_tag['href'])
                        is_weapon_id = self.session.query(exists().where(Weapon.id == ingredient_id)).scalar()
                        is_equipment_id = self.session.query(exists().where(Equipment.id == ingredient_id)).scalar()
                        is_consumable_id = self.session.query(exists().where(Consumable.id == ingredient_id)).scalar()
                        if is_weapon_id:
                            ingredient = Ingredient(weapon_id=ingredient_id, quantity=amount)
                        if is_equipment_id:
                            ingredient = Ingredient(equipment_id=ingredient_id, quantity=amount)
                        elif is_consumable_id:
                            ingredient = Ingredient(consumable_id=ingredient_id, quantity=amount)
                        else:
                            ingredient = Ingredient(resource_id=ingredient_id, quantity=amount)
                        recipe.ingredients.append(ingredient)
                    recipes.append(recipe)
        return recipes

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
        else:
            self.skipped_urls[url] = "Consumable found in db. Skipping"
            return None
        



