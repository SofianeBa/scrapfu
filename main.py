from queue import Queue
from selenium.webdriver.chrome.options import Options
from concurrent import futures
import time
from azure.storage.blob import BlobServiceClient
from sqlalchemy.orm import Session
from scrapers.monsterscraper import Monsterscraper
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

with futures.ThreadPoolExecutor(max_workers=3) as executer:
    session = Session(engine)
    scraping_future = executer.submit(monsterscraper.get_link_to_monsters)
    future_to_url = {scraping_future: 'MONSTER_URL_FUTURE'}
    file = open('log.txt','a+')
    while future_to_url:
        done, not_done = futures.wait(future_to_url,return_when=futures.FIRST_COMPLETED)
        while not url_queue.empty() or scraping_future.running:
            try:
                url = url_queue.get()
            except ValueError:
                file.write('queue is empty, waiting for more scraped URLs\n')
                time.sleep(2)
            file.write(f'scraping: {url}\n')
            future_to_url[executer.submit(monsterscraper.get_monster_info, url)] = url
        for future in done:
            data = future.result()
            if future_to_url[future] == 'MONSTER_URL_FUTURE':
                file.write(f'{data}\n')
            if data != None and future_to_url[future] != 'MONSTER_URL_FUTURE':
                file.write(f'{future_to_url[future]}\n')
                #put into database
                session.add(data)
                session.commit()
            del future_to_url[future]
        file.close()