import queue
from selenium import webdriver
from bs4 import BeautifulSoup
from queue import Queue
import time

base_url = "https://www.dofus.com"
driver = webdriver.Chrome('./chromedriver')
url_queue = Queue(maxsize=0)

def create_full_url(base, addition):
    return base + addition


def get_link_to_monsters(driver):
    #need to find a better way to determine the amount of pages in the table. 
    pageNumber = 0

    driver.get(base_url+'/en/mmorpg/encyclopedia/monsters')
    while pageNumber < 84:
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


get_link_to_monsters(driver)

while not url_queue.empty():
    print(url_queue.get())