from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from queue import Queue
import sys
import urllib.request
from monster import Monster
from concurrent import futures
import time
import re
import os
from azure.storage.blob import BlobClient, BlobServiceClient

def create_driver():
    if sys.platform == 'win32':
        driver = webdriver.Chrome('.\webdriver\chromedriver.exe')
    if sys.platform == 'linux' or sys.platform == 'linux2':
        driver = webdriver.Chrome('./webdriver/chromedriver')
    return driver

base_url = "https://www.dofus.com"
url_queue = Queue(maxsize=0)
future_to_url = {}
try:
    connect_str = os.getenv('AZ_Connection_String')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
except: 
    print('oops!No environment variable by that name :(')
    print('Unable to create blob_service_client and container_client')

def create_full_url(base, addition):
    return base + addition

def get_link_to_monsters():
    #need to find a better way to determine the amount of pages in the table. 
    pageNumber = 8
    driver = create_driver()
    driver.get(base_url+'/en/mmorpg/encyclopedia/monsters')
    while pageNumber < 10:
        pageNumber += 1
        soup = BeautifulSoup(driver.page_source, 'lxml')
        tbody = soup.find('tbody')
        rows = tbody.find_all('tr')
        for row in rows:
            links = row.find_all('a')
            for link in links: 
                fullURL =  create_full_url(base_url, link['href'])
                url_queue.put(fullURL)
        driver.get(base_url+'/en/mmorpg/encyclopedia/monsters?page='+str(pageNumber))
        time.sleep(5)
    driver.quit()

def parse_ranges(soup, stat):
    result = soup.find(text=re.compile(stat))
    div = result.parent
    range = div.findChild('span')
    rangeText = str.split(range.text, sep='to')
    if len(rangeText) > 1:
        begin = ''.join(re.findall('[0-9]',rangeText[0]))
        end = ''.join(re.findall('[0-9]',rangeText[1]))
    else:
        begin = ''.join(re.findall('[0-9]',rangeText[0]))
        end = begin
    return (begin,end)

def parse_level_ranges(levels):
    if len(levels) > 1:
        begin = ''.join(re.findall('[0-9]',levels[0]))
        end = ''.join(re.findall('[0-9]',levels[1]))
    else:
        begin = ''.join(re.findall('[0-9]',levels[0]))
        end = begin
    return (begin,end)
        
def save_monster_image(imageData, imageName):
    blob_client = blob_service_client.get_blob_client(container='dofus-pics', blob=f'{imageName}.png')
    blob_client.upload_blob_from_url(imageData)

def get_monster_info(url):
    driver = create_driver()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    if soup.find('div', {'class': 'ak-404'}) == None:
        monsterImageNumber = ''.join(re.findall('[0-9]',url))
        monsterImageLink = f'https://static.ankama.com/dofus/www/game/monsters/200/{monsterImageNumber}.png'
        name = soup.find('h1', {'class': 'ak-return-link'})
        family = soup.find('div', {'class': 'col-xs-8 ak-encyclo-detail-type'})
        family = family.findChild('span', recursive=False)
        levelRange = soup.find('div', {'class': 'col-xs-4 text-right ak-encyclo-detail-level'},text=True)
        minLevel, maxLevel = parse_level_ranges(str.split(levelRange.text, sep="to"))
        minHp, maxHp = parse_ranges(soup, 'HP:')
        minAp, maxAp = parse_ranges(soup, "AP:")
        minMp, maxMp = parse_ranges(soup, "MP:")
        minEarthRes,maxEarthRes = parse_ranges(soup, "Earth:")
        minAirRes, maxAirRes = parse_ranges(soup, "Air:")
        minFireRes, maxFireRes = parse_ranges(soup, "Fire:")
        minWaterRes, maxWaterRes = parse_ranges(soup, "Water:")
        minNeutralRes, maxNeutralRes = parse_ranges(soup, "Neutral:")
        name = str.strip(name.text)
        family = family.text
        monster = Monster(name, minLevel, maxLevel, family, 
        minHp, maxHp, minAp, maxAp, minMp, maxMp, minEarthRes,
        maxEarthRes, minWaterRes, maxWaterRes, minAirRes, maxAirRes, 
        minFireRes, maxFireRes, minNeutralRes, maxNeutralRes)
        save_monster_image(monsterImageLink,name)
        driver.quit()
        return monster
    else:
        driver.quit()
        return None
    

#def write_images_to_os
#def write_monster_characterstics_to_db

#move get_links_to_Monsters into a non-blocking thread. Do same for get_link_to_items
get_link_to_monsters()
    
with futures.ThreadPoolExecutor(max_workers=1) as executer:
    
    while not url_queue.empty():
        url = url_queue.get()
        done, not_done = futures.wait(future_to_url,return_when=futures.FIRST_COMPLETED)
        future_to_url[executer.submit(get_monster_info, url)] = url
        for future in done:
           #put into database, write to file system
           monster = future.result
           if monster != None:
               pass