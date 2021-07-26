import requests
from bs4 import BeautifulSoup
from data_formatter import format_columns
from typing import List
from dataclasses import dataclass


@dataclass()
class PlantEntry:
    """
    A Class representing a crawled Plant entry from Wikipedia.
    """
    common_name: str
    scientific_name: str

    helps: set
    helped_by: set

    attracts: set
    repels_distracts: set
    avoid: set


class Crawler:
    """
    The Webcrawler Class.
    """
    def __init__(self):
        self._url = "https://en.wikipedia.org/wiki/List_of_companion_plants"

    def crawl_all_plant_tables(self) -> List[PlantEntry]:
        """
        crawls all plant tables and returns a list consisting of PlantEntry Objects.
        """
        entries = []
        soup = self._get_soup()
        for table in soup.find_all("tbody")[:5]:  # The 5 first tables are the only ones we need.
            for row in table.find_all("tr")[2:]:  # skip the header rows.
                # [:-1] skips the 'Comments' column.
                columns = format_columns(row.find_all("td")[:-1])
                # the columns are empty and need to be skipped if the header table row repeats itself.
                if not columns:
                    continue
                entries.append(PlantEntry(*columns))
        return entries

    def _get_soup(self) -> BeautifulSoup:
        """
        send a GET requests to the website and return a BeautifulSoup Object created with the response.
        """
        r = requests.get(self._url)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup


if __name__ == '__main__':
    crawler = Crawler()
    for entry in crawler.crawl_all_plant_tables():
        print(entry.common_name + ": " + str(entry.helped_by))
