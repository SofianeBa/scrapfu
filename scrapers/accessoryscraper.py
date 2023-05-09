from models.accessory import Accessory
from models.equipment import Equipment
from models.monster import Monster
from models.monsteraccessory import MonsterAccessory
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

class Accessoryscraper(Scraper):
    def __init__(self, driver, options, queue):
        super().__init__(driver, options, queue)
        Session = db.create_session()
        self.session = Session()
        self.keywords = {
            'PV': 'pv','PA': 'pa','PM': 'pm','PW': 'pw','Portée': 'po','Armure reçue': 'armure_recu',
            'Armure donnée': 'armure_donne', 'Maîtrise Eau': 'maitrise_eau','Maîtrise Feu': 'maitrise_feu',
            'Maîtrise Terre': 'maitrise_terre','Maîtrise Air': 'maitrise_air', 'Résistance Feu': 'resistance_feu',
            'Résistance Eau': 'resistance_eau','Résistance Terre': 'resistance_terre','Résistance Air': 'resistance_air',
            '% Coup Critique': 'pourcent_critique','% Parade': 'pourcent_parade','Initiative': 'initiative',
            'Esquive': 'esquive','Tacle': 'tacle','Sagesse': 'sagesse','Prospection': 'prospection','Contrôle': 'controle',
            'Volonté' :'volonte','Maîtrise Critique': 'maitrise_critique','Résistance Critique': 'resistance_critique',
            'Maîtrise Dos': 'maitrise_dos', 'Résistance Dos': 'resistance_dos','Maîtrise Mêlée': 'maitrise_melee',
            'Maîtrise Distance': 'maitrise_distance','Maîtrise Monocible': 'maitrise_monocible',
            'Maîtrise Zone': 'maitrise_zone','Maîtrise Soin': 'maitrise_soin','Maîtrise Berserk': 'maitrise_berserk',
            'Maîtrise Élémentaire': 'maitrise_elem','Maîtrise sur 1 élément aléatoire': 'maitrise_elem_1',
            'Maîtrise sur 2 éléments aléatoires': 'maitrise_elem_2','Maîtrise sur 3 éléments aléatoires': 'maitrise_elem_3',
            'Résistance Élémentaire': 'resistance_elem','Résistance sur 1 élément aléatoire': 'resistance_elem_1',
            'Résistance sur 2 éléments aléatoires': 'resistance_elem_2', 'Résistance sur 3 éléments aléatoires': 'resistance_elem_3',
            'Niv. aux sorts élémentaires': 'niv_sort_elem','Niv. aux sorts Air': 'niv_sort_air','Niv. aux sorts Terre': 'niv_sort_terre',
            'Niv. aux sorts Feu': 'niv_sort_feu', 'Niv. aux sorts Eau': 'niv_sort_eau','% Quantité Récolte en Mineur': 'quantite_recolte_mineur',
            '% Quantité Récolte en Paysan': 'quantite_recolte_paysan','% Quantité Récolte en Forestier': 'quantite_recolte_forestier',
            '% Quantité Récolte en Herboriste': 'quantite_recolte_herboriste','% Quantité Récolte en Trappeur': 'quantite_recolte_trappeur',
            '% Quantité Récolte en Pêcheur': 'quantite_recolte_pêcheur'
            }
        self.found_keywords = []
    
    def find_carac_fields(self, soup):
            try:
                titles = soup.findAll('div', {'class': 'ak-panel-title'})
                for title in titles:
                    if str.strip(title.text) == 'Caractéristiques':
                        effects_parent = title.parent
                        effects_list = effects_parent.findAll('div',{'class':'ak-title'})
                        return effects_list
            except Exception as e:
                print(e)
                return None
            
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
                        elif is_equipment_id:
                            ingredient = Ingredient(equipment_id=ingredient_id, quantity=amount)
                        elif is_consumable_id:
                            ingredient = Ingredient(consumable_id=ingredient_id, quantity=amount)
                        else:
                            ingredient = Ingredient(resource_id=ingredient_id, quantity=amount)
                        recipe.ingredients.append(ingredient)
                    recipes.append(recipe)
        return recipes
    
    def scrape_carac_fields(self, effect_fields):
        scraped_fields = {}
        expression = '$|'.join(keyword for keyword in self.keywords.keys())
        for effect_field in effect_fields:
            match = re.search(expression, str.strip(effect_field.text))
            if match:
                keyword = match.group(0)
                scraped_fields[keyword] = (''.join(re.findall('[-,0-9]',effect_field.text)))
        return scraped_fields
    
    def get_accessory_info(self, url):
        id = self.get_id(url)
        accessory_exists = self.session.query(exists().where(Accessory.id == id)).scalar()

        if not accessory_exists:
            accessory = Accessory()
            time.sleep(5)
            driver = self.dr.create_driver(self.options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            if soup.find('div', {'class': 'ak-404'}) == None:
                try:
                    accessory.id = id
                    accessory.type = self.get_type(soup)
                    accessory.level = self.get_level(soup)
                    accessory.name =  self.get_name(soup)
                    accessory.rarity = self.get_rarity(soup)
                    accessory.description = self.get_description(soup)
                    accessory.image = self.get_image_link(soup)
                    effect_fields = self.find_carac_fields(soup)
                    if effect_fields:
                        scraped_fields = self.scrape_carac_fields(effect_fields)
                        keywords = scraped_fields.keys()
                        for keyword in keywords:
                            value = scraped_fields[keyword]
                            if 'Maîtrise sur' in keyword:
                                setattr(accessory, self.keywords[keyword], value[:-1])
                            elif 'Résistance sur' in keyword:
                                setattr(accessory, self.keywords[keyword], value[:-1])
                            else:
                                setattr(accessory, self.keywords[keyword], value)
                    recipes = self.get_recipe(soup)
                    if len(recipes) > 0:
                        for recipe in recipes:
                            accessory.recipes.append(recipe)
                    monsters = self.get_dropped_by(soup)
                    if len(monsters) > 0 :
                        for pairing in monsters:
                            monster_key = pairing['id']
                            drop_rate = pairing['drop_rate']
                            if self.session.query(exists().where(Monster.id == pairing['id'])).scalar():
                                a = MonsterAccessory(drop_rate=drop_rate, monster_id=monster_key,accessory_id=accessory.id)
                                accessory.remember.append(a)
                        if monsters is not None and accessory.monsters is None:
                            self.failed_urls[url] = 'failed creating resource. All monsters that drop this resource are either incomplete or not present in db. Please check and scrape if needed'
                    driver.quit()
                    return accessory
                except Exception as e: 
                    driver.quit()
                    self.failed_urls[url] = e
                    print(e)
            else:
                self.skipped_urls[url] = "404 found. Skipping"
                driver.quit()
        else:
            self.skipped_urls[url] = "Accessory found in db. Skipping"
            return None
