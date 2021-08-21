import re
import spacy


class DataFormatter:
    def __init__(self):
        # TODO: include in requirements.txt
        self._nlp = spacy.load("en_core_web_sm")
        # name formatting
        self._lemmatized_name_format_pattern = re.compile(r" (/|'s |, ) ?")
        self._names_to_be_replaced = {
            re.compile(r"^(bean), (.+)"): r"\2 \1", re.compile(r"brassicas"): "brassica",
            re.compile(r".*/maize$"): "corn", re.compile(r"(.*) or aubergine"): r"\1",
            re.compile(r"savoury"): "savory",
            re.compile(r" and rutabaga|cilantro/"): ""
        }
        # set entry formatting
        self._square_brackets_pattern = re.compile(r"\[[^]]*]")
        self._brackets_pattern = re.compile(r"\([^)]*\)")
        self._unique_text_mistake = re.compile(r" \((?:[^,]+,){3}")
        self._split_pattern = re.compile(r"[,;.&/]\s?|\s?\band\s|\sor\s")
        self._lemmatized_set_entry_format_pattern = re.compile(r" (-|'s ) ?")
        self._set_entries_to_be_deleted = {"together", "almost everything", "plant with many blossom", "many other"}
        self._set_entries_to_be_replaced = {
            re.compile(r"lady bug"): "ladybug", re.compile(r"^aster.*"): "aster",
            re.compile(r"radishes"): "radish", re.compile(r"brassicas"): "brassica",
            re.compile(r"green onion with chinese cabbage"): "onion", re.compile(r"maize"): "corn",
            re.compile(r"aubergine"): "eggplant", re.compile(r"savoury"): "savory",
            re.compile(r"many type of grass including kentucky bluegrass"): "grass",
            re.compile(r"cilantro"): "coriander", re.compile(r"avoid any member of the allium family"): "allium",
            re.compile(r"hoverflie"): "hoverfly", re.compile(r"butterflies"): "butterfly",
            re.compile(r"apple tree"): "apple",
            re.compile(r"(?:most|such as|mixture of|beneficial for|a variety of|other) |"
                       r" because.*|(?:.* )?especially |.*many (?:other )?|"
                       r"plant (?:which are prone to|that attracts) "): ""
        }

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
        return [column.text.strip().lower() for column in columns]

    def _format_name(self, name: str) -> str:
        name = self._lemmatize_word(name)
        name = self._format_lemmatized_name(name)
        name = self._manually_replace_names(name)
        return name

    def _lemmatize_word(self, word: str) -> str:
        """
        turns nouns singular
        """
        return " ".join([word.lemma_ if word.pos_ == "NOUN" else word.text for word in self._nlp(word)])

    def _format_lemmatized_name(self, name: str) -> str:
        return self._lemmatized_name_format_pattern.sub(r"\1", name)

    def _manually_replace_names(self, name: str) -> str:
        for pattern, replacement in self._names_to_be_replaced.items():
            if pattern.search(name):
                return pattern.sub(replacement, name)
        return name

    def _format_set_entries(self, columns: list) -> list:
        """
        formats the entries of helps, helped by, attracts ,-Repels/+distracts and avoid strings to sets.
        """
        columns = self._remove_footnotes_and_examples(columns)
        columns = self._remove_unique_text_mistake(columns)
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

    def _remove_unique_text_mistake(self, columns: list) -> list:
        columns[0] = self._unique_text_mistake.sub(",", columns[0])
        return columns

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
        columns = self._manually_delete_set_entries(columns)
        columns = self._manually_replace_set_entries(columns)
        return columns

    def _manually_delete_set_entries(self, columns: list) -> list:
        return [column ^ self._set_entries_to_be_deleted.intersection(column) for column in columns]

    def _manually_replace_set_entries(self, columns: list) -> list:
        new_columns = []
        for column in columns:
            new_entries = set()
            for entry in column:
                for pattern, replacement in self._set_entries_to_be_replaced.items():
                    if pattern.search(entry):
                        entry = pattern.sub(replacement, entry)
                new_entries.add(entry)
            new_columns.append(new_entries)
        return new_columns

    # TODO: handle insects: at entry --> 'carrot'/'borage'
