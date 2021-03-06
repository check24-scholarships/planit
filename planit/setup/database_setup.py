from planit.plant_data import *
from planit.crawler.webcrawler import Crawler


def create_db_file():
    crawler = Crawler()
    plants = crawler.crawl_companion_plants()
    overwrite('plants')
    overwrite('symbioses')
    for plant in plants:
        add_plant(plant.common_name)

    for plant in plants:
        for help_plant in plant.helps:
            add_symbiosis_score(plant.common_name, help_plant, 1)

        for helped_by_plant in plant.helped_by:
            add_symbiosis_score(helped_by_plant, plant.common_name, 1)

        for avoid_plant in plant.avoid:
            add_symbiosis_score(plant.common_name, avoid_plant, -1)


if __name__ == '__main__':
    create_db_file()
