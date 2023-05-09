from queue import Empty
from models.consumable import Consumable
from models.equipment import Equipment
from models.monsterresource import MonsterResource
from models.ingredient import Ingredient
from models.monster import Monster
from models.profession import Profession
from models.recipe import Recipe
from models.weapon import Weapon
from .scraper import Scraper
from sqlalchemy import exists, select
import time
from helpers import db
from models.resource import Resource
from bs4 import BeautifulSoup
import re

class Resourcescraper(Scraper):
    def __init__(self, driver, options, queue):
        super().__init__(driver=driver, options=options, queue=queue)
        self.Session = db.create_session()
        self.session = self.Session()
       
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
    


    def get_resource_info(self, url):
        id  = self.get_id(url)
        #Item 29048 cape de no contient un caractère spécial pouvant poser problème avec le systeme de log / A scrap solo sans log
        if (id == 29048 or id == "29048"):
            return None
        resource_exists = self.session.query(exists().where(Resource.id == id)).scalar()
        if not resource_exists:
            time.sleep(5)
            driver = self.dr.create_driver(self.options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            if soup.find('div', {'class': 'ak-404'}) == None:
                try:
                    resourceImageLink = self.get_image_link(soup)
                    name = self.get_name(soup)
                    type = self.get_type(soup)
                    level = self.get_level(soup)
                    description = self.get_description(soup)
                    monster_pks = self.get_dropped_by(soup)
                    rarity = self.get_rarity(soup)
                    #self.save_image(imageName=name, imagelink=resourceImageLink)
                    resource = Resource(
                        id = id, 
                        name = name, 
                        type = type, 
                        level = level, 
                        description = description,
                        image = resourceImageLink,
                        rarity = rarity
                    )
                    recipes = self.get_recipe(soup)
                    if len(recipes) > 0:
                        for recipe in recipes:
                            resource.recipes.append(recipe)
                    monsters = []
                    for pairing in monster_pks:
                        monster_key = pairing['id']
                        drop_rate = pairing['drop_rate']
                        if self.session.query(exists().where(Monster.id == pairing['id'])).scalar():
                            a = MonsterResource(drop_rate=drop_rate, monster_id=monster_key, resource_id=resource.id)
                            monsters.append(a)
                    if monster_pks is not None and resource.monsters is None:
                        self.failed_urls[url] = 'failed creating resource. All monsters that drop this resource are either incomplete or not present in db. Please check and scrape if needed'
                    driver.quit()
                    return resource,monsters
                except Exception as e:
                    print(e)
                    driver.quit()
                    self.failed_urls[url] = e
                    return None
            else:
                driver.quit()
                self.failed_urls[url] = 'skipped due to 404'
                return None
        else:
            self.skipped_urls[url] = 'Present in DB. Skipping'
            return None