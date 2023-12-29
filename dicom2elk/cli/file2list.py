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

    # Create the log filename and make sure there is not white space
    # and special character in the name of the input directory (basedir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    basedir = os.path.basename(os.path.abspath(args.path))
    log_basename = f"file2list_{basedir}_{timestamp}.log"
    for c in [' ', '(', ')', '[', ']', '{', '}', ',', ';', ':', '\'', '\"', '\\', '/']:
        log_basename = log_basename.replace(c, '_')
    # Create logger
    logger = create_logger(args.log_level, args.output_dir, log_basename)
    
    # Ignore warnings
    warnings.filterwarnings("ignore")

    # Make sure path are absolute
    args.path = os.path.abspath(args.path)
    args.output_dir = os.path.abspath(args.output_dir)
    
    # Display run summary
    logger.info(
        f"Running file2list (dicom2elk version {__version__}) with the following arguments:"
    )
    for arg in vars(args):
        logger.info(f"{arg}: {getattr(args, arg)}")

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

                    logger.info("Nbr file read : " + str(still_working))
                    logger.info("Finished!")
    # commit changes and close connection
    logger.info("Nbr file read : " + str(still_working))
    logger.info("Finished!")


if __name__ == "__main__":
    sys.exit(main())
