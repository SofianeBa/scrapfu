import re
from bs4 import BeautifulSoup
from .scraper import Scraper
from models.monster import Monster
from helpers import db
from sqlalchemy import exists
from psycopg2.extras import NumericRange
import time

class Monsterscraper(Scraper):
    def __init__(self,blob_service_client, driver, options, queue):
        super().__init__(blob_service_client=blob_service_client, driver=driver, options=options, queue=queue)
        self.Session = db.create_session()
        self.session = self.Session()
    def parse_ranges(self, soup, stat):
        result = soup.find(text=re.compile(stat))
        div = result.parent
        range = div.findChild('span')
        rangeText = str.split(range.text, sep='to')
        if len(rangeText) > 1:
            begin = ''.join(re.findall('[-,0-9]',rangeText[0]))
            end = ''.join(re.findall('[-,0-9]',rangeText[1]))
            try:
                begin = int(str.strip(begin))
            except:
                begin = end
            try:
                end = int(str.strip(end))
            except:
                end = begin
        else:
            begin = ''.join(re.findall('[-,0-9]',rangeText[0]))
            try:
                begin = int(str.strip(begin))
            except:
                begin = 1
            end = begin
        return (begin,end)
    
    def parse_level_ranges(self, levels):
        if len(levels) > 1:
            begin = ''.join(re.findall('[0-9]',levels[0]))
            end = ''.join(re.findall('[0-9]',levels[1]))
        else:
            begin = ''.join(re.findall('[0-9]',levels[0]))
            end = begin
        return (begin,end)

    def get_numeric_range(min,max):
        range = NumericRange(lower = min, upper=max, bounds='[]', empty=False)
        return range
    
    def get_family(self,soup):
        family = soup.find('div', {'class': 'col-xs-8 ak-encyclo-detail-type'})
        family = family.findChild('span', recursive=False)
        return family.text

    def get_monster_info(self, url):
        id = self.get_id(url)
        monster_exists = self.session.query(exists().where(Monster.id == id)).scalar()
        if not monster_exists:
            time.sleep(5)
            driver = self.dr.create_driver(self.options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            if soup.find('div', {'class': 'ak-404'}) == None:
                try:
                    monsterImageLink = self.get_image_link(soup)
                    name = self.get_name(soup)
                    if monsterImageLink:
                        self.save_image(monsterImageLink,name)
                    family = self.get_family(soup)
                    levelRange = soup.find('div', {'class': 'col-xs-4 text-right ak-encyclo-detail-level'},text=True)
                    minLevel, maxLevel = self.parse_level_ranges(str.split(levelRange.text, sep="to"))
                    minHp, maxHp = self.parse_ranges(soup, 'HP:')
                    minAp, maxAp = self.parse_ranges(soup, "AP:")
                    minMp, maxMp = self.parse_ranges(soup, "MP:")
                    minEarthRes,maxEarthRes = self.parse_ranges(soup, "Earth:")
                    minAirRes, maxAirRes = self.parse_ranges(soup, "Air:")
                    minFireRes, maxFireRes = self.parse_ranges(soup, "Fire:")
                    minWaterRes, maxWaterRes = self.parse_ranges(soup, "Water:")
                    minNeutralRes, maxNeutralRes = self.parse_ranges(soup, "Neutral:")
                    monster = Monster(
                        id = id,
                        name=name,
                        family=family,
                        level = self.get_numeric_range(minLevel,maxLevel),
                        mp = self.get_numeric_range(minMp,maxMp),
                        ap = self.get_numeric_range(minAp,maxAp),
                        hp = self.get_numeric_range(minHp,maxHp),
                        waterres = self.get_numeric_range(minWaterRes,maxWaterRes),
                        fireres = self.get_numeric_range(minFireRes,maxFireRes),
                        earthres = self.get_numeric_range(minEarthRes,maxEarthRes),
                        airres = self.get_numeric_range(minAirRes,maxAirRes),
                        neutralres = self.get_numeric_range(minNeutralRes,maxNeutralRes)
                    )
                    driver.quit()
                    return monster
                except Exception as e:
                    self.failed_urls[url] == e
                    driver.quit()
                    return None
            else:
                driver.quit()
                self.skipped_urls[url] == 'Skipping due to 404'
                return None
        else:
            self.skipped_urls[url] == 'Present in DB. Skipping'
            return None
            