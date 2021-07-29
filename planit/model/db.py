# -*- coding: utf-8 -*-

'''
Database

Connects to a sqlite3 database and execute SQL statements.
'''

import log, logging
import sqlite3

# Path to the db file
path: str = '../../var/planit.db'

# Use logger
# TODO: Type hint for logger
logger = log.createLogger('db')

# Connect to the db
connection: sqlite3.Connection = sqlite3.connect(path)

def executeSQL(sql: str) -> bool:

    '''
    Secure execution of an SQL statement.
    '''

    try:

        # Execute the SQL statement
        cursor: sqlite3.Cursor = connection.cursor()
        cursor.execute(sql)
        logging.debug("Execute '{}'".format(sql))
        connection.commit()

        return True

    except Exception as e:

        # Rollback on exception
        logging.warning('Database rollback')
        connection.rollback()

        # Reraise exception
        raise e
