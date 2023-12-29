# Copyright (C) 2023, The TranslationalML team and Contributors. All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""Tests for dicom2elk.utils.database module."""

import os
import pytest
import sqlite3 as sq

from dicom2elk.utils.database import (
    create_table,
    add_path_to_db,
    get_db_size,
    get_db_size_to_clean,
    stage_line,
    dump_staged_file,
    clean_db,
    closing_connection,
)


def test_create_table(db_connection):
    # Test if create_table creates a table in the database
    create_table(db_connection, table="test_table")
    # Check if the table exists
    x = db_connection.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in x]
    assert "test_table" in tables
    

def test_add_path_to_db(db_connection):
    # Test if add_path_to_db adds a path to the database
    add_path_to_db(db_connection, file_path="test_path", table="test_table")
    # Check if the path is in the database
    x = db_connection.execute("SELECT path FROM test_table;")
    paths = [row[0] for row in x]
    assert "test_path" in paths
    

def test_stage_line(db_connection):
    # Check if there is a file not staged (batch is null)
    x = db_connection.execute("SELECT count(*) FROM test_table WHERE batch is null;")
    for row in x:
        assert row[0] > 0
    # Test if stage_line stages a line in the database
    stage_line(db_connection, table="test_table")
    # Check if we have one file staged
    x = db_connection.execute("SELECT count(*) FROM test_table WHERE batch = 'TMP_';")
    for row in x:
        assert row[0] > 0
    # Check if there is no file not staged (batch is null)
    x = db_connection.execute("SELECT count(*) FROM test_table WHERE batch is null;")
    for row in x:
        assert row[0] == 0


def test_dump_staged_file(db_connection, io_path):
    # Test if dump_staged_file dumps a staged file
    files_list_path = dump_staged_file(
        db_connection,
        table="test_table",
        out=io_path,
    )
    # Check if the file is not empty
    with open(files_list_path) as f:
        lines = f.readlines()
    assert len(lines) > 0
    # Check if the file contains the staged file
    assert "test_path" in lines[0]
    # Check in the database if the file has the value of "batch"
    # equaled to the basename of files_list_path
    x = db_connection.execute(
        f"SELECT count(*) FROM test_table WHERE batch = '{os.path.basename(files_list_path)}';"
    )
    for row in x:
        assert row[0] > 0
    

def test_get_db_size(db_connection):
    # Test if get_db_size returns the number of file in the database
    # when the table is empty
    get_db_size(db_connection, table="test_table")
    assert True


def test_get_db_size_to_clean(db_connection):
    # Test if get_db_size_to_clean returns the number of file in the database
    # when the table is empty
    get_db_size_to_clean(db_connection, table="test_table")
    assert True


def test_clean_db(db_connection, io_path):
    # Test if clean_db cleans the database
    clean_db(db_connection, table="test_table", batch=1, out=io_path)
    # Check if the database is empty
    x = db_connection.execute("SELECT count(*) FROM test_table WHERE batch = 'TMP_';")
    for row in x:
        assert row[0] == 0


def test_closing_connection(db_connection, io_path):
    # Test if closing_connection closes the connection to the database
    closing_connection(db_connection, table="test_table", batch=1, out=io_path)
    # Check if connection is closed
    is_closed = False
    try:
        db_connection.cursor()
    except sq.ProgrammingError:
        is_closed = True
    assert is_closed
