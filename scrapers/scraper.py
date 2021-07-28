from azure.core.exceptions import ResourceExistsError
from bs4 import BeautifulSoup
import time
import re

class Scraper():
    def __init__(self,blob_service_client, driver, options, queue):
        self.blob_service_client = blob_service_client
        self.dr = driver
        self.options = options
        self.url_queue = queue

    def save_image(self, imagelink, imageName):
            blob_client = self.blob_service_client.get_blob_client(container='dofus-pics', blob=f'{imageName}.png')
            try:
                blob_client.upload_blob_from_url(imagelink)
            except ResourceExistsError:
                print(f'{imageName}.png blob already exists')
            except:
                print('something else went wrong!')

    def get_image_link(self,soup):
        resourceImage = soup.find('div', {'class':'ak-encyclo-detail-illu'})
        resourceImage = resourceImage.findChild('img')
        resourceImageLink = resourceImage['src']
        return resourceImageLink

    def get_name(self,soup):
        name = soup.find('h1', {'class': 'ak-return-link'})
        name = str.strip(name.text)
        return name

    def get_id(self, url):
        monsterImageNumber = ''.join(re.findall('[0-9]',url))
        monsterImageNumber = int(monsterImageNumber)
        return monsterImageNumber 

    def get_link(self, url, tag,pages):
        #need to find a better way to determine the amount of pages in the table. 
            pageNumber = 1
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