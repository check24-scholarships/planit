import re
from typing import Union


def format_columns(columns: list) -> list:
    """
    applies all format methods on the columns list.
    """
    columns = _format_html_code_to_plain_text(columns)
    columns = _format_column_entry_strings_to_sets(columns)
    return columns


def _format_html_code_to_plain_text(columns: list) -> list:
    """
    returns the columns list but with plain text instead of html code.
    """
    return [_remove_footnotes_and_examples(column.text.strip()) for column in columns]


def _remove_footnotes_and_examples(column_entry: str) -> str:
    """
    The regular expression removes square brackets and their contents (Wikipedia footnotes) as well as regular brackets
    and their contents (Examples).
    """
    return re.sub(r"\((.*?)\)", "", re.sub(r"\[(.*?)]", "", column_entry))


def _format_column_entry_strings_to_sets(columns: list) -> list:
    """
    formats the entries of helps, helped by, attracts ,-Repels/+distracts and avoid strings to sets.
    """
    new_columns = columns[:2]
    for column in columns[2:]:
        new_columns.append(_split_column(column))
    return new_columns


def _split_column(column: str) -> Union[set, None]:
    """
    splits the column string on multiple different separators.
    """
    # If an empty string is passed return None
    if not column:
        return None
    separators = [" and ", " or ", ";", "/", ". "]
    for separator in separators:
        column = column.replace(separator, ",")
    return _strip_entries(column.split(","))


def _strip_entries(entry: list) -> set:
    """
    strips all list entries and removes empty strings. returns the entries as a set.
    """
    return set(entry.strip().rstrip(".") for entry in entry if entry)
