import logging
import os
import sqlite3
import time
from collections import defaultdict
from operator import itemgetter
from pathlib import Path
from sqlite3 import Connection

from talon import Module, actions, app, cron, imgui

mod = Module()

# TODO: Have cron job index (with option to index on command)
should_index_files_on_ready = True

# TODO: add support for full reindex via voice (set all version numbers to 0)
# (dropping table should only be needed in rare updates when table structure changes)
should_drop_table = False
should_perform_full_reindex = False

# Directories containing the following parts will NOT be indexed
# CacheStorage / "Code Cache" is used by Google Chrome (and other programs)
# htmlcache is used by Steam
# CachedData is used by VSCode
# History is used by VSCode (noticed VSCode has History folder with 1500 files across many folders)

# TODO: move to talon_list file
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
}

# TODO: move to talon_list file
ignore_directories = {
    r"C:\Users\cross\AppData\Local\PowerToys",
    r"C:\Windows\WinSxS\Manifests",
    r"C:\Program Files (x86)\Steam\steamapps\common",
}

# Use map for better performance
ignore_directory_parts_map = {e.lower() for e in ignore_directory_parts}

ignore_directories_map = {e.lower() for e in ignore_directories}

# Runtime priorities of file extension
# (can be changed on-the-fly without reindex, since passed into SQL query)
# TODO: move to talon_list file
priority_file_extensions = ["exe", "lnk", "md", "talon", "chm"]

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

# TODO: support deleted directories (should delete from database)
# For example, if doesn't iterate due to ignoring directory

# https://github.com/sqlalchemy/sqlalchemy/discussions/9466#discussioncomment-5273152


# Treat index as priority (so lower index has higher priority)
# If not in list, has lowest priority
# Join string helps make SQL pretty formatted (useful when debugging)
priority_file_extensions_sql = ",\n    ".join(
    [f"('{e}', {i})" for i, e in enumerate(priority_file_extensions)]
)

COUNT_BY_DIRECTORY = f"""
select f.directory, count(1) as count
from {TABLE_NAME} f
group by f.directory
order by count(1) desc
limit 25
"""

COUNT_BY_EXTENSION = f"""
select f.directory, f.extension, count(1) as count
from {TABLE_NAME} f
group by f.directory, f.extension
order by count(1) desc
limit 25
"""


# Note: 'OR' is case-sensitive to match as operator
# PYTHON_JAVA_FULL_TEXT_SEARCH = f"""
# SELECT *
# FROM {TABLE_NAME}('python OR java');
# """


@imgui.open()
def fishy_gui_search_results(gui: imgui.GUI):
    gui.text("Search Results")
    gui.line()
    search_results = search("freecom*")
    for i, search_result in enumerate(search_results):
        directory = search_result["directory"]
        filename = search_result["filename"]

        gui.text(f"{i+1:02d}: {directory}")
        gui.text(f"{filename}")

        gui.spacer()

    if gui.button("Fishy"):
        actions.user.fishy_hide_search_results()


def create_file_dictionary(directory: str, filename: str):
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


def create_database(database_pathname):
    with sqlite3.connect(database_pathname) as connection:
        if should_drop_table:
            connection.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
            connection.commit()

        connection.execute(CREATE_VIRTUAL_TABLE)
        connection.commit()
        logging.debug(
            f"FISHy Existing: {connection.execute(SELECT_COUNT).fetchone()[0]}"
        )

        # https://www.techonthenet.com/sqlite/auto_vacuum.php
        connection.execute("VACUUM")
        connection.commit()

        if should_perform_full_reindex:
            connection.execute(f"update {TABLE_NAME} set version = 0")
            connection.commit()


def determine_filename(name: str, extension: str):
    return name + ("." if extension != "" and extension != "." else "") + extension


