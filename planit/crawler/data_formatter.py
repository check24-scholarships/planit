import re
import spacy


class DataFormatter:
    def __init__(self):
        # TODO: include in requirements.txt
        self._nlp = spacy.load("en_core_web_sm")
        self._lemmatized_name_format_pattern = re.compile(r" (/|'s |, ) ?")
        self._square_brackets_pattern = re.compile(r"\[[^]]*]")
        self._brackets_pattern = re.compile(r"\([^)]*\)")
        self._split_pattern = re.compile(r"[,;.&\/]\s?|\s?\band\s|\sor\s")
        self._lemmatized_set_entry_format_pattern = re.compile(r" (-|'s ) ?")
        self._set_entries_to_be_deleted = {"together", "almost everything", "plant with many blossom"}
        self._set_entries_to_be_replaced = {re.compile(r".*lady bug$"): "ladybug", re.compile(r"^most "): "",
                                            re.compile(r"^such as "): "", re.compile(r"^mixture of "): "", }

    def format_columns(self, columns: list) -> list:
        """
        applies all format methods on the columns list.
        """
        columns = self._format_html_code_to_plain_text(columns)
        if not columns:
            return columns
        columns.pop(1)
        columns[0] = self._format_name(columns[0])
        columns[1:] = self._format_set_entries(columns[1:])
        return columns

    def _format_html_code_to_plain_text(self, columns: list) -> list:
        """
        returns the columns list but with plain text instead of html code.
        """
        return [column.text.strip() for column in columns]

    def _format_name(self, name: str) -> str:
        name = self._lemmatize_word(name)
        name = self._format_lemmatized_name(name)
        return name

    def _lemmatize_word(self, word: str) -> str:
        """
        turns nouns singular
        """
        return " ".join([word.lemma_ if word.pos_ == "NOUN" else word.text for word in self._nlp(word.lower())])

    def _format_lemmatized_name(self, name: str) -> str:
        return self._lemmatized_name_format_pattern.sub(r"\1", name)

    def _format_set_entries(self, columns: list) -> list:
        """
        formats the entries of helps, helped by, attracts ,-Repels/+distracts and avoid strings to sets.
        """
        columns = self._remove_footnotes_and_examples(columns)
        columns = self._split_column_entries_to_set(columns)
        columns = self._strip_set_entries(columns)
        columns = self._lemmatize_set_entries(columns)
        columns = self._format_lemmatized_set_entries(columns)
        columns = self._manually_format_set_entries(columns)
        return columns

    def _remove_footnotes_and_examples(self, columns: list) -> list:
        """
        The regular expression removes square brackets and their contents (Wikipedia footnotes) as well as regular brackets
        and their contents (Examples).
        The square brackets are replaced with a ',' because sometimes it was forgotten in the article. :(
        """
        return [self._brackets_pattern.sub(",", self._square_brackets_pattern.sub(",", column)) for column in columns]

    def _split_column_entries_to_set(self, columns: list) -> list:
        """
        split the column entries on the following values: ",", ";", ".", "/", "and", "or".
        return a list with sets containing the seperated column entries.
        """
        new_columns = []
        for column in columns:
            if not column:
                new_columns.append(set())
            else:
                new_columns.append(set(self._split_pattern.split(column)))
        return new_columns

    def _strip_set_entries(self, columns: list) -> list:
        """
        returns a list of sets witch contain stripped values. if the value is "" it is skipped.
        """
        return [set(entry.strip('-" ') for entry in column if entry) for column in columns]

    def _lemmatize_set_entries(self, columns: list) -> list:
        """
        calls _lemmatize_word for each word in a list of sets (Helps, Helped by, Attracts, -Repels/+distracts, Avoid)
        """
        return [set(self._lemmatize_word(entry) for entry in column) for column in columns]

    def _format_lemmatized_set_entries(self, columns: list) -> list:
        return [set(self._lemmatized_set_entry_format_pattern.sub(r"\1", entry) for entry in column if entry)
                for column in columns]

    def _manually_format_set_entries(self, columns: list) -> list:
        columns = self._delete_set_entries(columns)
        columns = self._replace_set_entries(columns)
        return columns

    def _delete_set_entries(self, columns: list) -> list:
        return [column ^ self._set_entries_to_be_deleted.intersection(column) for column in columns]

    def _replace_set_entries(self, columns: list) -> list:
        new_columns = []
        for column in columns:
            new_entries = set()
            for entry in column:
                for pattern, replacement in self._set_entries_to_be_replaced.items():
                    if pattern.match(entry) is not None:
                        entry = pattern.sub(replacement, entry)
                        break
                new_entries.add(entry)
            new_columns.append(new_entries)
        return new_columns
