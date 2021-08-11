import re
from bs4 import BeautifulSoup
from .scraper import Scraper
from models.monster import Monster
import time

class Monsterscraper(Scraper):
    def __init__(self,blob_service_client, driver, options, queue):
        super().__init__(blob_service_client=blob_service_client, driver=driver, options=options, queue=queue)

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

    def get_family(self,soup):
        family = soup.find('div', {'class': 'col-xs-8 ak-encyclo-detail-type'})
        family = family.findChild('span', recursive=False)
        return family.text

    def get_monster_info(self, url):
        time.sleep(5)
        driver = self.dr.create_driver(self.options)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        if soup.find('div', {'class': 'ak-404'}) == None:
            try:
                monsterImageLink = self.get_image_link(soup)
                name = self.get_name(soup)
                id = self.get_id(url)
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
                    minlevel=minLevel,
                    maxlevel=maxLevel,
                    minmp=minMp,
                    maxmp=maxMp,
                    minap=minAp,
                    maxap=maxAp,
                    family=family,
                    minhp=minHp,
                    maxhp=maxHp,
                    minearthres=minEarthRes,
                    maxearthres=maxEarthRes,
                    minwaterres=minWaterRes,
                    maxwaterres=maxWaterRes,
                    minfireres=minFireRes,
                    maxfireres=maxFireRes,
                    minairres=minAirRes,
                    maxairres=maxAirRes,
                    minneutralres=minNeutralRes,
                    maxneutralres=maxNeutralRes)
                driver.quit()
                return monster
            except:
                print('something went wrong!')
                driver.quit()
                return None
        else:
            driver.quit()
            return None
            