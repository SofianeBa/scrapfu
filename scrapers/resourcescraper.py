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
                print(f'{id} {name} {type} {level}')
                self.save_image(imageName=name, imagelink=resourceImageLink)
                resource = Resource(
                    id = id, 
                    name = name, 
                    type = type, 
                    level = level, 
                    description = description
                )
                driver.quit()
                #need to create resource and assign values. Work on relationship with monsters.
            except Exception as e:
                print(e)
                driver.quit()
                return None
        else:
            driver.quit()
            return None
            