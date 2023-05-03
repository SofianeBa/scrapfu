from .scraper import Scraper
from bs4 import BeautifulSoup
import time
from models.profession import Profession

class Professionscraper(Scraper):
    def __init__(self, driver, options, queue):
        super().__init__(driver=driver, options=options, queue=queue)

    def get_link(self, url, tag,pages):
        #need to find a better way to determine the amount of pages in the table. 
            pageNumber = 1
            browser = self.dr.create_driver(self.options)
            while pageNumber < pages + 1:
                browser.get(self.dr.create_full_url(url+str(pageNumber)))
                soup = BeautifulSoup(browser.page_source, 'lxml')
                professionlist = soup.findAll('div', {'class':'ak-mosaic-item-detail'})
                for profession in professionlist:
                    link = profession.findChild('a')
                    fullURL =  {self.dr.create_full_url(link['href']): tag}
                    self.url_queue.put(fullURL)
                pageNumber += 1
                time.sleep(1)
            browser.quit()
            return f"Done scraping {tag} urls"

    def get_description(self, soup):
        titles = soup.findAll('div', {'class': 'ak-panel-title'})
        for title in titles:
            if str.strip(title.text) == 'Profession description':
                parent = title.parent
                description = parent.find('p')
                return description.text

    def get_profession_info(self, url):
        time.sleep(5)
        driver = self.dr.create_driver(self.options)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        if soup.find('div', {'class': 'ak-404'}) == None:
            try:
                id = self.get_id(url)
                image_link = self.get_image_link(soup)
                name = self.get_name(soup)
                description = self.get_description(soup)
                self.save_image(image_link, name)
                profession = Profession(
                    id = int(id),
                    name = name,
                    description = description
                )
                driver.quit()
                return profession
            except Exception as e:
                print(e)
                driver.quit()
                return None
        else:
            driver.quit()
            return None
