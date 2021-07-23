import re
from bs4 import BeautifulSoup
from models.monster import Monster
from azure.core.exceptions import ResourceExistsError
import time

class Monsterscraper:
    def __init__(self, blob_service_client, driver, options,queue):
        self.blob_service_client = blob_service_client
        self.dr = driver
        self.options = options
        self.url_queue = queue

    def parse_ranges(self, soup, stat):
        result = soup.find(text=re.compile(stat))
        div = result.parent
        range = div.findChild('span')
        rangeText = str.split(range.text, sep='to')
        if len(rangeText) > 1:
            begin = ''.join(re.findall('[-,0-9]',rangeText[0]))
            end = ''.join(re.findall('[-,0-9]',rangeText[1]))
        else:
            begin = ''.join(re.findall('[-,0-9]',rangeText[0]))
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
    
    def save_monster_image(self, imageData, imageName):
        blob_client = self.blob_service_client.get_blob_client(container='dofus-pics', blob=f'{imageName}.png')
        try:
            blob_client.upload_blob_from_url(imageData)
        except ResourceExistsError:
            print(f'{imageName}.png blob already exists')

    def get_link_to_monsters(self):
    #need to find a better way to determine the amount of pages in the table. 
        pageNumber = 91
        driver = self.dr.create_driver(self.options)
        driver.get(self.dr.create_full_url('/en/mmorpg/encyclopedia/monsters'))
        while pageNumber < 93:
            soup = BeautifulSoup(driver.page_source, 'lxml')
            tbody = soup.find('tbody')
            rows = tbody.find_all('tr')
            for row in rows:
                links = row.find_all('a')
                for link in links: 
                    fullURL =  self.dr.create_full_url(link['href'])
                    self.url_queue.put(fullURL)
            driver.get(self.dr.create_full_url('/en/mmorpg/encyclopedia/monsters?page='+str(pageNumber)))
            pageNumber += 1
            time.sleep(1)
        driver.quit()
        return "Done scraping monster urls"

    def get_monster_info(self, url):
        time.sleep(.5)
        driver = self.dr.create_driver(self.options)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        if soup.find('div', {'class': 'ak-404'}) == None:
            monsterImageNumber = ''.join(re.findall('[0-9]',url))
            monsterImageLink = f'https://static.ankama.com/dofus/www/game/monsters/200/{monsterImageNumber}.png'
            name = soup.find('h1', {'class': 'ak-return-link'})
            family = soup.find('div', {'class': 'col-xs-8 ak-encyclo-detail-type'})
            family = family.findChild('span', recursive=False)
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
            name = str.strip(name.text)
            family = family.text
            monster = Monster(
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
            self.save_monster_image(monsterImageLink,name)
            driver.quit()
            return monster
        else:
            driver.quit()
            return None