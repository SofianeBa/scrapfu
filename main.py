from bs4 import BeautifulSoup
from queue import Queue
from selenium.webdriver.chrome.options import Options
from concurrent import futures
import time
import os
from azure.storage.blob import BlobServiceClient
from sqlalchemy.orm import Session
from scrapers.monsterscraper import Monsterscraper
from helpers import db
from helpers import driver as dr

base_url = "https://www.dofus.com"
url_queue = Queue(maxsize=0)
options = Options()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
dbsecret = db.get_conenction_string()
engine = db.create_engine(dbsecret.value)
try:
    connect_str = os.getenv('AZ_Connection_String')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
except os.error: 
    print('Error! Please check if the environment variable has been set.')
monsterscraper = Monsterscraper(blob_service_client, dr, options)

def create_full_url(base, addition):
    return base + addition

def get_link_to_monsters():
    #need to find a better way to determine the amount of pages in the table. 
    pageNumber = 91
    driver = dr.create_driver(options)
    driver.get(base_url+'/en/mmorpg/encyclopedia/monsters')
    while pageNumber < 92:
        soup = BeautifulSoup(driver.page_source, 'lxml')
        tbody = soup.find('tbody')
        rows = tbody.find_all('tr')
        for row in rows:
            links = row.find_all('a')
            for link in links: 
                fullURL =  create_full_url(base_url, link['href'])
                url_queue.put(fullURL)
        pageNumber += 1
        driver.get(base_url+'/en/mmorpg/encyclopedia/monsters?page='+str(pageNumber))
        time.sleep(5)
    driver.quit()
    return "Done scraping monster urls"

with futures.ThreadPoolExecutor(max_workers=3) as executer:
    session = Session(engine)
    future_to_url = {executer.submit(get_link_to_monsters): 'MONSTER_URL_FUTURE'}
    while future_to_url:
        done, not_done = futures.wait(future_to_url,return_when=futures.FIRST_COMPLETED)
        while not url_queue.empty():
            url = url_queue.get()
            future_to_url[executer.submit(monsterscraper.get_monster_info, url)] = url
        for future in done:
            data = future.result()
            if future_to_url[future] == 'MONSTER_URL_FUTURE':
                with open('log.txt', 'a+') as file:  # Use file to refer to the file object
                    file.write(data)
            if data != None and future_to_url[future] != 'MONSTER_URL_FUTURE':
                with open('log.txt', 'a+') as file:  # Use file to refer to the file object
                    file.write(future_to_url[future])
                #put into database
                session.add(data)
                session.commit()
            del future_to_url[future]