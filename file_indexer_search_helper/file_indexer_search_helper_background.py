import atexit
import logging
import os
import sqlite3
import sys
import time
from collections import defaultdict
from operator import itemgetter
from pathlib import Path
from sqlite3 import Connection
from typing import Any

# TODO: add support for full reindex via voice (set all version numbers to 0)
# (dropping table should only be needed in rare updates when table structure changes)
should_drop_table = False
should_perform_full_reindex = False

# Directories containing the following parts will NOT be indexed
# CacheStorage / "Code Cache" is used by Google Chrome (and other programs)
# htmlcache is used by Steam
# CachedData is used by VSCode
# History is used by VSCode (noticed VSCode has History folder with 1500 files across many folders)

# TODO: move to file
ignore_directory_parts = {
    "__pycache__",
    ".git",
    ".vscode",
    "CacheStorage",
    "cache",
    "htmlcache",
    "Code Cache",
    "CachedData",
    "DXCache",
    "History",
    "Temp",
    "Backup",
    "SquirrelTemp",
}

# TODO: move to file
ignore_directories = {
    r"c:\$Recycle.Bin",
    r"%LocalAppData%\PowerToys",
    r"C:\Program Files (x86)\Steam\steamapps\common",
    r"C:\Windows",
    # r"C:\Windows\WinSxS\Manifests",
}

# Use map for better performance
ignore_directory_parts_map = {e.lower() for e in ignore_directory_parts}

ignore_directories_map = {os.path.expandvars(e).lower() for e in ignore_directories}

# Constant for table name inside SQLite database
TABLE_NAME = "file"
# TODO: does the user ever need to change this (or is this when I update the code?)
# Store version number in Talon database (via storage) to allow first time upgrades such as dropping table or full
VERSION = 1

# https://www.geeksforgeeks.org/sqlite-full-text-search/
CREATE_VIRTUAL_TABLE = f"""
CREATE VIRTUAL TABLE IF NOT EXISTS {TABLE_NAME}
USING FTS5(directory, name, extension, size, modified_time, version);
"""

SELECT_COUNT = f"select count(1) as count from {TABLE_NAME}"


def create_database(database_pathname):
    with sqlite3.connect(database_pathname) as connection:
        if should_drop_table:
            connection.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
            connection.commit()

        connection.execute(CREATE_VIRTUAL_TABLE)
        connection.commit()
        logging.debug(
            f"FISHer Existing: {connection.execute(SELECT_COUNT).fetchone()[0]}"
        )

        # https://www.techonthenet.com/sqlite/auto_vacuum.php
        connection.execute("VACUUM")
        connection.commit()

        if should_perform_full_reindex:
            connection.execute(f"update {TABLE_NAME} set version = 0")
            connection.commit()


def create_file_dictionary(directory: str, filename: str) -> dict[str, Any]:
    pathname = os.path.join(directory, filename)
    name, extension = os.path.splitext(filename)

    # If blank or just ".", don't modify
    if len(extension) > 1:
        extension = extension[1:]

    size = os.path.getsize(pathname)
    modified_time = os.path.getmtime(pathname)

    return dict(
        directory=directory,
        name=name,
        extension=extension,
        size=size,
        modified_time=modified_time,
        version=VERSION,
    )


def determine_filename(name: str, extension: str):
    return name + ("." if extension != "" and extension != "." else "") + extension


def query_existing_files(
    database_pathname: str,
) -> defaultdict[str, list[dict[str, Any]]]:
    existing_files = defaultdict(list[dict[str, Any]])

    with sqlite3.connect(database_pathname) as connection:
        cursor = connection.execute(
            f"select rowid, directory, name, extension, size, modified_time, version from {TABLE_NAME}"
        )
        for row in cursor:
            row_dict = {cursor.description[i][0]: e for i, e in enumerate(row)}
            row_dict["filename"] = determine_filename(
                row_dict["name"], row_dict["extension"]
            )
            existing_files[row_dict["directory"]].append(row_dict)

    return existing_files


def filter_index_directories(directory: str, dirs: list[str]) -> list[str]:
    # https://stackoverflow.com/a/10620948
    return [
        dir
        for dir in dirs
        if dir.lower() not in ignore_directory_parts_map
        and os.path.join(directory, dir).lower() not in ignore_directories_map
    ]


def index_directory_files(
    directory: str,
    files: list[str],
    existing_rows: list[dict[str, Any]],
    update_count_mutable: list[int],  # Single index
    insert_files: list[dict[str, Any]],
    delete_records: set[int],
):
    existing_index = 0
    pathwalk_index = 0

    while existing_index < len(existing_rows) or pathwalk_index < len(files):
        if existing_index >= len(existing_rows):
            # "file" is a new file in the directory and should be INSERTED
            try:
                insert_files.append(
                    create_file_dictionary(directory, files[pathwalk_index])
                )
            except OSError as e:
                print(f"An error occurred: {e}")

            pathwalk_index += 1
            continue

        if pathwalk_index >= len(files):
            # File in database is no longer in directory (and can be deleted in database)
            record = existing_rows[existing_index]
            rowid = record["rowid"]
            if rowid in delete_records:
                raise Exception("Duplicate rowid", record)
            delete_records.add(rowid)

            existing_index += 1
            continue

        record = existing_rows[existing_index]
        existing_filename = record["filename"]
        pathwalk_filename = files[pathwalk_index]

        if existing_filename > pathwalk_filename:
            try:
                insert_files.append(
                    create_file_dictionary(directory, files[pathwalk_index])
                )
            except OSError as e:
                print(f"An error occurred: {e}")
            pathwalk_index += 1
        elif pathwalk_filename > existing_filename:
            # For example "DEF" on pathwalk and "ABC" on database
            # In this case, "ABC" is no longer in the directory (and can be delete in the database)
            record = existing_rows[existing_index]
            rowid = record["rowid"]
            if rowid in delete_records:
                raise Exception("Duplicate rowid", record)
            delete_records.add(rowid)
            existing_index += 1
        else:
            # Filenames match
            file_dictionary = create_file_dictionary(directory, pathwalk_filename)

            pathwalk_index += 1
            existing_index += 1

            file_has_change = (
                record["version"] != VERSION
                or record["size"] != file_dictionary["size"]
                or record["modified_time"] != file_dictionary["modified_time"]
            )

            if file_has_change:
                rowid = record["rowid"]
                if rowid in delete_records:
                    raise Exception("Duplicate rowid", record)
                delete_records.add(rowid)

                update_count_mutable[0] += 1
                insert_files.append(file_dictionary)


