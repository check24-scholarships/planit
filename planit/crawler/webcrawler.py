import requests
from bs4 import BeautifulSoup
import re
from typing import List


class PlantEntry:
    """
    A Class representing a crawled Plant entry from Wikipedia.
    """
    def __init__(self, common_name: str, scientific_name: str, helps: str, helped_by: str, attracts: str,
                 repels_distracts: str, avoid: str):
        self.common_name = common_name
        self.scientific_name = scientific_name
        self.helps = helps
        self.helped_by = helped_by
        self.attracts = attracts
        self.repels_distracts = repels_distracts
        self.avoid = avoid


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
                columns = self._get_formated_text_from_columns(row.find_all("td")[:-1])  # skip the 'Comments' column.
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

    def _get_formated_text_from_columns(self, columns: list) -> list:
        """
        returns the columns list but with formatted text instead of html code.
        The regular expression removes square brackets and their contents (Wikipedia footnotes).
        """
        return [re.sub(r"\[(.*?)\]", "", value.text).strip() for value in columns]
