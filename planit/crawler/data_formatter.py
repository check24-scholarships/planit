import re
from typing import Union
import spacy
from concurrent.futures import ThreadPoolExecutor
import time


class DataFormatter:
    def __init__(self):
        self._nlp = spacy.load("en_core_web_sm")

    def format_columns(self, columns: list) -> list:
        """
        applies all format methods on the columns list.
        """
        columns = self._format_html_code_to_plain_text(columns)
        columns = self._format_column_entry_strings(columns)
        return columns

    def _format_html_code_to_plain_text(self, columns: list) -> list:
        """
        returns the columns list but with plain text instead of html code.
        """
        return [self._remove_footnotes_and_examples(column.text.strip()) for column in columns if column]

    def _format_column_entry(self, column_entry: str) -> str:
        """
        apply text formatting with string.
        """
        column_entry = self._remove_footnotes_and_examples(column_entry)
        return column_entry

    def _remove_footnotes_and_examples(self, column_entry: str) -> str:
        """
        The regular expression removes square brackets and their contents (Wikipedia footnotes) as well as regular brackets
        and their contents (Examples).
        """
        # maybe ...(re.sub(r"\[(.*?)]", ",", column_entry)) check example in wiki: Nasturtium
        return re.sub(r"\((.*?)\)", "", re.sub(r"\[(.*?)]", "", column_entry))

    def _format_column_entry_strings(self, columns: list) -> list:
        """
        formats the entries of helps, helped by, attracts ,-Repels/+distracts and avoid strings to sets.
        """
        new_columns = self._lemmatize_names(columns[:2])
        for column in columns[2:]:
            new_columns.append(self._split_column(column))
        return new_columns

    def _lemmatize_names(self, names: list) -> list:
        """
        calls the _lemmatize_name for the two columns (common name and scientific name).
        """
        with ThreadPoolExecutor(max_workers=2) as executor:
            running_threads = [executor.submit(self._lemmatize_name, name) for name in names]
        return [thread.result() for thread in running_threads]

    def _lemmatize_name(self, name: str) -> str:
        """
        turns the nouns singular
        """
        print(name)
        return " ".join([word.lemma_ for word in self._nlp(name)]).replace(" , ", ", ")

    def _split_column(self, column: str) -> Union[set, None]:
        """
        splits the column string on multiple different separators.
        """
        # If an empty string is passed return None
        if not column:
            return None
        separators = [" and ", " or ", ";", "/", ". "]
        for separator in separators:
            column = column.replace(separator, ",")
        return self._strip_entries(column.split(","))

    def _strip_entries(self, entry: list) -> set:
        """
        strips all list entries and returns the entries as a set.
        """
        return set(entry.strip().rstrip(".").strip("-") for entry in entry)
