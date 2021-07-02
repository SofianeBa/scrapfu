import queue
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from queue import Queue
import sys
from concurrent import futures
import time

def create_driver():
    if sys.platform == 'win32':
        driver = webdriver.Chrome('.\webdriver\chromedriver.exe')
    if sys.platform == 'linux' or sys.platform == 'linux2':
        driver = webdriver.Chrome('./webdriver/chromedriver')
    return driver

base_url = "https://www.dofus.com"
url_queue = Queue(maxsize=0)
future_to_url = {}

def create_full_url(base, addition):
    return base + addition

def get_link_to_monsters():
    #need to find a better way to determine the amount of pages in the table. 
    pageNumber = 0
    driver = create_driver()
    driver.get(base_url+'/en/mmorpg/encyclopedia/monsters')
    while pageNumber < 1:
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

def scrape_monster_pages(url):
    driver = create_driver()
    driver.create_options
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    #scrape everything monster related
    driver.quit()

#def write_images_to_os
#def write_monster_characterstics_to_db

#move get_links_to_Monsters into a non-blocking thread. Do same for get_link_to_items
get_link_to_monsters()
with futures.ThreadPoolExecutor(max_workers=5) as executer:
    
    while not url_queue.empty():
        url = url_queue.get()
        done, not_done = futures.wait(future_to_url,return_when=futures.FIRST_COMPLETED)
        future_to_url[executer.submit(scrape_monster_pages, url)] = url
        for future in done:
           #put into database, write to file system
           pass