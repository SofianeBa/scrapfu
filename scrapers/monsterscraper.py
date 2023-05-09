import re
from bs4 import BeautifulSoup
from .scraper import Scraper
from models.monster import Monster
from models.monsterharvest import MonsterHarvest
from helpers import db
from sqlalchemy import exists
from psycopg2.extras import NumericRange
import time

class Monsterscraper(Scraper):
    def __init__(self, driver, options, queue):
        super().__init__(driver=driver, options=options, queue=queue)
        self.Session = db.create_session()
        self.session = self.Session()
    def parse_ranges(self, soup, stat):
        result = soup.find(text=re.compile(stat))
        if result is None:
            return 0,0
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
        return (int(begin),int(end))

    def get_numeric_range(self,min,max):
        range = NumericRange(lower = min, upper=max, bounds='[]', empty=False)
        return range
    
    def get_family(self,soup):
        family = soup.find('div', {'class': 'col-xs-8 ak-encyclo-detail-type'})
        family = family.findChild('span', recursive=False)
        return family.text
    

            
    def get_catchable(self, soup):
        catchable = soup.find('div',{'class':'catchable'})
        is_catchable = (catchable.find('strong').text.strip())
        if(is_catchable == "Non"):
            return False
        else:
            return True
        
    def get_element(self, soup, element_name):
        element = soup.find('span',{'class':'ak-icon-small ak-'+element_name})
        element_div = element.parent.parent.find('div',{'class':'ak-title'})
        element_spans = element_div.findAll('span')
        return int(element_spans[1].text.replace("%","").strip()),int(element_spans[3].text.replace("%","").strip())

    def get_harvest_list(self, soup):
        print("Let's harvest")
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
                        print(drop)
                        monster_harvest.append(drop)
        return monster_harvest

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
                        #self.save_image(monsterImageLink,name)
                        a = 1
                    family = self.get_family(soup)
                    is_catchable = self.get_catchable(soup)
                    levelRange = soup.find('div', {'class': 'col-xs-4 text-right ak-encyclo-detail-level'},text=True)
                    minLevel, maxLevel = self.parse_level_ranges(str.split(levelRange.text, sep="à"))
                    minPV, maxPV = self.parse_ranges(soup, 'Points de vie :')
                    minPA, maxPA = self.parse_ranges(soup, "Points d'action :")
                    minPM, maxPM = self.parse_ranges(soup, "PM :")
                    minInitiative, maxInitiative = self.parse_ranges(soup, "Initiative :")
                    minTacle, maxTacle = self.parse_ranges(soup, "Tacle :")
                    minEsquive, maxEsquive = self.parse_ranges(soup, "Esquive :")
                    minParade, maxParade = self.parse_ranges(soup, "Parade :")
                    minCritique, maxCritique = self.parse_ranges(soup, "Coup critique :")
                    
                    maitrise_eau_value,resistance_eau_value = self.get_element(soup,"water")
                    maitrise_terre_value,resistance_terre_value = self.get_element(soup,"earth")
                    maitrise_air_value,resistance_air_value = self.get_element(soup,"air")
                    maitrise_feu_value,resistance_feu_value = self.get_element(soup,"fire")


                    image_link = self.get_image_link(soup)
                    
                    monster = Monster(
                        id = id,
                        name=name,
                        family=family,
                        image = image_link,
                        level = self.get_numeric_range(minLevel,maxLevel),
                        pm = minPM,
                        pa = minPA,
                        pv = minPV,
                        initiative = minInitiative,
                        tacle = minTacle,
                        esquive = minEsquive,
                        parade = minParade,
                        critique = minCritique,
                        catchable = is_catchable,
                        maitrise_eau = maitrise_eau_value,
                        resistance_eau = resistance_eau_value,
                        maitrise_terre = maitrise_terre_value,
                        resistance_terre = resistance_terre_value,
                        maitrise_air = maitrise_air_value,
                        resistance_air = resistance_air_value,
                        maitrise_feu = maitrise_feu_value,
                        resistance_feu = resistance_feu_value
                    )
                    #Cela ne fonctionne pas, car les ressources n'existent pas encore...
                    #harvest_list = self.get_harvest_list(soup)
                    #for harvested in harvest_list:
                        #monster.harvest.append(harvested)
                    driver.quit()
                    return monster
                except Exception as e:
                    self.failed_urls[url] == e
                    driver.quit()
                    return None
            else:
                driver.quit()
                self.skipped_urls[url] = 'Skipping due to 404'
                return None
        else:
            self.skipped_urls[url] = 'Present in DB. Skipping'
            