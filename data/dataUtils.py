"""
A manager for the database.
"""

import sqlite3


class DB:
    """
    A manager for the database.
    """

    def __init__(self, db_name):
        """
        Constructor for the DB class.
        """
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        """
        Creates a table in the database.
        """
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS {} {};".format(table_name, columns))
        self.conn.commit()

    def insert(self, table_name, columns, values):
        """
        Inserts a row into the database.
        """
        self.cursor.execute("INSERT INTO {} {} VALUES {};".format(
            table_name, columns, values))
        self.conn.commit()

    def update(self, table_name, columns, values, where=True):
        """
        Updates a row in the database.
        """
        self.cursor.execute("UPDATE {} SET {} WHERE {};".format(
            table_name, columns, where))
        self.conn.commit()

    def delete(self, table_name, where):
        """
        Deletes a row in the database.
        """
        self.cursor.execute(
            "DELETE FROM {} WHERE {};".format(table_name, where))
        self.conn.commit()

    def select(self, table_name, columns, where):
        """
        Selects a row in the database.
        """
        self.cursor.execute("SELECT {} FROM {} WHERE {};".format(
            columns, table_name, where))
        return self.cursor.fetchall()

    def select_all(self, table_name):
        """
        Selects all rows in the database.
        """
        self.cursor.execute("SELECT * FROM {};".format(table_name))
        return self.cursor.fetchall()

    def close(self):
        """
        Closes the connection to the database.
        """
        self.conn.close()
