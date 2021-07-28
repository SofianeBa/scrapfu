from helpers.db import create_session
from models.mrassociation import Mrassociation
from .scraper import Scraper
import time
from models.resource import Resource
from bs4 import BeautifulSoup
import re

class Resourcescraper(Scraper):
    def __init__(self, blob_service_client, driver, options, queue):
        super().__init__(blob_service_client=blob_service_client, driver=driver, options=options, queue=queue)

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
                    drop_rate_raw = column.find('div',{'class':'ak-aside'})
                    drop_rate_raw = drop_rate_raw.text
                    drop_rate = ''.join(re.findall('[.,0-9]',drop_rate_raw))
                    monster_pk = ''.join(re.findall('[0-9]', link_raw['href']))
                    pairing = {'id': monster_pk, 'drop_rate': drop_rate}
                    monster_key_drop_pairings.append(pairing)
        return monster_key_drop_pairings


    def get_resource_info(self, url):
        time.sleep(5)
        driver = self.dr.create_driver(self.options)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        if soup.find('div', {'class': 'ak-404'}) == None:
            try:
                resourceImageLink = self.get_image_link(soup)
                id  = self.get_id(url)
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
                    a = Mrassociation(drop_rate=drop_rate, monster_id=monster_key)
                    resource.monsters.append(a)
                driver.quit()
                return resource
                #need to create resource and assign values. Work on relationship with monsters.
            except Exception as e:
                print(e)
                driver.quit()
                return None
        else:
            driver.quit()
            return None