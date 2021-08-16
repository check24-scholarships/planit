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
        columns = self._remove_footnotes_and_examples(columns)
        columns = self._format_column_entry_strings(columns)
        return columns

    def _format_html_code_to_plain_text(self, columns: list) -> list:
        """
        returns the columns list but with plain text instead of html code.
        """
        return [column.text.strip() for column in columns]

    def _remove_footnotes_and_examples(self, columns: list) -> list:
        """
        The regular expression removes square brackets and their contents (Wikipedia footnotes) as well as regular brackets
        and their contents (Examples).
        The square brackets are replaced with a ',' because sometimes it was forgotten in the article. :(
        """
        square_brackets_pattern = re.compile(r"\[[^]]*]")
        brackets_pattern = re.compile(r"\([^)]*\)")
        return [brackets_pattern.sub("", square_brackets_pattern.sub(",", column)) for column in columns]

    def _format_column_entry_strings(self, columns: list) -> list:
        """
        formats the entries of helps, helped by, attracts ,-Repels/+distracts and avoid strings to sets.
        """
        new_columns = self._lemmatize_names(columns[:2])
        new_columns += self._split_column_entries_to_set(columns[2:])
        new_columns[2:] = self._strip_entries(new_columns[2:])
        new_columns[2:] = self._lemmatize_sets(new_columns[2:])
        new_columns = self._format_lemmatized_words(new_columns)
        return new_columns

    def _split_column_entries_to_set(self, columns: list) -> list:
        """
        split the column entries on the following values: ",", ";", ".", "/", "and", "or".
        return a list with sets containing the seperated column entries.
        """
        split_pattern = re.compile(r"[,;.&\/]\s?|\s?\band\s|\sor\s")
        new_columns = []
        for column in columns:
            if not column:
                new_columns.append(set())
                continue
            new_columns.append(set(split_pattern.split(column)))
        return new_columns

    def _strip_entries(self, columns: list) -> list:
        """
        returns a list of sets witch contain stripped values. if the value is "" it is skipped.
        """
        return [set(entry.strip('-" ') for entry in column if entry) for column in columns]

    def _lemmatize_names(self, names: list) -> list:
        """
        calls _lemmatize_word method for the two columns (common name, scientific name).
        """
        return [self._lemmatize_word(name) for name in names]

    def _lemmatize_sets(self, columns: list) -> list:
        """
        calls _lemmatize_word for each word in a list of sets (Helps, Helped by, Attracts, -Repels/+distracts, Avoid)
        """
        return [set(self._lemmatize_word(entry) for entry in column) for column in columns]

    def _lemmatize_word(self, word: str) -> str:
        """
        turns nouns singular
        """
        return " ".join([word.lemma_ if word.pos_ == "NOUN" else word.text for word in self._nlp(word.lower())])

    def _format_lemmatized_words(self, columns: list) -> list:
        """
        format the strings returned by _lemmatize_word().
        """
        sub_pattern = re.compile(r" ([-/]|\.$|'s |[.,] ) ?")
        # noinspection PyTypeChecker
        return [sub_pattern.sub(r"\1", column) for column in columns[:2]] + \
               [set(sub_pattern.sub(r"\1", entry) for entry in column if entry) for column in columns[2:]]
