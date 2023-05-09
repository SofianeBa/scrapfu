import re
import time
from bs4 import BeautifulSoup
from sqlalchemy import exists
from helpers import db
from models.monsterharvest import MonsterHarvest
from scrapers.scraper import Scraper


class MonsterHarvestscraper(Scraper):
    def __init__(self, driver, options, queue):
        super().__init__(driver, options, queue)
        Session = db.create_session()
        self.session = Session()

    def get_harvest_list(self, soup):
        monster_harvest = []
        titles = soup.findAll('div', {'class':'ak-panel-title'},recursive=True)
        for title in titles:
            text = str.strip(title.text)
            if text.strip() == 'Permet de recolter':
                content = title.find_next_sibling('div')
                columns = content.findAll('div',{'class':'ak-column ak-container col-xs-12 col-md-6'})
                for column in columns:
                    link_raw = column.find('a')
                    resource_name = column.find('div', {'class':'ak-title'})
                    if str.strip(resource_name.text):
                        link_raw = str.split(link_raw['href'],'-')[0]
                        job = column.find('div',{'class':'ak-text'}).text.split(" - ")
                        job_name = job[0].strip()
                        job_level = ''.join(re.findall('[.,0-9]',job[1])).strip()
                        resource_id = ''.join(re.findall('[0-9]', link_raw))
                        drop = MonsterHarvest(job_name=job_name,job_level=job_level,resource_id=resource_id)
                        monster_harvest.append(drop)
        return monster_harvest

    def get_monster_harvest_info(self,url):
        monster_id = self.get_id(url)
        monster_harvest_exists = self.session.query(exists().where(MonsterHarvest.id == id)).scalar()
        
        if not monster_harvest_exists:
            monster_harvest = object
            monster_harvest.no = True
            time.sleep(5)
            driver = self.dr.create_driver(self.options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            if soup.find('div', {'class': 'ak-404'}) == None:
                try:
                    harvest_list = self.get_harvest_list(soup)
                    for harvested in harvest_list:
                        monster_harvest.remember(harvested)
                except Exception as e:
                    driver.quit()
                    self.failed_urls[url] = e
                    print(e)
                    return None
            else:
                self.skipped_urls[url] = "404 found. Skipping"
                driver.quit()
                return None
        else:
            self.skipped_urls[url] = "Consumable found in db. Skipping"
            return None
