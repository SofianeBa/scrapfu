import time
from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome('./chromedriver')
driver.get('https://www.dofus.com/en/mmorpg/encyclopedia/monsters')
soup = BeautifulSoup(driver.page_source)
images = soup.find_all('img')
for i in images: 
    print(i)
driver.quit()