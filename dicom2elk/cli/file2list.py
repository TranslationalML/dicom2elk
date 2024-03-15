# Copyright 2023-2024 Lausanne University and Lausanne University Hospital, Switzerland & Contributors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    add_path_to_db,
    stage_line,
    dump_staged_file,
    clean_db,
    closing_connection,
)
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
    db_connection = sq.connect(database=args.db_file)

    # create table to store file paths
    create_table(db_connection, table=args.db_table)

    # assigned regular string date
    date_unixtime = time.mktime(datetime(1990, 1, 1, 0, 0).timetuple())

    # traverse directory and subdirectories
    nb_files = 1
    still_working = 0

    clean_db(db_connection, table=args.db_table, batch=args.batch_size, out=args.output_dir)

    for root, _, files in os.walk(args.path):
        # iterate over files
        for file in tqdm.tqdm(
            files,
            total=len(files),
            desc=f"Processing files (batch size: {args.batch_size})",
        ):
            # get absolute path of file
            file_path = os.path.join(root, file)
            still_working += 1
            if os.path.getmtime(file_path) > date_unixtime:
                # insert path into database
                nb_files += add_path_to_db(db_connection, file_path, table=args.db_table)
                if nb_files % args.batch_size == 0:
                    stage_line(db_connection, table=args.db_table, batch=args.batch_size)
                    dump_staged_file(db_connection, table=args.db_table, out=args.output_dir)
            if args.limit is not None and args.limit <= still_working:
                logger.info("Nbr file read : " + str(still_working))
                logger.info("Finished!")
                return closing_connection(
                    db_connection, table=args.db_table, batch=args.batch_size, out=args.output_dir
                )
            time.sleep(args.sleep_time_ms / 1000.0)  # takes seconds as argument
            
    # commit changes and close connection
    logger.info("Nbr file read : " + str(still_working))
    logger.info("Finished!")
    return closing_connection(
        db_connection,  table=args.db_table, batch=args.batch_size, out=args.output_dir
    )


if __name__ == "__main__":
    sys.exit(main())
