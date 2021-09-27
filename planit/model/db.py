# -*- coding: utf-8 -*-

import logging
import sqlite3
from .log import createLogger
from typing import Any, Dict, Iterable, List, Tuple

class Db:
    """ Connect to a sqlite3 database and execute SQL statements. """

    def __init__(self):

        # Path to the db file
        path: str = 'var/planit.db'

        # Use logger
        # TODO: Type hint for logger
        self._logger = createLogger('db')

        # Connect to the db
        self._connection: sqlite3.Connection = sqlite3.connect(path)

        # Create missing tables
        self._create_tables()

    def _execute_sql(
        self, sql: str, values: Iterable[Any] = []) -> List[Tuple[str, ...]]:
        """ Execute a SQL statement securely. """

        try:

            # Execute the SQL statement
            cursor: sqlite3.Cursor = self._connection.cursor()
            cursor.execute(sql, values)
            logging.debug("Execute '{}' with values '{}'".format(sql, values))

            # Get rows
            rows: List[Tuple[str, ...]] = cursor.fetchall()

            self._connection.commit()
            return rows

        except Exception as e:

            # Rollback on exception
            logging.warning('Database rollback')
            self._connection.rollback()

            # Reraise exception
            raise e

    def _create_tables(self) -> None:
        """ Create the tables plants and symbioses. """

        sql_create: str = 'CREATE TABLE IF NOT EXISTS {} ({});'
        tables: Dict[str, List[str]] = {
            'plants':
            ['alias VARCHAR(255) PRIMARY KEY', 'common_name VARCHAR(255)'],
            'symbioses':
            ['plant_a VARCHAR(255)', 'plant_b VARCHAR(255), score INTEGER']
        }

        for name in tables:
            self._execute_sql(sql_create.format(name, ', '.join(tables[name])))

    def add_plant(self, alias: str, common_name: str) -> None:
        """ Add a plant to the db. """

        sql: str = 'INSERT INTO plants VALUES (?, ?)'
        values: List[str] = [alias, common_name]
        self._execute_sql(sql, values)

    def get_all_plants(self) -> Dict[str, str]:
        """ Get all plants from the db. """

        # Get the common names
        sql: str = 'SELECT alias, common_name FROM plants;'
        rows: List[Tuple[str, ...]] = self._execute_sql(sql)

        # Sort the plants
        plants: Dict[str, str] = dict()
        for row in rows:
            plants[row[0]] = row[1]

        return plants

    def get_symbiosis_score(self, plant_a: str, plant_b: str) -> int:
        """ Get the symbiosis score of the plants a and b from the db. """

        # Default 0
        return 0
