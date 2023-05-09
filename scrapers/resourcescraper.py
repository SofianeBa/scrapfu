from models.monsterresource import MonsterResource
from models.monster import Monster
from .scraper import Scraper
from sqlalchemy import exists, select
import time
from helpers import db
from models.resource import Resource
from bs4 import BeautifulSoup

class Resourcescraper(Scraper):
    def __init__(self, driver, options, queue):
        super().__init__(driver=driver, options=options, queue=queue)
        self.Session = db.create_session()
        self.session = self.Session()
 
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