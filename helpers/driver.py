import sys
from selenium import webdriver

def create_driver(options):
    if sys.platform == 'win32':
        driver = webdriver.Chrome('.\webdriver\chromedriver.exe', options=options)  
    if sys.platform == 'linux' or sys.platform == 'linux2':
        driver = webdriver.Chrome('./webdriver/chromedriver', options=options)
    return driver