# TODO: break into smaller functions
def index_files():
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
    update_count = 0

    # Create multimap from directory -> files
    # https://stackoverflow.com/a/1731989
    existing_files = defaultdict(list)

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

    logging.debug(f"FISHy walk: {root_path}")

    # TODO: replace path.walk with os.walk
    # (since Talon is currently on Python 3.11 and path.walk was added in 3.12)
    for directory, dirs, files in os.walk(root_path):
        if dirs:
            # https://stackoverflow.com/a/10620948
            dirs[:] = [
                dir for dir in dirs if dir.lower() not in ignore_directory_parts_map
            ]
            dirs[:] = [
                dir
                for dir in dirs
                if os.path.join(directory, dir).lower() not in ignore_directories_map
            ]

        if not files:
            continue

        files.sort()

        if directory in existing_files:
            existing_rows = existing_files.pop(directory)
            existing_rows.sort(key=itemgetter("filename"))
        else:
            existing_rows = []

        existing_index = 0
        pathwalk_index = 0

        while existing_index < len(existing_rows) or pathwalk_index < len(files):
            if existing_index >= len(existing_rows):
                # "file" is a new file in the directory and should be INSERTED
                insert_files.append(
                    create_file_dictionary(directory, files[pathwalk_index])
                )
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
                insert_files.append(
                    create_file_dictionary(directory, files[pathwalk_index])
                )
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

                    update_count += 1
                    insert_files.append(file_dictionary)

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

    # TODO: convert code from SQLAlchemy to sqlite3
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

        logging.debug(f"FISHy Updated {update_count} files in database")
        logging.debug(
            f"FISHy Inserted {len(insert_files) - update_count} files from {str(root_path)}"
        )
        logging.debug(
            f"FISHy Deleted {len(delete_records) - update_count} records from database"
        )

    end_time = time.time()

    # get the execution time
    elapsed_time = end_time - start_time
    logging.debug(f"FISHy Execution time: {elapsed_time} seconds")


# TODO: show only 10 results and show directory / filename on separate lines with spacer?
# Enable paging (like done for help)
# This may help make results easier to read
def search(FULL_TEXT_SEARCH_TEXT):
    # Note: -e.priority desc will sort NULL / no priority last (since descending)
    # Negative ensures that, for example, priority 0 comes before priority 1
    # (since 0 > -1, so when sorting descending will be earlier)
    FULL_TEXT_SEARCH = f"""
    with extension_xref (extension, priority) as
    (values
        {priority_file_extensions_sql}
    )
    SELECT rowid, e.priority, f.directory, f.name, f.extension, f.size, f.modified_time
    FROM {TABLE_NAME}("{FULL_TEXT_SEARCH_TEXT}") f
    left join extension_xref e on e.extension = f.extension
    order by f.rank, -e.priority desc
    limit 10
    """

    search_results = []

    with sqlite3.connect(database_pathname) as connection:
        cursor = connection.execute(FULL_TEXT_SEARCH)
        for row in cursor:
            row_dict = {cursor.description[i][0]: e for i, e in enumerate(row)}
            row_dict["filename"] = determine_filename(
                row_dict["name"], row_dict["extension"]
            )
            # logging.info(os.path.join(row_dict["directory"], row_dict["filename"]))
            search_results.append(row_dict)

        return search_results

        # print()
        # print("Directories:")
        # for result in connection.execute(COUNT_BY_DIRECTORY).fetchall():
        #     print(result)

        # print()
        # print("Extensions:")
        # for result in connection.execute(COUNT_BY_EXTENSION).fetchall():
        #     print(result)


def on_ready():
    global database_pathname

    # TODO: have user setting
    # (if relative path, make relative to talon user; if absolute, should override, please test)
    database_pathname = os.path.join(
        actions.path.talon_user(), "file_indexer_search_helper.db"
    )
    create_database(database_pathname)

    # TODO: Run indexing on separate thread
    # (so doesn't cause imgui to wait for indexing to finish before responds)
    # TODO: use subprocess (such as system_command_nb)
    # https://talonvoice.slack.com/archives/C7ENXA7C4/p1719603988033169

    if should_index_files_on_ready:
        cron.after("0s", index_files)

    cron.interval("600s", index_files)

    # search("ada dis*")


app.register("ready", on_ready)


@mod.action_class
class Actions:
    def fishy_hide_search_results():
        """Hides the GUI for fishy search results"""
        fishy_gui_search_results.hide()

    def fishy_show_search_results():
        """Shows the GUI for fishy search results"""
        fishy_gui_search_results.show()

    def fishy_toggle_search_results():
        """Toggles the GUI for fishy search results"""
        if fishy_gui_search_results.showing:
            actions.user.fishy_hide_search_results()
        else:
            actions.user.fishy_show_search_results()
