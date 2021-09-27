# -*- coding: utf-8 -*-

"""
Database

Connect to a sqlite3 database and execute SQL statements.
"""

import log, logging
import sqlite3
from typing import Any, Dict, Iterable, List, Tuple

# Path to the db file
path: str = '../../var/planit.db'

# Use logger
# TODO: Type hint for logger
logger = log.createLogger('db')

# Connect to the db
connection: sqlite3.Connection = sqlite3.connect(path)

def execute_sql(sql: str, values: Iterable[Any] = []) -> List[Tuple[str, ...]]:
    """ Secure execution of an SQL statement. """

    try:

        # Execute the SQL statement
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(sql, values)
        logging.debug("Execute '{}' with values '{}'".format(sql, values))

        # Get rows
        rows: List[Tuple[str, ...]] = cursor.fetchall()

        connection.commit()
        return rows

    except Exception as e:

        # Rollback on exception
        logging.warning('Database rollback')
        connection.rollback()

        # Reraise exception
        raise e

def create_tables() -> None:
    """ Create the table plants. """

    sql: str = ('CREATE TABLE IF NOT EXISTS plants (alias VARCHAR(255), ' +
                'common_name VARCHAR(255));')
    execute_sql(sql)

def add_plant(alias: str, common_name: str) -> None:
    """ Add a plant to the model. """

    sql: str = 'INSERT INTO plants VALUES (?, ?)'
    values: List[str] = [alias, common_name]
    execute_sql(sql, values)

def get_all_plants() -> Dict[str, str]:
    """ Get all plants. """

    # Get the common names
    sql: str = 'SELECT alias, common_name FROM plants;'
    rows: List[Tuple[str, ...]] = execute_sql(sql)

    # Sort the plants
    plants: Dict[str, str] = dict()
    for row in rows:
        plants[row[0]] = row[1]

    return plants

# Create missing tables
create_tables()
