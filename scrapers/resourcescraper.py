from .scraper import Scraper
import time
from bs4 import BeautifulSoup
import re

class Resourcescraper(Scraper):
    def __init__(self, blob_service_client, driver, options, queue):
        super().__init__(blob_service_client=blob_service_client, driver=driver, options=options, queue=queue)

    def get_resource_info(self, url):
        time.sleep(5)
        driver = self.dr.create_driver(self.options)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        if soup.find('div', {'class': 'ak-404'}) == None:
            try:
                resourceImageNumber = ''.join(re.findall('[0-9]',url))
                resourceImageLink = f'https://static.ankama.com/dofus/www/game/items/200/{resourceImageNumber}.png'
                name = soup.find('h1', {'class': 'ak-return-link'})
                name = str.strip(name.text)
                type= soup.find('div', {'class': 'ak-encyclo-detail-type col-xs-6'})
                type = type.findChild('span', recursive=False)
                type = type.text
                level = soup.find('div', {'class': 'ak-encyclo-detail-level col-xs-6 text-right'})
                level = ''.join(re.findall('[0-9]',level.text))
                description = ''
                self.save_image(imageName=name, imagelink=resourceImageLink)
                print(type)
                print(level)
                print (name)
                driver.quit()
            except:
                print('something went wrong!')
                driver.quit()
                return None
        else:
            driver.quit()
            return None
            