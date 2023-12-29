import os
import sqlite3 as sq
import sys
from datetime import datetime
import time
import warnings
import tqdm

from dicom2elk.info import __version__
from dicom2elk.cli.parser import get_file2list_parser
from dicom2elk.utils.database import (
    create_table,
    stage_line,
    dump_staged_file,
    clean_db,
    closing_connection,
)
from dicom2elk.utils.misc import prepare_file_list_batches
from dicom2elk.utils.logging import create_logger


def main():
    parser = get_file2list_parser()
    args = parser.parse_args()

    # Make sure path are absolute
    dir_path = os.path.abspath(args.path)
    output_dir = os.path.abspath(args.output_dir)

    # connect to database
    db_connection = sq.connect(DB_FILE)

    # create table to store file paths
    db_connection.execute('''CREATE TABLE IF NOT EXISTS pacs_file_paths
                     (path TEXT PRIMARY KEY,
                      access_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      batch TEXT
                      );''')
    db_connection.execute('''CREATE INDEX IF NOT EXISTS pacs_file_paths_idx
      ON pacs_file_paths 
        (path)
      WHERE batch is null;''')
    db_connection.execute('''CREATE INDEX IF NOT EXISTS pacs_file_paths_idx_tmp
      ON pacs_file_paths 
        (batch)
      ;''')

    get_db_size(db_connection)

    # assigned regular string date
    date_unixtime = time.mktime(datetime(1990, 1, 1, 0, 0).timetuple())

    # traverse directory and subdirectories
    nb_files = 0
    still_working = 0

    clean_db(db_connection, BATCH_SIZE, output_dir)

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            # get absolute path of file
            file_path = os.path.join(root, file)
            still_working += 1
            if os.path.getmtime(file_path) > date_unixtime:

                # insert path into database
                status = db_connection.execute("INSERT OR IGNORE INTO pacs_file_paths (path) VALUES (?)", (file_path,))
                for row in status:
                    print(row)
                nb_files += 1
                if nb_files % BATCH_SIZE == 0:
                    stage_line(db_connection, BATCH_SIZE)
                    dump_staged_file(db_connection, output_dir)
            if still_working >= args.limit:
                return closing_connection(db_connection, BATCH_SIZE, output_dir)

    # commit changes and close connection
    print("Nbr file read : " + str(still_working))
    return closing_connection(db_connection, BATCH_SIZE, output_dir)


if __name__ == "__main__":
    sys.exit(main())
