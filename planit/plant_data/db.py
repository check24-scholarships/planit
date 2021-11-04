# -*- coding: utf-8 -*-

import logging
import os
import sqlite3
from planit import resources
from .log import createLogger
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Tuple, Union

# Path of the log dir
basePath: str = 'plantdata/'

class Db:
    """ Connect to a sqlite3 database and execute SQL statements. """

    def __init__(self):

        # Path to the db file
        path: str = os.path.join(resources.get(basePath), 'planit.db')

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
            logging.warning("Database rollback because of '{}'".format(e))
            self._connection.rollback()

            # Reraise exception
            raise e

    def _create_tables(self) -> None:
        """ Create the tables plants and symbioses. """

        sql: str = 'CREATE TABLE IF NOT EXISTS {} ({});'
        tables: Dict[str, List[str]] = {
            'plants':
            ['common_name TEXT PRIMARY KEY'],
            'symbioses':
            ['plant_a TEXT NOT NULL', 'plant_b TEXT NOT NULL',
            'score INTEGER NOT NULL']
        }

        for name in tables:
            self._execute_sql(sql.format(name, ', '.join(tables[name])))

    def overwrite(self, name: str) -> None:
        """ Overwrite a table. """

        sql: str = 'DROP TABLE IF EXISTS {};'
        self._execute_sql(sql.format(name))
        self._create_tables()

    def add_plant(self, common_name: str) -> bool:
        """ Add a plant to the db if it does not exist so far. """

        sql: str = 'INSERT INTO plants VALUES (?)'
        values: List[str] = [common_name]
        try:
            self._execute_sql(sql, values)
            return True
        except sqlite3.IntegrityError as e:
            logging.debug("Integrity error: '{}'".format(e))
            return False

    def add_symbiosis_score(self, plant_a: str, plant_b: str,
                            score: int) -> bool:
        """ Add a symbiosis score to the db if it does not exist so far. """

        sql_integrity: str = ('SELECT 1 FROM symbioses WHERE plant_a = ? AND ' +
                              'plant_b = ? OR plant_a = ? AND plant_b = ?')
        values_integrity: List[str] = [plant_a, plant_b, plant_b, plant_a]
        sql_insert: str = 'INSERT INTO symbioses VALUES (?, ?, ?)'
        values_insert: List[Union[str, int]] = [plant_a, plant_b, score]

        # Check integrity and insert the symbiosis score
        if len(self._execute_sql(sql_integrity, values_integrity)) == 0:
            self._execute_sql(sql_insert, values_insert)
            return True
        logging.debug('Integrity error')
        return False

    def get_all_plants(self) -> List[str]:
        """ Get all plants from the db. """

        # Get the common names
        sql: str = 'SELECT common_name FROM plants;'
        rows: List[Tuple[str, ...]] = self._execute_sql(sql)

        # Sort the plants
        plants: List[str] = []
        for row in rows:
            plants.append(row[0])

        return plants

    # Max size of 500 items for LRU cache to prevent the app from using too much
    # memory
    @lru_cache(500)
    def get_symbiosis_score(self, plant_a: str, plant_b: str) -> int:
        """ Get the symbiosis score of the plants a and b from the db. """

        # Find the symbiosis in the db
        sql: str = ('SELECT score FROM symbioses WHERE plant_a = ? AND ' +
                    'plant_b = ? OR plant_a = ? AND plant_b = ?')
        values: List[str] = [plant_a, plant_b, plant_b, plant_a]
        symbiosis_score: List[Tuple[str, ...]] = self._execute_sql(sql, values)
        if not len(symbiosis_score) == 0:
            return int(symbiosis_score[0][0])

        # Default 0
        return 0
