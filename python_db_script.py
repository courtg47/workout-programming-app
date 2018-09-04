#!/usr/bin/env python
import psycopg2


"""Python script to populate exercisecatlog database with
pre-made information from csv files"""

def database_connection():
    '''Connects to PostgreSQL database using DB-API
    and queries the DB with the above SQL.'''

    db = psycopg2.connect("dbname=exercisecatalog")
    c = db.cursor()

    with open('primary_categories.csv', 'r') as f:
        c.copy_from(f, 'primary_categories', sep=',')

    """

    with open('secondary_categories.csv', 'r') as f:
        c.copy_from(f, 'secondary_categories', sep=',')

    with open('exercises.csv', 'r') as f:
        c.copy_from(f, 'exercises', sep=',')

    with open('additional_categories.csv', 'r') as f:
        c.copy_from(f, 'additional_categories', sep=',')

    """

    #populate_database(c)

    db.commit()
    db.close()



#def populate_database(connection):
    #""""""


if __name__ == '__main__':
    database_connection()
