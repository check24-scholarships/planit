import sys
import requests
from bs4 import BeautifulSoup
from planit.crawler.data_formatter import DataFormatter
from typing import List
from dataclasses import dataclass


@dataclass()
class PlantEntry:
    """
    A Class representing a crawled Plant entry from Wikipedia.
    """
    common_name: str

    helps: set
    helped_by: set

    attracts: set
    repels_distracts: set
    avoid: set


# TODO: add logging
class Crawler:
    """
    The Webcrawler Class.
    """

    def __init__(self):
        self._companion_plants_url = "https://en.wikipedia.org/wiki/List_of_companion_plants"
        self._aster_family_plants = "https://www.britannica.com/topic/list-of-plants-in-the-family-Asteraceae-2040400"
        self._aromatic_plants = "https://www.saussurea-costus.com/list-of-medicinal-and-aromatic-plants/"
        self._fruit_trees = "https://en.wikipedia.org/wiki/Fruit_tree"
        self._allium_family_plants = "http://www.theplantlist.org/browse/A/Amaryllidaceae/Allium/"
        self._vegetable_url = "https://simple.wikipedia.org/wiki/List_of_vegetables"
        self._formatter = DataFormatter()

    def _get_soup(self, url: str) -> BeautifulSoup:
        """
        send a GET requests to a website and return a BeautifulSoup Object created with the response.
        """
        try:
            r = requests.get(url, headers={
                "user-agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +https://www.google.com/bot.html)"
            })
        except requests.exceptions.ConnectionError:
            # TODO: handle exception
            sys.exit(1)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup

    def crawl_companion_plants(self) -> List[PlantEntry]:
        """
        crawls all plant tables and returns a list consisting of PlantEntry Objects.
        """
        entries = []
        soup = self._get_soup(self._companion_plants_url)
        for table in soup.find_all("tbody")[:5]:  # The 5 first tables are the only ones we need.
            for row in table.find_all("tr")[2:]:  # skip the header rows.
                # [:-1] skips the 'Comments' column.
                entries.append(self._formatter.format_columns(row.find_all("td")[:-1]))
        # the columns are empty and need to be skipped if the header table row repeats itself.
        return [PlantEntry(*entry) for entry in entries if entry]

    def get_nightshades(self) -> set:
        nightshades = {
            "ashwagandha", "pepper", "tomato", "cape gooseberry", "cocona", "eggplant", "garden huckleberry",
            "goji berries", "kutjera", "naranjillas", "Paprika", "pepinos", "pimentos", "potatoes",
            "tamarillos", "atomatillos", "tomatoes"
        }
        return nightshades

    def crawl_aster_family_plants(self) -> set:
        soup = self._get_soup(self._aster_family_plants)
        aster_flowers = {flower.text.lower() for flower in soup.find_all("a", attrs={"class": "md-crosslink"})[12:]}
        return aster_flowers

    def crawl_aromatic_plants(self) -> set:
        soup = self._get_soup(self._aromatic_plants)
        aromatic_plants = {
            aromatic_plant.find_all("td")[1].text.strip(". ").lower()
            for aromatic_plant in soup.find_all("tr")
            if aromatic_plant.text
        }
        return aromatic_plants

    def crawl_fruit_trees(self) -> set:
        soup = self._get_soup(self._fruit_trees)
        fruit_trees = {fruit_tree.text.strip().lower() for fruit_tree in soup.find_all("ul")[1].find_all("a")}
        return fruit_trees

    def get_verticillium_susceptible_species(self) -> set:
        # pdf = "https://depts.washington.edu/hortlib/resources/ucdavis_verticillium.pdf"
        verticillium_susceptible_species = {
            "Maple", "Box elder", "Tree-of - heaven", "Pecan", "Catalpa", "Carob", "Redbud", "Camphor tree",
            "Yellow wood", "Carrotwood", "Persimmon", "Oleaster,  Russian olive", "Weeping fig", "Indian laurel", "Ash",
            "Golden rain tree", "Tulip tree", "Southern magnolia", "Black gum,  pepperidge", "Olive", "Avocado",
            "Chinese pistache", "Pistache", "Almond", "apricot", "cherry", "peach", "Black locust",
            "California pepper  tree", "Brazilian pepper  tree", "Elm", "plum", "prune",

            "Barberry", "Trumpet creeper", "Pepper", "Ice plant", "Spotted rock rose", "Rock rose",
            "Orchid-spot rock rose", "Smoke tree", "Hopseed  bush", "Heather", "Flannel bush", "Fuchsia", "Hebe",
            "Hebe", "Hebe", "Angel wing jasmine", "Prim rose jasmine", "Ice plant", "Privet", "Sacred bamboo",
            "Guayule", "Indian hawthorn", "Yeddo hawthorn", "Lemonade berry", "Sumac", "Currant", "gooseberry", "Rose",
            "Rosemary", "Taylor blackberry", "Red raspberry", "Black raspberry", "Thimbleberry", "Dewberry",
            "Blackberry,  brambles", "Elderberry", "Lilac", "Viburnum", "wayfaring-tree",

            "Peanut", "Horseradish", "Rutabaga", "Cabbage", "Brussels sprouts", "Pepper", "Safflower", "Hemp",
            "Watermelon", "citron", "Cantaloupe", "honey dew", "Cucumber", "Pumpkin", "Strawberry", "Cotton", "Okra",
            "Tomato", "Mint", "Radish", "Rhubarb", "Castor bean", "Eggplant", "Potato", "Spinach",
            "Yard-long bean", "Cowpea", "muskmelon", "Persian melon",

            "Abutilon", "Snapdragon", "Udo", "American spikenard", "Aster", "Belladonna", "Slipperwort",
            "Poppy-mallow", "China aster", "Bellflower", "Cockscomb", "Sweet sultan", "Marguerite",
            "Italian chrysanthemum", "Shasta daisy", "Chrysanthemum", "Clarkia", "Tickseed", "Dahlia",
            "Rocket larkspur", "Foxglove", "Cape  marigold", "California poppy", "Transvaal daisy", "Strawflower",
            "Heliotrope", "Garden balsam", "Sweet pea", "Gayfeather", "Lobelia", "Stock", "Peony", "Oriental poppy",
            "Pelargonium", "Geranium", "Petunia", "Phlox", "Alkekengi", "Chinese lantern plant", "Polemonium", "Pyrola",
            "Mignonette",

            "Black-eyed susan", "Painted tongue", "Mealy-cup sage", "Sage", "Blue sage", "Butterfly flower",
            "Florists' cineraria", "Namaqualand daisy",

            "Rough pigweed", "Oxeye daisy", "Wild bergamot", "American ginseng", "Groundsel", "London rocket",
            "Carolina horsenettle", "White horsenettle", "Black nightshade", "Hairy nightshade", "Dandelion",
        }
        return {vss.lower() for vss in verticillium_susceptible_species}

    def crawl_allium_family_plants(self) -> set:
        soup = self._get_soup(self._allium_family_plants)
        html_allium_plants = [
            allium_part.find_all("i") + [allium_part.find("span")] for allium_part in soup.find("tbody").find_all("tr")
        ]
        allium_plants = set()
        for html_allium_plant_list in html_allium_plants:
            allium_plants.add(" ".join([allium_plant.text.lower() for allium_plant in html_allium_plant_list]))
        return allium_plants

    def crawl_vegetables(self) -> set:
        soup = self._get_soup(self._vegetable_url)
        vegetables = {vegetable.text for vegetable in soup.find("ul").find_all("a")}
        vegetables.remove("[1]")
        return vegetables
