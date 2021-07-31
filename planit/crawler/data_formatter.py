import re
import spacy


class DataFormatter:
    def __init__(self):
        # TODO: include in requirements.txt
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
        return [self._remove_footnotes_and_examples(column.text.strip()) for column in columns]

    def _remove_footnotes_and_examples(self, column_entry: str) -> str:
        """
        The regular expression removes square brackets and their contents (Wikipedia footnotes) as well as regular brackets
        and their contents (Examples).
        The square brackets are replaced with a ',' because sometimes it was forgotten in the article. :(
        """
        return re.sub(r"\((.*?)\)", "", re.sub(r"\[(.*?)]", ",", column_entry))

    def _format_column_entry_strings(self, columns: list) -> list:
        """
        formats the entries of helps, helped by, attracts ,-Repels/+distracts and avoid strings to sets.
        """
        new_columns = self._lemmatize_names(columns[:2])
        for column in columns[2:]:
            new_columns.append(self._split_column_entries_to_sets(column))
        new_columns[2:] = self._lemmatize_sets(new_columns[2:])
        return new_columns

    def _lemmatize_names(self, names: list) -> list:
        """
        calls _lemmatize_word method for the two columns (common name, scientific name).
        """
        return [self._lemmatize_word(name) for name in names]

    def _lemmatize_sets(self, columns: list) -> list:
        """
        calls _lemmatize_word for each word in a list of sets (Helps, Helped by, Attracts, -Repels/+distracts, Avoid)
        """
        # if the column value is None and therefore not a set it doesn't call _lemmatize_word() but instead just inserts
        # None in the final list.
        return [set(self._lemmatize_word(entry) for entry in column) for column in columns]

    def _lemmatize_word(self, word: str) -> str:
        """
        turns nouns singular
        """
        return self._replace_joined_punctuation(
            " ".join([word.lemma_ if word.pos_ == "NOUN" else word.text for word in self._nlp(word.lower())]))

    def _replace_joined_punctuation(self, word: str) -> str:
        """
        fixes the joined string that spacy returns.
        """
        return word.replace(" , ", ", ")\
            .replace(" 's ", "'s ")\
            .replace(" . ", ". ")\
            .replace(" .", ".")\
            .replace(" - ", "-")

    # TODO: maybe only return empty set if column is empty?
    def _split_column_entries_to_sets(self, column: str) -> set:
        """
        splits the column string on multiple different separators and return them as a set or return None if column empty.
        """
        # If an empty string is passed return None
        if not column:
            return set()
        separators = [" and ", " or ", ";", "/", ". "]
        for separator in separators:
            column = column.replace(separator, ",")
        return self._strip_entries(column.split(","))

    def _strip_entries(self, entries: list) -> set:
        """
        strips all list entries and returns the entries as a set. Removes all empty strings as well.
        """
        return set(entry.strip().rstrip(".").strip("-").strip('"') for entry in entries if entry)
