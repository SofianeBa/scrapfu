from queue import Empty
from models.monsterresource import MonsterResource
from models.monster import Monster
from .scraper import Scraper
from sqlalchemy import exists
import time
from helpers import db
from models.resource import Resource
from bs4 import BeautifulSoup
import re

class Resourcescraper(Scraper):
    def __init__(self, blob_service_client, driver, options, queue):
        super().__init__(blob_service_client=blob_service_client, driver=driver, options=options, queue=queue)
        self.Session = db.create_session()
        self.session = self.Session()

    def get_type(self,soup):
        type= soup.find('div', {'class': 'ak-encyclo-detail-type col-xs-6'})
        type = type.findChild('span', recursive=False)
        type = type.text
        return type
    
    def get_level(self,soup):
        level = soup.find('div', {'class': 'ak-encyclo-detail-level col-xs-6 text-right'})
        level = ''.join(re.findall('[0-9]',level.text))
        level = int(level)
        return level

    def get_description(self,soup):
        description = soup.find('div',{'class':'ak-encyclo-detail-right ak-nocontentpadding'})
        description = description.findChild('div', {'class':'ak-panel-content'})
        description = str.strip(description.text)
        return description

    def get_dropped_by(self, soup):
        monster_key_drop_pairings = []
        titles = soup.findAll('div', {'class':'ak-panel-title'},recursive=True)
        for title in titles:
            text = str.strip(title.text)
            if text == 'Dropped by':
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


    def get_resource_info(self, url):
        id  = self.get_id(url)
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
                    self.save_image(imageName=name, imagelink=resourceImageLink)
                    resource = Resource(
                        id = id, 
                        name = name, 
                        type = type, 
                        level = level, 
                        description = description
                    )
                    for pairing in monster_pks:
                        monster_key = pairing['id']
                        drop_rate = pairing['drop_rate']
                        if self.session.query(exists().where(Monster.id == pairing['id'])).scalar():
                            a = MonsterResource(drop_rate=drop_rate, monster_id=monster_key)
                            resource.monsters.append(a)
                    if monster_pks is not None and resource.monsters is None:
                        self.failed_urls[url] = 'failed creating resource. All monsters that drop this resource are either incomplete or not present in db. Please check and scrape if needed'
                    driver.quit()
                    return resource
                except Exception as e:
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