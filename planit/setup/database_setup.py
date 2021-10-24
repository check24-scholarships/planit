from planit.model import *
from planit.crawler.webcrawler import Crawler


def create_db_file():
    crawler = Crawler()
    plants = crawler.crawl_companion_plants()
    for plant in plants:
        add_plant(plant.common_name, plant.common_name)

    for plant in plants:
        for help_plant in plant.helps.union(plant.helped_by):
            add_symbiosis_score(help_plant, plant.common_name, 1)


if __name__ == '__main__':
    create_db_file()
