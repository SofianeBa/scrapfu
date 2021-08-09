from .scraper import Scraper
import time
import re
from bs4 import BeautifulSoup


class Equipmentscraper(Scraper):
    def __init__(self,blob_service_client, driver, options, queue):
        super().__init__(blob_service_client=blob_service_client, driver=driver, options=options, queue=queue)
        self.keywords = ['AP', 'AP Parry', 'AP Reduction', 'Agility', 'Air Damage',
        "% Air Resistance", 'Chance', 'Water Damage', "% Water Resistance", 'Prospecting',
        'Intelligence','Fire Damage', "% Fire resistance", "Strength", "Earth Damage",
        "% Earth Resistance", "Pods", "Wisdom", "Neutral Damage", "% Neutral Resistance", 
        "Damage", "Damage Reflected", "Critical Damage", "Critical Resistance", "% Critical",
        "Pushback Damage", "Pushback Resistance", "Dodge", "Heals", "Initiative", "Lock", "MP",
        "MP Parry", "MP Reduction", "% Melee Damage", "% Melee Resistance", "% Ranged Damage", 
        "% Ranged Resistance", "% Spell Damage", "% Weapon Damage", "Summons", "Trap Damage", "Range"]

    def scan_effect_fields():
        #return keywords found
        pass

    def scrape_effect_fields():
        #scrape all rows using keywords found with scan_effect_fields()
        pass
    
    def get_level(self, soup):
        level_tag = soup.find('div', {'class':'ak-encyclo-detail-level col-xs-6 text-right'})
        level_value = ''.join(re.findall('[-,0-9]', level_tag.text))
        return level_value
    
    def get_description(self, soup):
        titles = soup.findAll('div', {'class': 'ak-panel-title'})
        for title in titles:
            if str.strip(title.text) == 'Description':
                description_value = title.nextSibling
                return description_value.text

    def get_type(self, soup):
        strong_tags = soup.findAll('strong')
        for strong_tag in strong_tags:
            if str.strip(strong_tag.text) == 'Type':
                type_value = strong_tag.nextSibling
                return type_value.text

    def get_equipment_info(self, url):
        time.sleep(5)
        driver = self.dr.create_driver(self.options)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        if soup.find('div', {'class': 'ak-404'}) == None:
            equipment_id = self.get_id(url)
            equipment_type = self.get_type(soup)
            equipment_level = self.get_level(soup)
            equipment_name =  self.get_name(soup)
            equipment_description = self.get_description(soup)
            equipment_image_link = self.get_image_link(soup)
            
            self.save_image(equipment_image_link, equipment_name)
            print(equipment_id)
            print(equipment_name)
            print(equipment_type)
            print(equipment_level)