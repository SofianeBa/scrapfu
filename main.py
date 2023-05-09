from queue import Queue
from selenium.webdriver.chrome.options import Options
from concurrent import futures
from scrapers.consumablescraper import Consumablescraper
from scrapers.monsterscraper import Monsterscraper
from scrapers.resourcescraper import Resourcescraper
from scrapers.professionscraper import Professionscraper
from scrapers.equipmentscraper import Equipmentscraper
from scrapers.weaponscraper import Weaponscraper
from sqlalchemy.ext.declarative import declarative_base
from helpers import db
from helpers import driver as dr
#import settings as config

Session = db.create_session()
session = Session()
url_queue = Queue(maxsize=0)
options = Options()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
#blob_service_client = BlobServiceClient.from_connection_string(config.connect_str)
monsterscraper = Monsterscraper(dr, options, url_queue)
resourcescraper = Resourcescraper(dr, options, url_queue)
professionscraper = Professionscraper(dr, options, url_queue)
equipmentscraper = Equipmentscraper(dr, options, url_queue)
weaponscraper = Weaponscraper(dr, options, url_queue)
consumablescraper = Consumablescraper(dr, options, url_queue)


def write_to_log(file_name, msg):
    with open(file_name, 'a+') as file:
        file.write(msg)

def start_scraping(log_file_name,monster_url = None, resource_url = None, profession_url = None, equipment_url = None, weapon_url = None, consumable_url = None):
    with futures.ThreadPoolExecutor(max_workers=6) as executer:
        if monster_url != None:
            future_to_url = {executer.submit(monsterscraper.get_link, monster_url, 'Monster', 1, 1): 'URL_FUTURE'}
        if resource_url !=None:
            future_to_url = {executer.submit(resourcescraper.get_link, resource_url, 'Resource', 1, 1): 'URL_FUTURE'}
        if profession_url !=None:
            future_to_url = {executer.submit(professionscraper.get_link, profession_url, 'Profession', 1, 7): 'URL_FUTURE'}
        if equipment_url !=None:
            future_to_url = {executer.submit(equipmentscraper.get_link, equipment_url, 'Equipment', 1, 80): 'URL_FUTURE'}
        if weapon_url !=None:
            future_to_url = {executer.submit(weaponscraper.get_link, weapon_url, 'Weapon', 1, 1): 'URL_FUTURE'}
        if consumable_url !=None:
            future_to_url = {executer.submit(consumablescraper.get_link, consumable_url, 'Consumable', 1, 13): 'URL_FUTURE'}

        while future_to_url:
            remember_done = []
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
                elif tag == "Consumable":
                    future_to_url[executer.submit(consumablescraper.get_consumable_info, url)] = url
            for future in done:
                data = future.result()
                if data != None and future_to_url[future] != 'URL_FUTURE':
                    #put into database
                    try:
                        session.add(data)
                        session.commit()
                        if hasattr(data,"remember"):
                            for truc in data.remember:
                                remember_done.append(truc)
                        write_to_log(log_file_name, f'successfully scraped: {future_to_url[future]}\n')
                    except Exception as e:
                        write_to_log(log_file_name,f'failed to commit data: rolling back session for url: {future_to_url[future]}\n')
                        write_to_log(log_file_name,f'{e}'+'\n')
                        session.rollback()
                del future_to_url[future]
            for to_add in remember_done:
                try:
                    session.add(to_add)
                    session.commit()
                    write_to_log(log_file_name, f'successfully scraped the Monster_Weapon \n')
                except Exception as e:
                        write_to_log(log_file_name,f'failed to commit data: rolling back session for Monster_Weapon\n')
                        write_to_log(log_file_name,f'{e}'+'\n')
                        session.rollback()



