[![wakatime](https://wakatime.com/badge/github/cjw21824/scrapus.svg)](https://wakatime.com/badge/github/cjw21824/scrapus)

## <u>Scrapus</u>

**Goal of Scrapus:** gather all of the 'clean' entries in Dofus' encyclopedia. It ignores empty items that go to 404 pages, and items that have recipes or relationships to non-existent items (also to 404 pages). Although this would serve as a poor replacement for the information currently at dofus.com, it will eventually be used in a discord game similar to PokeTwo. To use this information in a game (discord bot), I'll need the information to be complete.

**Current Architecture:** I'm using selenium's chromium webdriver to scrape the pages. This is extremely slow, but seems to be the only way to bypass Cloudflare's bot detection engine. I tried using the requests library, or even selenium headless, but each one was flagged. I'm using psycopg2 and sqlalchemy to dump all of the information in a PostgreSQL DB. Using a relational database has proven to be a bit of a chore, and scraping things in order seems to be the best way to avoid any relationship constraint issues. The binary files (images) are pumped into a blob storage account in Azure. I'm hoping to expand this to be configurable for those who want to store them locally or in another provider's managed storage service.

### But  Why?

I really enjoy Dofus as a game. I think the artwork is awesome and the gameplay is a great! I want to adapt some of that awesomeness into a discord bot/game. Before I can do that though I need to gather as much actual game material as I can. I decided to do this in Python because I enjoy the language and want to learn it through actual projects that do more than , "hello world" or building a calculator. I chose Postgres because that's what I'm familiar with and I also want to learn more about it. That being said, this is not a best-practice or even a good program. It's functional and will be bettered in time. Hopefully this serves as a learning experience for myself and those who stumble upon this project. 



### **Current Gathering Capabilities:** 

- [x] Resources
  - [x] Basic Info (id, name, type, level, description)
- [x] Monsters
  - [x] Basic Info (id, name, family, level)
  - [x] basic stats (ap,mp,hp)
  - [x] resistances
  - [ ] Areas
  - [x] Drops (resources)
- [x] Professions
  - [x] Basic Info (id, name, description)
  - [x] Recipes
- [x] Recipes
  - [x] Basic Info (id, level)
  - [x] ingredients
- [x] Equipment
  - [x] Basic Info(id, name, type, level, description)
  - [x] Effects
    - [x] Basic Effects (damage, crit, resistance, etc)
    - [ ] Class Effects (i.e. cra spells +1 range, no LoS)
  - [ ] Conditions (i.e. strength > 300)
  - [x] Recipe
- [x] Weapons
  - [x] Basic Info()
  - [x] Effects
    - [x] Basic Effects (damage, crit, resistance, etc)
    - [ ] Class Effects
  - [ ] Conditions
  - [ ] Characteristics
  - [x] Recipe
- [ ] Pets
  - [ ] Basic Info
  - [ ] Stats
- [ ] Mounts
  - [ ] Basic Info
  - [ ] Stats
- [ ] Ceremonial Items
  - [ ] Basic Info
