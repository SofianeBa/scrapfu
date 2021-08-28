from queue import Queue
from selenium.webdriver.chrome.options import Options
from concurrent import futures
from azure.storage.blob import BlobServiceClient
import sqlalchemy
from scrapers.monsterscraper import Monsterscraper
from scrapers.resourcescraper import Resourcescraper
from scrapers.professionscraper import Professionscraper
from scrapers.equipmentscraper import Equipmentscraper
from scrapers.weaponscraper import Weaponscraper
from helpers import db
from helpers import driver as dr
import settings as config

Session = db.create_session()
session = Session()
url_queue = Queue(maxsize=0)
options = Options()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
blob_service_client = BlobServiceClient.from_connection_string(config.connect_str)
monsterscraper = Monsterscraper(blob_service_client, dr, options, url_queue)
resourcescraper = Resourcescraper(blob_service_client, dr, options, url_queue)
professionscraper = Professionscraper(blob_service_client, dr, options, url_queue)
equipmentscraper = Equipmentscraper(blob_service_client, dr, options, url_queue)
weaponscraper = Weaponscraper(blob_service_client, dr, options, url_queue, update = True)


def write_to_log(file_name, msg):
    with open(file_name, 'a+') as file:
        file.write(msg)

def start_scraping(log_file_name,monster_url = None, resource_url = None, profession_url = None, equipment_url = None, weapon_url = None):
    with futures.ThreadPoolExecutor(max_workers=3) as executer:
        if monster_url != None:
            future_to_url = {executer.submit(monsterscraper.get_link, monster_url, 'Monster', 92): 'URL_FUTURE'}
        if resource_url !=None:
            future_to_url = {executer.submit(resourcescraper.get_link, resource_url, 'Resource', 122): 'URL_FUTURE'}
        if profession_url !=None:
            future_to_url = {executer.submit(professionscraper.get_link, profession_url, 'Profession', 2): 'URL_FUTURE'}
        if equipment_url !=None:
            future_to_url = {executer.submit(equipmentscraper.get_link, equipment_url, 'Equipment', 101): 'URL_FUTURE'}
        if weapon_url !=None:
            future_to_url = {executer.submit(weaponscraper.get_link, weapon_url, 'Weapon', 36): 'URL_FUTURE'}
        while future_to_url:
            done, not_done = futures.wait(future_to_url,return_when=futures.FIRST_COMPLETED)
            while not url_queue.empty():
                url_dict = url_queue.get()
                url = next(iter(url_dict))
                tag = url_dict[url]
                if tag == 'Monster':
                    future_to_url[executer.submit(monsterscraper.get_monster_info, url)] = url
                elif tag == "Resource":
                    future_to_url[executer.submit(resourcescraper.get_resource_info, url)] = url
                elif tag == "Profession":
                    future_to_url[executer.submit(professionscraper.get_profession_info, url)] = url
                elif tag == "Equipment":
                    future_to_url[executer.submit(equipmentscraper.get_equipment_info, url)] = url
                elif tag == "Weapon":
                    future_to_url[executer.submit(weaponscraper.get_weapon_info, url)] = url
            for future in done:
                data = future.result()
                if data != None and future_to_url[future] != 'URL_FUTURE':
                    #put into database
                    try:
                        session.add(data)
                        session.commit()
                        write_to_log(log_file_name, f'successfully scraped: {future_to_url[future]}\n')
                    except Exception as e:
                        write_to_log(log_file_name,f'failed to commit data: rolling back session for url: {future_to_url[future]}\n')
                        write_to_log(log_file_name,f'{e}')
                        session.rollback()
                del future_to_url[future]

def scrape_monsters():
    start_scraping('monster_log.txt', monster_url='/en/mmorpg/encyclopedia/monsters?page=')
    for url, reason in monsterscraper.failed_urls.items():
        write_to_log('monster_log.txt', f'{url}: {reason}\n')
    for i in range(0,5):
        write_to_log('monster_log.txt', '\n')
    for url, reason in monsterscraper.skipped_urls.items():
        write_to_log('monster_log.txt', f'{url}: {reason}\n')

def scrape_resources():
    start_scraping('resource_log.txt',resource_url='/en/mmorpg/encyclopedia/resources?page=')
    for url, reason in resourcescraper.failed_urls.items():
        write_to_log('resource_log.txt', f'{url}: {reason}\n')
    for i in range(0,5):
        write_to_log('resource_log.txt', '\n')
    for url, reason in resourcescraper.skipped_urls.items():
        write_to_log('resource_log.txt', f'{url}: {reason}\n')

def scrape_professions():
    start_scraping(profession_url='/en/mmorpg/encyclopedia/professions?page=')

def scrape_equipment():
    start_scraping('equipment_log.txt',equipment_url='/en/mmorpg/encyclopedia/equipment?sort=3A&page=')
    for url, reason in equipmentscraper.failed_urls.items():
        write_to_log('equipment_log.txt', f'{url}: {reason}\n')
    for i in range(0,5):
        write_to_log('equipment_log.txt', '\n')
    for url, reason in equipmentscraper.skipped_urls.items():
        write_to_log('equipment_log.txt', f'{url}: {reason}\n')

def scrape_weapons():
    start_scraping('weapon_log.txt',weapon_url='/en/mmorpg/encyclopedia/weapons?sort=3A&page=')
    for url, reason in weaponscraper.failed_urls.items():
        write_to_log('weapon_log.txt', f'{url}: {reason}\n')
    for i in range(0,5):
        write_to_log('weapon_log.txt', '\n')
    for url, reason in weaponscraper.skipped_urls.items():
        write_to_log('weapon_log.txt', f'{url}: {reason}\n')

#scrape_monsters()
#scrape_resources()
#scrape_equipment()
#scrape_weapons()
weapn = weaponscraper.get_weapon_info('https://www.dofus.com/en/mmorpg/encyclopedia/weapons/19096-forfut-hammer')