def start_scraping_resources(log_file_name, resource_url = None):
    with futures.ThreadPoolExecutor(max_workers=6) as executer:
        if resource_url !=None:
            future_to_url = {executer.submit(resourcescraper.get_link, resource_url, 'Resource', 61, 79): 'URL_FUTURE'}

        while future_to_url:
            done, not_done = futures.wait(future_to_url,return_when=futures.FIRST_COMPLETED)
            while not url_queue.empty():
                url_dict = url_queue.get()
                url = next(iter(url_dict))
                tag = url_dict[url]
                future_to_url[executer.submit(resourcescraper.get_resource_info, url)] = url
            for future in done:
                data = (future.result())
                if data != None and future_to_url[future] != 'URL_FUTURE':
                    #put into database
                    try:
                        for truc in data:
                            if(type(truc) is list):
                                for monster in truc:
                                    session.add(monster)
                                session.commit()
                            else:
                                session.add(truc)
                                session.commit()
                        write_to_log(log_file_name, f'successfully scraped: {future_to_url[future]}\n')
                    except Exception as e:
                        write_to_log(log_file_name,f'failed to commit data: rolling back session for url: {future_to_url[future]}\n')
                        write_to_log(log_file_name,f'{e}'+'\n')
                        session.rollback()
                del future_to_url[future]

def scrape_monsters():
    start_scraping('monster_log.txt', monster_url='/fr/mmorpg/encyclopedie/monstres?page=')
    for url, reason in monsterscraper.failed_urls.items():
        write_to_log('monster_log.txt', f'{url}: {reason}\n')
    for i in range(0,5):
        write_to_log('monster_log.txt', '\n')
    for url, reason in monsterscraper.skipped_urls.items():
        write_to_log('monster_log.txt', f'{url}: {reason}\n')

def scrape_resources():
    start_scraping_resources('resource_log.txt',resource_url='/fr/mmorpg/encyclopedie/ressources?display=table&page=')
    #ressources?text=&level_min=0&level_max=230&display=table&page=
    for url, reason in resourcescraper.failed_urls.items():
        write_to_log('resource_log.txt', f'{url}: {reason}\n')
    for i in range(0,5):
        write_to_log('resource_log.txt', '\n')
    for url, reason in resourcescraper.skipped_urls.items():
        write_to_log('resource_log.txt', f'{url}: {reason}\n')

def scrape_professions():
    start_scraping(profession_url='/fr/mmorpg/encyclopedia/professions?page=')

def scrape_equipment():
    start_scraping('equipment_log.txt',equipment_url='/fr/mmorpg/encyclopedie/armures?display=table&sort=3A&page=')
    for url, reason in equipmentscraper.failed_urls.items():
        write_to_log('equipment_log.txt', f'{url}: {reason}\n')
    for i in range(0,5):
        write_to_log('equipment_log.txt', '\n')
    for url, reason in equipmentscraper.skipped_urls.items():
        write_to_log('equipment_log.txt', f'{url}: {reason}\n')

def scrape_weapons():
    start_scraping('weapon_log.txt',weapon_url='/fr/mmorpg/encyclopedie/armes?text=&level_min=0&level_max=230&rarities%5B0%5D=7&display=table&page=')
    for url, reason in weaponscraper.failed_urls.items():
        write_to_log('weapon_log.txt', f'{url}: {reason}\n')
    for i in range(0,5):
        write_to_log('weapon_log.txt', '\n')
    for url, reason in weaponscraper.skipped_urls.items():
        write_to_log('weapon_log.txt', f'{url}: {reason}\n')

def scrape_consumables():
    start_scraping('consumable_log.txt', consumable_url='/fr/mmorpg/encyclopedie/consommables?page=')
    for url, reason in consumablescraper.failed_urls.items():
        write_to_log('consumable_log.txt', f'{url}: {reason}\n')
    for i in range(0,5):
        write_to_log('consumable_log.txt', '\n')
    for url, reason in consumablescraper.skipped_urls.items():
        write_to_log('consumable_log.txt', f'{url}: {reason}\n')



def test_resource(my_url):
    try:
        resource,monsters = resourcescraper.get_resource_info(my_url)
        session.add(resource)
        session.commit()
        for monster in monsters:
            session.add(monster)
        session.commit()
        write_to_log('resource_log.txt', f'successfully scraped: '+my_url+'\n')
    except Exception as e:
        write_to_log('resource_log.txt',f'failed to commit data: rolling back session for url: '+my_url+'\n')
        write_to_log('resource_log.txt',f'{e}'+'\n')
        session.rollback()

