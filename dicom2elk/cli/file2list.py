import os
import sqlite3 as sq
import sys
from datetime import datetime
import time

from file2list_parser import get_parser

DB_FILE = 'file_abs_database.db'
BATCH_SIZE = 500


def get_db_size(db_connection):
    x = db_connection.execute("SELECT count(*) FROM pacs_file_paths;")
    for row in x:
        print('Nbr file in db : ' + str(row[0]))


def get_db_size_to_clean(db_connection):
    x = db_connection.execute("SELECT count(*) FROM pacs_file_paths where batch is null or batch = 'TMP_';")
    for row in x:
        return int(row[0])


def stage_line(db_connection, batch):
    cmd = (
            "UPDATE pacs_file_paths SET batch = 'TMP_' WHERE path IN (SELECT path FROM pacs_file_paths WHERE batch is null ORDER BY path LIMIT " + str(
        batch) + ")")
    db_connection.execute(cmd)


def clean_db(db_connection, batch, out='.'):
    dump_staged_file(db_connection, out)
    while get_db_size_to_clean(db_connection) > 0:
        stage_line(db_connection, batch)
        dump_staged_file(db_connection, out)


def dump_staged_file(db_connection, out='.'):
    now = datetime.now()  # current date and time
    current_time = now.strftime("%Y%m%d_%H%M%S%f")
    x = db_connection.execute("SELECT path FROM pacs_file_paths where batch = 'TMP_';")
    data_file = ''
    for row in x:
        row = str(row[0])
        if data_file == '':
            data_file = open(out + '\\dicom_' + current_time + '.txt', 'w')
        data_file.write("%s\n" % row)
    if data_file != '':
        data_file.close()
        db_connection.execute(
            "UPDATE pacs_file_paths SET batch = '" + 'dicom_' + current_time + '.txt' + "' WHERE batch = 'TMP_';")


def closing_connection(db_connection, batch, out):
    clean_db(db_connection, batch, out)
    get_db_size(db_connection)
    db_connection.commit()
    db_connection.close()
    return 0


def main():
    parser = get_parser()
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