# TODO: break into smaller functions
def index_files(database_pathname: str):
    start_time = time.time()

    # TODO: Allow specifying multiple locations via talon_list
    # (handle overlap of directories, such as if one is a subdirectory of another can be ignored)
    root_pathname = "c:/"
    # root_pathname = "%userprofile%"
    # root_pathname = "%appdata%/talon/user"
    root_path = Path(os.path.expandvars(root_pathname))

    insert_files = []
    # Create SortedSet (values will always be True; alows ensuring there are not duplicates, which suggests an issue)
    delete_records: set[int] = set()
    update_count_mutable = [0]

    # Create multimap from directory -> files
    # https://stackoverflow.com/a/1731989
    existing_files = query_existing_files(database_pathname)

    logging.debug(f"FISHer walk: {root_path}")

    # TODO: replace path.walk with os.walk
    # (since Talon is currently on Python 3.11 and path.walk was added in 3.12)
    for directory, dirs, files in os.walk(root_path):
        if dirs:
            dirs[:] = filter_index_directories(directory, dirs)

        if not files:
            continue

        files.sort()

        if directory in existing_files:
            existing_rows = existing_files.pop(directory)
            existing_rows.sort(key=itemgetter("filename"))

            # TODO: handle if duplicates get introduced by accident (such as running process twice)
            # In this case, keep first and add later ones to delete records
            # Remove from above results (so can update first one as needed)
        else:
            existing_rows = []

        index_directory_files(
            directory,
            files,
            existing_rows,
            update_count_mutable,
            insert_files,
            delete_records,
        )

    # Any files remaining in existing_files are for directories which no longer existing on the file system
    # These records can be deleted
    for records in existing_files.values():
        for record in records:
            rowid = record["rowid"]
            if rowid in delete_records:
                raise Exception("Duplicate rowid", record)
            delete_records.add(rowid)

    # TODO: Also read file contents (depending on file types, use include list)
    # (that way can slowly add types and ignore binary like png)

    # For file contents, should this be handled separately?
    # Would allow storing row number and adding logic to parse using parse-tree to identify info
    # For example, could indicate method name, class name
    # Also indicate type of line (such as assignment, function definition, etc.)

    update_count = update_count_mutable[0]
    upsert_database(database_pathname, update_count, insert_files, delete_records)

    end_time = time.time()

    # get the execution time
    elapsed_time = end_time - start_time
    logging.debug(f"FISHer Execution time: {elapsed_time} seconds")


# TODO: implement method to index_files_batch based on passed deque


def upsert_database(
    database_pathname: str,
    update_count: int,
    insert_files: list[dict[str, Any]],
    delete_records: set[int],
):
    connection: Connection
    with sqlite3.connect(database_pathname) as connection:
        # https://stackoverflow.com/a/52479382
        # https://stackoverflow.com/a/16856730
        # (need to convert into list of tuples of size 1)
        connection.executemany(
            f"delete from {TABLE_NAME} where rowid = ?",
            [(d,) for d in delete_records],
        )

        # https://stackoverflow.com/a/32239587
        # https://stackoverflow.com/a/53963137
        connection.executemany(
            f"""
            insert into {TABLE_NAME}(directory, name, extension, size, modified_time, version)
            values (:directory, :name, :extension, :size, :modified_time, :version)
            """,
            insert_files,
        )

        connection.commit()

        logging.debug(f"FISHer Updated {update_count} files in database")
        logging.debug(f"FISHer Inserted {len(insert_files) - update_count} files")
        logging.debug(
            f"FISHer Deleted {len(delete_records) - update_count} records from database"
        )


unlink_fisher_path: Path = None


@atexit.register
def on_close():
    if unlink_fisher_path:
        unlink_fisher_path.unlink()


def determine_fisher_lock_path(database_pathname: str) -> Path:
    return Path(database_pathname).with_name("FISHer.lck")


def main():
    global unlink_fisher_path

    logging.getLogger().setLevel(logging.DEBUG)

    if len(sys.argv) != 2:
        logging.debug("Pass DB pathname as parameter")
        return

    database_pathname = sys.argv[1]

    fisher_lock_path = determine_fisher_lock_path(database_pathname)
    try:
        if fisher_lock_path.exists():
            logging.error(f"Indexer is already running, see {fisher_lock_path}")
            return

        with fisher_lock_path.open("x") as file:
            unlink_fisher_path = fisher_lock_path

            pid = os.getpid()
            file.write(str(pid))

        print("Database pathname:", database_pathname)
        create_database(database_pathname)
        index_files(database_pathname)
    except Exception as e:
        print(f"An error occurred: {e}")
    # finally:
    #     input("Press enter to exit")


if __name__ == "__main__":
    main()
