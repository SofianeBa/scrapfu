from queue import Queue
from selenium.webdriver.chrome.options import Options
from concurrent import futures
from azure.storage.blob import BlobServiceClient
from sqlalchemy.orm import Session
from scrapers.monsterscraper import Monsterscraper
from scrapers.resourcescraper import Resourcescraper
from helpers import db
from helpers import driver as dr
import settings as config

url_queue = Queue(maxsize=0)
options = Options()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
dbsecret = db.get_conenction_string()
engine = db.create_engine(dbsecret.value)
blob_service_client = BlobServiceClient.from_connection_string(config.connect_str)
monsterscraper = Monsterscraper(blob_service_client, dr, options, url_queue)
resourcescraper = Resourcescraper(blob_service_client, dr, options, url_queue)
session = Session(engine)


def write_to_log(msg):
    with open('log.txt', 'a+') as file:
        file.write(msg)

def start_scraping(monster_url = None, resource_url = None):
    with futures.ThreadPoolExecutor(max_workers=3) as executer:
        if monster_url != None:
            future_to_url = {executer.submit(monsterscraper.get_link, monster_url, 'Monster', 92): 'URL_FUTURE'}
        if resource_url !=None:
            future_to_url = {executer.submit(resourcescraper.get_link, resource_url, 'Resource', 122): 'URL_FUTURE'}
        while future_to_url:
            done, not_done = futures.wait(future_to_url,return_when=futures.FIRST_COMPLETED)
            while not url_queue.empty():
                url_dict = url_queue.get()
                url = next(iter(url_dict))
                tag = url_dict[url]
                write_to_log(f'scraping: {url}\n')
                if tag == 'Monster':
                    future_to_url[executer.submit(monsterscraper.get_monster_info, url)] = url
                elif tag == "Resource":
                    future_to_url[executer.submit(resourcescraper.get_resource_info, url)] = url
            for future in done:
                data = future.result()
                if future_to_url[future] == 'URL_FUTURE':
                    write_to_log(f'{data}\n')
                if data == None:
                    write_to_log(f'Nothing to scrape: {future_to_url[future]}\n')
                if data != None and future_to_url[future] != 'URL_FUTURE':
                    #put into database
                    try:
                        session.add(data)
                        session.commit()
                    except Exception as e:
                        print(e)
                        write_to_log(f'failed to commit data: rolling back session for url: {future_to_url[future]}\n')
                        session.rollback()
                    write_to_log(f'scraped: {future_to_url[future]}\n')
                del future_to_url[future]

#start_scraping(monster_url='/en/mmorpg/encyclopedia/monsters?page=')
start_scraping(resource_url='/en/mmorpg/encyclopedia/resources?page=')
