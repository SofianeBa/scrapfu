from bs4 import BeautifulSoup
import time
import re

from sqlalchemy import exists, select
from models.consumable import Consumable
from models.equipment import Equipment

from models.ingredient import Ingredient
from models.profession import Profession
from models.recipe import Recipe
from models.weapon import Weapon

class Scraper():
    def __init__(self, driver, options, queue):
        #self.blob_service_client = blob_service_client
        self.dr = driver
        self.options = options
        self.url_queue = queue
        self.failed_urls = {}
        self.skipped_urls = {}
        

    #def save_image(self, imagelink, imageName):
    #        blob_client = self.blob_service_client.get_blob_client(container='wakfu-pics', blob=f'{imageName}.png')
    #        try:
    #            blob_client.upload_blob_from_url(imagelink)
    #        except ResourceExistsError:
    #            print(f'{imageName}.png blob already exists')
    #        except:
    #            print('something else went wrong!')

    def get_type(self, soup):
        strong_tags = soup.findAll('strong')
        for strong_tag in strong_tags:
            if str.strip(strong_tag.text) == 'Type':
                parent = strong_tag.parent
                strong_value = parent.find('span')
                return strong_value.text

    def get_description(self, soup):
        titles = soup.findAll('div', {'class': 'ak-panel-title'})
        for title in titles:
            if str.strip(title.text) == 'Description':
                title_parent = title.parent
                description_value = title_parent.find('div', {'class':'ak-panel-content'})
                return str.strip(description_value.text)

    def get_level(self, soup):
        level_tag = soup.find('div', {'class':'ak-encyclo-detail-level col-xs-6 text-right'})
        level_value = ''.join(re.findall('[0-9]', level_tag.text))
        return level_value

    def get_image_link(self,soup):
        resourceImage = soup.find('div', {'class':'ak-encyclo-detail-illu'})
        if resourceImage:
            resourceImage = resourceImage.findChild('img')
            resourceImageLink = resourceImage['src']
        else:
            return None
        return resourceImageLink

    def get_name(self,soup):
        name = soup.find('h1', {'class': 'ak-return-link'})
        name = str.strip(name.text)
        return name

    def get_id(self, url):
        url = str.split(url,'-')[0]
        object_id = ''.join(re.findall('[0-9]',url))
        object_id = int(object_id)
        return object_id 
    
    def get_rarity(self, soup):
        rarity = soup.find('div',{'class':'ak-object-rarity'})
        return rarity.findAll('span')[0].text.strip()

    def get_link(self, url, tag,page_start,pages):
        #need to find a better way to determine the amount of pages in the table. 
            pageNumber = page_start
            driver = self.dr.create_driver(self.options)
            while pageNumber < pages + 1:
                driver.get(self.dr.create_full_url(url+str(pageNumber)))
                soup = BeautifulSoup(driver.page_source, 'lxml')
                tbody = soup.find('tbody')
                rows = tbody.find_all('tr')
                for row in rows:
                    link = row.find('a')
                    fullURL =  {self.dr.create_full_url(link['href']): tag}
                    self.url_queue.put(fullURL)
                pageNumber += 1
                time.sleep(1)
            driver.quit()
            return f"Done scraping {tag} urls"

    def get_dropped_by(self, soup):
        monster_key_drop_pairings = []
        titles = soup.findAll('div', {'class':'ak-panel-title'},recursive=True)
        for title in titles:
            text = str.strip(title.text)
            if text == 'Peut être obtenu sur':
                content = title.find_next_sibling('div')
                columns = content.findAll('div',{'class':'ak-column ak-container col-xs-12 col-md-6'})
                for column in columns:
                    link_raw = column.find('a')
                    monster_name = column.find('div', {'class':'ak-title'})
                    if str.strip(monster_name.text):
                        link_raw = str.split(link_raw['href'],'-')[0]
                        drop_rate_raw = column.find('div',{'class':'ak-aside'})
                        drop_rate_raw = drop_rate_raw.text
                        drop_rate = ''.join(re.findall('[.,0-9]',drop_rate_raw))
                        monster_pk = ''.join(re.findall('[0-9]', link_raw))
                        pairing = {'id': monster_pk, 'drop_rate': drop_rate}
                        monster_key_drop_pairings.append(pairing)
        return monster_key_drop_pairings

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