def test_equipment(my_url):
    try:
        session.add(equipmentscraper.get_equipment_info(my_url))
        session.commit()
        write_to_log('equipment_log.txt', f'successfully scraped: '+my_url+'\n')
    except Exception as e:
        write_to_log('equipment_log.txt',f'failed to commit data: rolling back session for url: '+my_url+'\n')
        write_to_log('equipment_log.txt',f'{e}'+'\n')
        session.rollback()

def test_weapon(my_url):
    try:
        weapon = weaponscraper.get_weapon_info(my_url)
        session.add(weapon)
        session.commit()
        for truc in weapon.remember:
            session.add(truc)
            session.commit()
        write_to_log('weapon_log.txt', f'successfully scraped: '+my_url+'\n')
    except Exception as e:
        write_to_log('weapon_log.txt',f'failed to commit data: rolling back session for url: '+my_url+'\n')
        write_to_log('weapon_log.txt',f'{e}'+'\n')
        session.rollback()

def test_monster(my_url):
    try:
        monster = monsterscraper.get_monster_info(my_url)
        session.add(monster)
        session.commit()
        write_to_log('monster_log.txt', f'successfully scraped: '+my_url+'\n')
    except Exception as e:
        write_to_log('monster_log.txt',f'failed to commit data: rolling back session for url: '+my_url+'\n')
        write_to_log('monster_log.txt',f'{e}'+'\n')
        session.rollback()

#Production

#Done Scrapping scrape_monsters() # - Ready - Sorts non implémentés / Inutiles (peut-être un jour si Wakfu améliore son Encyclopédie)
#Manque monster_harvest

#Done Scrapping scrape_resources() # - Ready
#Done Scrapping scrape_consumables() # - Ready
#Done Scrapping scrape_weapons() # - Ready

#scrape_accesories() #  -- Info : Tout ce qui est sacs etc...
#scrape_equipment() # - Ready 

#For Test purpose

#equipmentscraper.get_equipment_info("https://www.wakfu.com/fr/mmorpg/encyclopedie/armures/25572-bottes-riktus-brakmar")

#monsterscraper.get_monster_info("https://www.wakfu.com/fr/mmorpg/encyclopedie/monstres/41-boufette")

#session.add(monsterscraper.get_monster_info("https://www.wakfu.com/fr/mmorpg/encyclopedie/monstres/4-tofu"))
#session.commit()

#resourcescraper.get_resource_info("https://www.wakfu.com/fr/mmorpg/encyclopedie/ressources/29381")

#test_resource("https://www.wakfu.com/fr/mmorpg/encyclopedie/ressources/29381-trophee-dh")
#test_weapon("https://www.wakfu.com/fr/mmorpg/encyclopedie/armes/29485-sceptre-dernier-repos")
#test_weapon("https://www.wakfu.com/fr/mmorpg/encyclopedie/armes/28194-racine-heptie")
#test_weapon("https://www.wakfu.com/fr/mmorpg/encyclopedie/armes/21474-racine-heptie")
#test("https://www.wakfu.com/fr/mmorpg/encyclopedie/ressources/19494")
#resourcescraper.get_resource_info("https://www.wakfu.com/fr/mmorpg/encyclopedie/ressources/28345-pointe-sumorse")
#resourcescraper.get_resource_info("https://www.wakfu.com/fr/mmorpg/encyclopedie/ressources/27823-semence-cagnardeur")
#resourcescraper.get_resource_info("https://www.wakfu.com/fr/mmorpg/encyclopedie/ressources/2702-bec-piou")



#Boubou... #test_equipment("https://www.wakfu.com/fr/mmorpg/encyclopedie/armures/9927")


#Problème : Sceau du maître truc
#Bas de laine (id : 20604) nécessaire pour le craft, mais c'est un accessoire, hors pas d'accessory_id dans la recipe ni dans ingredient....
