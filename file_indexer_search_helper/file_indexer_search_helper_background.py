import atexit
import logging
import os
import sqlite3
import sys
import time
from collections import defaultdict
from contextlib import closing
from dataclasses import dataclass
from operator import itemgetter
from pathlib import Path
from sqlite3 import Connection
from typing import Any

script_directory = Path(__file__).resolve().parent

logger = logging.getLogger("file_indexer_search_helper")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(script_directory / "file_indexer_search_helper.log")
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("[Background] %(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# TODO: add support for full reindex via voice (set all version numbers to 0)
# (dropping table should only be needed in rare updates when table structure changes)
# should_drop_table = False
# should_perform_full_reindex = False

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

# Use set for better performance
# TODO: only lowercase on Windows (or use os.path.normcase)
ignore_directory_parts_map = {e.lower() for e in ignore_directory_parts}

# TODO: only lowercase on Windows (or use os.path.normcase)
ignore_directories_map = {os.path.expandvars(e).lower() for e in ignore_directories}

# Logic from esshop (though not sure if this is the best way to do it)
# (ideally would have static class variables, though this looked complicated and unsure if needed)

# Changed from list to tuple to make immutable (even during instantiation)
STORED_COLUMNS = (
    "directory",
    "name",
    "extension",
    "size",
    "modified_time",
    "version",
)

# TODO: add generated columns as needed
GENERATED_COLUMNS = ()
COLUMNS = STORED_COLUMNS + GENERATED_COLUMNS
# logger.debug(f"FISHer COLUMNS: {COLUMNS}")

# Turned into frozenset to make immutable (even during instantiation)
UNINDEXED_COLUMNS = frozenset(
    {
        "size",
        "modified_time",
        "version",
    }
)

FTS_COLUMNS = frozenset(
    column_name for column_name in COLUMNS if column_name not in UNINDEXED_COLUMNS
)
# logger.debug(f"FISHer FTS_COLUMNS: {FTS_COLUMNS}")


@dataclass(frozen=True)
class FisherSettings:
    table_name = "file"

    # Don't add type hint to make immutable (even during instantiation)
    # TODO: find better way?
    select_count = f"select count(1) as count from {table_name}"

    # TODO: change to actual constant (so cannot be modified at runtime)
    # Constant for table name inside SQLite database

    # TODO: does the user ever need to change this (or is this when I update the code?)
    # Store version number in Talon database (via storage) to allow first time upgrades such as dropping table or full
    version = 1

    # Logic from esshop
    FTS_TABLE_NAME = f"{table_name}_fts_idx"
    # TODO: changed from list to tuple to make immutable (even during instantiation)
    # In order to use as a class variable, need to use field(default_factory=...) to avoid mutable default value
    # (need to also use for anything which relies on this, such as OLD_FTS_COLUMN_NAMES and NEW_FTS_COLUMN_NAMES)
    # FTS_COLUMNS: ClassVar[tuple[str, ...]] = field(
    #     default_factory=lambda: tuple(
    #         column_name
    #         for column_name in FisherSettings.COLUMNS
    #         if column_name not in FisherSettings.UNINDEXED_COLUMNS
    #     )
    # )

    COLUMN_NAMES = ",".join([column_name for column_name in COLUMNS])
    FTS_COLUMN_NAMES = ",".join([column_name for column_name in FTS_COLUMNS])
    OLD_FTS_COLUMN_NAMES = ",".join(
        ["old." + column_name for column_name in FTS_COLUMNS]
    )
    NEW_FTS_COLUMN_NAMES = ",".join(
        ["new." + column_name for column_name in FTS_COLUMNS]
    )

    DROP_TRIGGERS = f"""
    DROP TRIGGER IF EXISTS {table_name}_insert;
    DROP TRIGGER IF EXISTS {table_name}_delete;
    DROP TRIGGER IF EXISTS {table_name}_update;
    """

    REINDEX_FTS = f"""
    DROP TABLE IF EXISTS {FTS_TABLE_NAME};
    CREATE VIRTUAL TABLE IF NOT EXISTS {FTS_TABLE_NAME} USING fts5({FTS_COLUMN_NAMES}, content='{table_name}', tokenize = 'porter trigram');
    INSERT INTO {FTS_TABLE_NAME}({FTS_TABLE_NAME}) VALUES('rebuild');
    """

    # TODO: why does the delete trigger perfom an update??
    # Is there a better way to write these
    # Reference https://medium.com/@johnidouglasmarangon/full-text-search-in-sqlite-a-practical-guide-80a69c3f42a4
    # (though the update looks wrong in the article...why is it an insert?)
    CREATE_TRIGGERS = f"""
    CREATE TRIGGER {table_name}_insert AFTER INSERT ON {table_name} BEGIN
        INSERT INTO {FTS_TABLE_NAME}(rowid, {FTS_COLUMN_NAMES}) VALUES (new.rowid, {NEW_FTS_COLUMN_NAMES});
    END;
    CREATE TRIGGER {table_name}_delete AFTER DELETE ON {table_name} BEGIN
        INSERT INTO {FTS_TABLE_NAME}({FTS_TABLE_NAME}, rowid, {FTS_COLUMN_NAMES}) VALUES('delete', old.rowid, {OLD_FTS_COLUMN_NAMES});
    END;
    CREATE TRIGGER {table_name}_update AFTER UPDATE ON {table_name} BEGIN
        INSERT INTO {FTS_TABLE_NAME}({FTS_TABLE_NAME}, rowid, {FTS_COLUMN_NAMES}) VALUES('delete', old.rowid, {OLD_FTS_COLUMN_NAMES});
        INSERT INTO {FTS_TABLE_NAME}(rowid, {FTS_COLUMN_NAMES}) VALUES (new.rowid, {NEW_FTS_COLUMN_NAMES});
    END;
    """

    # TODO: can add generated columns after drop triggers
    # (remember to first drop columns in reverse order of creation)
    CREATE_FULL_TEXT_SEARCH = f"""
    DROP TABLE IF EXISTS {table_name};
    CREATE TABLE IF NOT EXISTS {table_name}(rowid INTEGER PRIMARY KEY, {COLUMN_NAMES});

    {DROP_TRIGGERS}

    {REINDEX_FTS}

    {CREATE_TRIGGERS}

"""


# https://www.geeksforgeeks.org/sqlite-full-text-search/
# create_virtual_table = f"""
# CREATE VIRTUAL TABLE IF NOT EXISTS {table_name}
# USING FTS5(directory, name, extension, size UNINDEXED, modified_time UNINDEXED, version UNINDEXED, tokenize = 'porter trigram');
# """


fisher_settings = FisherSettings()


def create_database(database_pathname):
    with closing(sqlite3.connect(database_pathname)) as connection:
        # if should_drop_table:
        #     connection.execute(f"DROP TABLE IF EXISTS {fisher_settings.table_name}")
        #     connection.commit()

        # logger.debug(fisher_settings.CREATE_TRIGGERS)

        connection.executescript(fisher_settings.CREATE_FULL_TEXT_SEARCH)
        # connection.execute(fisher_settings.create_virtual_table)
        connection.commit()
        logger.debug(
            f"FISHer Existing: {connection.execute(fisher_settings.select_count).fetchone()[0]}"
        )

        # https://www.techonthenet.com/sqlite/auto_vacuum.php
        connection.execute("VACUUM")
        connection.commit()

        # if should_perform_full_reindex:
        #     connection.execute(f"update {fisher_settings.table_name} set version = 0")
        #     connection.commit()


def create_file_dictionary(
    directory: str, filename: str, handle_deleted_files=False
) -> dict[str, Any]:
    pathname = os.path.join(directory, filename)
    name, extension = os.path.splitext(filename)

    # If blank or just ".", don't modify
    if len(extension) > 1:
        extension = extension[1:]

    if handle_deleted_files and not os.path.isfile(pathname):
        size = -1
        modified_time = -1
    else:
        size = os.path.getsize(pathname)
        modified_time = os.path.getmtime(pathname)

    return {
        "directory": directory,
        "name": name,
        "extension": extension,
        "size": size,
        "modified_time": modified_time,
        "version": fisher_settings.version,
    }


def determine_filename(name: str, extension: str):
    return name + ("." if extension != "" and extension != "." else "") + extension


def query_existing_files(
    database_pathname: str,
) -> defaultdict[str, list[dict[str, Any]]]:
    existing_files = defaultdict(list[dict[str, Any]])

    with closing(sqlite3.connect(database_pathname)) as connection:
        cursor = connection.execute(
            f"select rowid, directory, name, extension, size, modified_time, version from {fisher_settings.table_name}"
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
    files: list[str],  # Comes in already sorted
    existing_rows: list[dict[str, Any]],  # Comes in already sorted by filename
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
                logger.error(f"An error occurred: {e}")

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
                logger.error(f"An error occurred: {e}")
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
                record["version"] != fisher_settings.version
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

    insert_files: list[dict[str, Any]] = []
    # Create SortedSet (values will always be True; alows ensuring there are not duplicates, which suggests an issue)
    delete_records: set[int] = set()
    update_count_mutable = [0]

    # Create multimap from directory -> files
    # https://stackoverflow.com/a/1731989
    existing_files = query_existing_files(database_pathname)

    logger.debug(f"FISHer walk: {root_path}")

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
    logger.debug(f"FISHer Execution time: {elapsed_time} seconds")


# TODO: implement method to index_files_batch based on passed deque
# Note: cannot use actual upsert on virtual table
def upsert_database(
    database_pathname: str,
    update_count: int,
    insert_files: list[dict[str, Any]],
    delete_records: set[int],
):
    connection: Connection
    with closing(sqlite3.connect(database_pathname)) as connection:
        # https://stackoverflow.com/a/52479382
        # https://stackoverflow.com/a/16856730
        # (need to convert into list of tuples of size 1)
        connection.executemany(
            f"delete from {fisher_settings.table_name} where rowid = ?",
            [(d,) for d in delete_records],
        )

        # https://stackoverflow.com/a/32239587
        # https://stackoverflow.com/a/53963137
        connection.executemany(
            f"""
            insert into {fisher_settings.table_name}(directory, name, extension, size, modified_time, version)
            values (:directory, :name, :extension, :size, :modified_time, :version)
            """,
            insert_files,
        )

        connection.commit()

        logger.debug(f"FISHer Updated {update_count} files in database")
        logger.debug(f"FISHer Inserted {len(insert_files) - update_count} files")
        logger.debug(
            f"FISHer Deleted {len(delete_records) - update_count} records from database"
        )


def upsert_records(
    database_pathname: str,
    upsert_files: list[dict[str, Any]],
):
    # Takes 26 seconds for 1000 files (think related to delete and need indexes or something)
    start_time = time.perf_counter()

    connection: Connection
    with closing(sqlite3.connect(database_pathname)) as connection:
        # logger.debug("upsert_records: Before delete")
        # TODO: improve performance issue (first try by refactoring table into data table and separate fts index)
        # This way, can index directory and name columns, which should fix performance issues
        connection.executemany(
            f"""
            delete from {fisher_settings.table_name}
            where directory = :directory
            and name = :name
            """,
            upsert_files,
        )
        # logger.debug("upsert_records: After delete")

        # logger.debug("upsert_records: Before insert")
        connection.executemany(
            f"""
            insert into {fisher_settings.table_name}(directory, name, extension, size, modified_time, version)
            values (:directory, :name, :extension, :size, :modified_time, :version)
            """,
            # size = -1 (special marker to indicate file no longer exists)
            [e for e in upsert_files if e["size"] != -1],
        )
        # logger.debug("upsert_records: After insert")

        connection.commit()

    end_time = time.perf_counter()

    elapsed_time = end_time - start_time
    logger.debug(
        f"upsert_records: Time taken: {elapsed_time:.6f} seconds (files {len(upsert_files)})"
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

    if len(sys.argv) != 2:
        logger.debug("Pass DB pathname as parameter")
        return

    database_pathname = sys.argv[1]

    fisher_lock_path = determine_fisher_lock_path(database_pathname)
    try:
        if fisher_lock_path.exists():
            logger.error(f"Indexer is already running, see {fisher_lock_path}")
            return

        with fisher_lock_path.open("x") as file:
            unlink_fisher_path = fisher_lock_path

            pid = os.getpid()
            file.write(str(pid))

        logger.debug("Database pathname:", database_pathname)
        if not Path(database_pathname).exists():
            create_database(database_pathname)
        index_files(database_pathname)

        # TODO: optimize database after each bulk run
        # https://medium.com/@johnidouglasmarangon/full-text-search-in-sqlite-a-practical-guide-80a69c3f42a4

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    # finally:
    #     input("Press enter to exit")


if __name__ == "__main__":
    main()
