from .scraper import Scraper
import time
import re
from bs4 import BeautifulSoup
from models.equipment import Equipment


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
        "% Ranged Resistance", "% Spell Damage", "% Weapon Damage", "Summons", "Trap Damage", "Range", "Vitality"]
        self.found_keywords = []
        self.equipment = Equipment()

    def find_effect_fields(self, soup):
        titles = soup.findAll('div', {'class': 'ak-panel-title'})
        for title in titles:
            if str.strip(title.text) == 'Effects':
                effects_parent = title.parent
                effects_list = effects_parent.findAll('div',{'class':'ak-title'})
                return effects_list

    def get_min_max_values(self, effect_field):
        rangeText = str.split(effect_field, sep='to')
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
            begin_is_int = isinstance(begin, int)
            if begin_is_int == False:
                begin = 1
            end = begin
        return (begin, end)

    def scrape_effect_fields(self, effect_fields):
        for effect_field in effect_fields:
            expression = '|'.join(keyword for keyword in self.keywords)
            match = re.search(expression, effect_field.text)
            if match:
                keyword = match.group(0)
                min_value, max_value = self.get_min_max_values(effect_field.text)
                if keyword =='AP':
                    self.equipment.min_ap = min_value
                    self.equipment.max_ap = max_value
                if keyword =='AP Parry':
                    self.equipment.min_ap_parry = min_value
                    self.equipment.max_ap_parry = max_value
                if keyword =='AP Reduction':

                if keyword =='Agility': 

                if keyword =='Air Damage':

                if keyword =='% Air Resistance':

                if keyword =='Chance':

                if keyword =='Water Damage':

                if keyword =='% Water Resistance':

                if keyword =='Prospecting':

                if keyword =='Intelligence':

                if keyword =='Fire Damage' :

                if keyword =='% Fire resistance':

                if keyword =='Strength' :

                if keyword =='Earth Damage':

                if keyword =='% Earth Resistance': 

                if keyword =='Pods' :

                if keyword =='Wisdom':

                if keyword =='Neutral Damage':

                if keyword =='% Neutral Resistance':

                if keyword =='Damage':

                if keyword =='Damage Reflected':

                if keyword =='Critical Damage':

                if keyword =='Critical Resistance':

                if keyword =='% Critical':

                if keyword =='Pushback Damage':

                if keyword =='Pushback Resistance':

                if keyword =='Dodge':

                if keyword =='Heals':

                if keyword =='Initiative':

                if keyword =='Lock' :

                if keyword =='MP':

                if keyword =='MP Parry':

                if keyword =='MP Reduction':

                if keyword =='% Melee Damage': 

                if keyword =='% Melee Resistance':

                if keyword =='% Ranged Damage' :

                if keyword =='% Ranged Resistance':

                if keyword =='% Spell Damage' :

                if keyword =='% Weapon Damage':

                if keyword =='Summons':

                if keyword =='Trap Damage': 

                if keyword =='Range':

                if keyword =='Vitality':
                    self.equipment.min_vitality = min_value
                    self.equipment.max_vitality = max_value

    def get_level(self, soup):
        level_tag = soup.find('div', {'class':'ak-encyclo-detail-level col-xs-6 text-right'})
        level_value = ''.join(re.findall('[0-9]', level_tag.text))
        return level_value
    
    def get_description(self, soup):
        titles = soup.findAll('div', {'class': 'ak-panel-title'})
        for title in titles:
            if str.strip(title.text) == 'Description':
                title_parent = title.parent
                description_value = title_parent.find('div', {'class':'ak-panel-content'})
                return str.strip(description_value.text)

    def get_type(self, soup):
        strong_tags = soup.findAll('strong')
        for strong_tag in strong_tags:
            if str.strip(strong_tag.text) == 'Type':
                parent = strong_tag.parent
                strong_value = parent.find('span')
                return strong_value.text

    def get_equipment_info(self, url):
        time.sleep(5)
        driver = self.dr.create_driver(self.options)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        if soup.find('div', {'class': 'ak-404'}) == None:
            self.equipment.id = self.get_id(url)
            self.equipment.type = self.get_type(soup)
            self.equipment.level = self.get_level(soup)
            self.equipment.name =  self.get_name(soup)
            self.equipment.description = self.get_description(soup)
            equipment_image_link = self.get_image_link(soup)
            effect_fields = self.find_effect_fields(soup)
            self.scrape_effect_fields(effect_fields)
            self.save_image(equipment_image_link, self.equipment.name)
            driver.quit()