# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Module that provides functions used by `file2list` to interact with a SQL database."""

from datetime import datetime
import os
import sqlite3 as sq


BATCH_SIZE = 500


def get_db_size(db_connection: sq.Connection, table: str = 'pacs_file_paths'):
    """Print the number of file in the database.

    Args:
        db_connection (sq.Connection): The connection to the database.
        table (str): The name of the table. Default is 'pacs_file_paths'.
    """
    x = db_connection.execute(f"SELECT count(*) FROM {table};")
    for row in x:
        print('Nbr file in db : ' + str(row[0]))


def get_db_size_to_clean(db_connection: sq.Connection, table: str = 'pacs_file_paths'):
    """Get the number of file in the database to clean e.g. where batch is null or batch = 'TMP_'.

    Args:
        db_connection (sq.Connection): The connection to the database.
        table (str): The name of the table. Default is 'pacs_file_paths'.

    Returns:
        int: The number of file to clean.
    """
    x = db_connection.execute(f"SELECT count(*) FROM {table} where batch is null or batch = 'TMP_';")
    for row in x:
        return int(row[0])


def stage_line(db_connection: sq.Connection, table: str = 'pacs_file_paths', batch: int = BATCH_SIZE):
    """Stage a file (line) in the database.

    Args:
        db_connection (sq.Connection): The connection to the database.
        table (str): The name of the table. Default is 'pacs_file_paths'.
        batch (int): The batch size. Default is 500.
    """
    cmd = (
            f"UPDATE {table} SET batch = 'TMP_' WHERE path IN "
            f"(SELECT path FROM {table} WHERE batch is null ORDER BY path LIMIT {batch})")
    db_connection.execute(cmd)


def dump_staged_file(
    db_connection: sq.Connection,
    table: str = 'pacs_file_paths',
    out: str = '.'
):
    """Dump the staged file (with batch = 'TMP_') in a text file.

    Args:
        db_connection (sq.Connection): The connection to the database.
        table (str): The name of the table. Default is 'pacs_file_paths'.
        out (str): The output directory. Default is '.'.
    """
    now = datetime.now()  # current date and time
    current_time = now.strftime("%Y%m%d_%H%M%S%f")

    cmd = f"SELECT path FROM {table} where batch = 'TMP_';"
    x = db_connection.execute(cmd)

    data_file = ''
    for row in x:
        row = str(row[0])
        if data_file == '':
            file_path = os.path.join(out, 'dicom_' + current_time + '.txt')
            # print("Opening file: " + file_path + " to write")
            data_file = open(file=file_path, mode='w')
        data_file.write("%s\n" % row)

    if data_file != '':
        data_file.close()
        db_connection.execute(
            f"UPDATE {table} SET batch = 'dicom_{current_time}.txt' WHERE batch = 'TMP_';"
        )


def clean_db(db_connection: sq.Connection, table: str = 'pacs_file_paths', batch: int = BATCH_SIZE, out: str = '.'):
    """Clean the database.

    Args:
        db_connection (sq.Connection): The connection to the database.
        table (str): The name of the table. Default is 'pacs_file_paths'.
        batch (int): The batch size.
        out (str): The output directory.
    """
    dump_staged_file(db_connection, table=table, out=out)
    while get_db_size_to_clean(db_connection, table=table) > 0:
        stage_line(db_connection, table=table, batch=batch)
        dump_staged_file(db_connection, table=table, out=out)


def closing_connection(
    db_connection: sq.Connection,
    table: str = 'pacs_file_paths',
    batch: int = BATCH_SIZE,
    out: str = '.',
):
    """Close the connection to the database.

    Args:
        db_connection (sq.Connection): The connection to the database.
        table (str): The name of the table. Default is 'pacs_file_paths'.
        batch (int): The batch size. Default is 500.
        out (str): The output directory. Default is '.'.

    Returns:
        int: 0
    """
    clean_db(db_connection, table=table, batch=batch, out=out)
    get_db_size(db_connection, table=table)
    db_connection.commit()
    db_connection.close()
    return 0


def create_table(db_connection: sq.Connection, table: str = 'pacs_file_paths'):
    """Create the table to store file paths.

    It creates the table if it does not exist with the following indices:
    - path (primary key)
    - path (where batch is null)
    - batch

    It prints the number of file in the database after the creation.

    Args:
        db_connection (sq.Connection): The connection to the database.
        table (str): The name of the table. Default is 'pacs_file_paths'.
    """
    db_connection.execute(f'''CREATE TABLE IF NOT EXISTS {table}
                     (path TEXT PRIMARY KEY,
                      access_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      batch TEXT
                      );''')
    db_connection.execute(f'''CREATE INDEX IF NOT EXISTS {table}_idx
      ON {table} 
        (path)
      WHERE batch is null;''')
    db_connection.execute(f'''CREATE INDEX IF NOT EXISTS {table}_idx_tmp
      ON {table} 
        (batch)
      ;''')
    get_db_size(db_connection, table)
