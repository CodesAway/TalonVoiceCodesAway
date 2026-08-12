import logging
import os
import queue
import sqlite3
import sys
import threading
import time
from collections import deque
from collections.abc import Callable, Iterable
from contextlib import closing
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("file_indexer_search_helper")
logger.setLevel(logging.DEBUG)

DeleteRecord = tuple[int]
InsertRecord = dict[str, str | int | float]


@dataclass
class WorkerResult:
    database_deletes: deque[DeleteRecord] = field(default_factory=deque, init=False)
    database_inserts: deque[InsertRecord] = field(default_factory=deque, init=False)
    update_counts: deque[int] = field(default_factory=deque, init=False)


WorkerCallable = Callable[[Path, str, list[os.DirEntry], WorkerResult], int]


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
}

ignore_directory_parts_norm = {os.path.normcase(e) for e in ignore_directory_parts}

ignore_directories_norm = {
    os.path.normcase(os.path.normpath(os.path.expandvars(e)))
    for e in ignore_directories
}


def should_ignore_directory(directory: os.DirEntry) -> bool:
    return (
        os.path.normcase(directory.name) in ignore_directory_parts_norm
        or os.path.normcase(os.path.normpath(directory.path)) in ignore_directories_norm
    )


def worker(
    database_path: Path,
    dir_queue: queue.Queue[str],
    process_batch_fn: WorkerCallable,
    result: WorkerResult,
) -> None:

    update_count = 0
    # 1. Use sentinel iterator: loops until queue_get() returns None
    for current_dir in iter(dir_queue.get, ""):
        try:
            files = []
            with os.scandir(current_dir) as entries:
                for entry in entries:
                    if entry.is_file(follow_symlinks=False):
                        files.append(entry)
                    elif entry.is_dir(follow_symlinks=False):  # noqa: SIM102
                        if not should_ignore_directory(entry):
                            dir_queue.put(entry.path)

            # TODO: What if an error is thrown, should I still handle the files?
            # TODO: may need to multiprocess the process_batch_fn if it is CPU bound, but that would require more complex design
            if files:
                update_count += process_batch_fn(
                    database_path, current_dir, files, result
                )

        except (PermissionError, FileNotFoundError):
            pass
        except OSError as e:
            logger.error(f"Error processing {current_dir}: {e}")
        finally:
            dir_queue.task_done()

    result.update_counts.append(update_count)

    # 2. Acknowledge the 'None' sentinel task so dir_queue.join() unblocks cleanly
    dir_queue.task_done()


def fast_parallel_walk(
    database_path: Path,
    root_dir: str,
    process_batch_fn: WorkerCallable,
    num_workers: int = 16,
) -> WorkerResult:

    dir_queue: queue.Queue[str] = queue.Queue()
    dir_queue.put(root_dir)

    worker_result = WorkerResult()

    threads = [
        threading.Thread(
            target=worker,
            args=(database_path, dir_queue, process_batch_fn, worker_result),
            daemon=True,
        )
        for _ in range(num_workers)
    ]

    for t in threads:
        t.start()

    # 1. Wait until all active directories in the tree are fully scanned
    dir_queue.join()

    # 2. Push one shutdown sentinel per worker thread
    for _ in range(num_workers):
        dir_queue.put("")

    # 3. Wait for workers to pull sentinels and finish exiting
    dir_queue.join()

    # 4. Join threads for clean thread stack teardown
    for t in threads:
        t.join()

    return worker_result


@dataclass(frozen=True)
class FisherModel:
    # database_path: Path

    # Don't add type hint to make immutable (even during instantiation)

    table_name = "file"

    select_count = f"select count(1) as count from {table_name}"

    query_by_directory = f"select rowid, directory, name, size, modified_time, version from {table_name} where directory = ?"

    # TODO: does the user ever need to change this (or is this when I update the code?)
    # Store version number in Talon database (via storage) to allow first time upgrades such as dropping table or full reindex
    version = 1

    # Logic from esshop
    FTS_TABLE_NAME = f"{table_name}_fts_idx"

    # Logic from esshop (though not sure if this is the best way to do it)
    # (ideally would have static class variables, though this looked complicated and unsure if needed)

    STORED_COLUMNS = ("directory", "name", "size", "modified_time", "version")

    GENERATED_COLUMNS = ("extension",)
    COLUMNS = STORED_COLUMNS + GENERATED_COLUMNS

    UNINDEXED_COLUMNS = ("size", "modified_time", "version", "extension")

    # Workaround suggested by GitHub Copilot (since tuple(generator) doesn't work referencing UNINDEXED_COLUMNS)
    # FTS_COLUMNS = tuple(c for c in COLUMNS if c not in UNINDEXED_COLUMNS) # Results in compiler error
    _fts_columns = []  # noqa: RUF012
    for column_name in COLUMNS:
        if column_name not in UNINDEXED_COLUMNS:
            _fts_columns.append(column_name)
    FTS_COLUMNS = tuple(_fts_columns)
    del _fts_columns

    STORED_COLUMN_NAMES = ",".join([column_name for column_name in STORED_COLUMNS])
    NAMED_STORED_COLUMN_NAMES = ",".join(
        [":" + column_name for column_name in STORED_COLUMNS]
    )

    FTS_COLUMN_NAMES = ",".join(column_name for column_name in FTS_COLUMNS)
    OLD_FTS_COLUMN_NAMES = ",".join("old." + column_name for column_name in FTS_COLUMNS)
    NEW_FTS_COLUMN_NAMES = ",".join("new." + column_name for column_name in FTS_COLUMNS)

    DROP_TRIGGERS = f"""
    DROP TRIGGER IF EXISTS {table_name}_delete;
    DROP TRIGGER IF EXISTS {table_name}_insert;
    DROP TRIGGER IF EXISTS {table_name}_update;
    """

    # https://www.geeksforgeeks.org/sqlite-full-text-search/
    REINDEX_FTS = f"""
    DROP TABLE IF EXISTS {FTS_TABLE_NAME};
    CREATE VIRTUAL TABLE IF NOT EXISTS {FTS_TABLE_NAME} USING fts5({FTS_COLUMN_NAMES}, content='{table_name}', tokenize = 'porter trigram');
    INSERT INTO {FTS_TABLE_NAME}({FTS_TABLE_NAME}) VALUES('rebuild');
    """

    # Is there a better way to write these
    # Reference https://medium.com/@johnidouglasmarangon/full-text-search-in-sqlite-a-practical-guide-80a69c3f42a4
    # (though the update looks wrong in the article...why is it an insert?)
    CREATE_TRIGGERS = f"""
    CREATE TRIGGER {table_name}_delete AFTER DELETE ON {table_name} BEGIN
        INSERT INTO {FTS_TABLE_NAME}({FTS_TABLE_NAME}, rowid, {FTS_COLUMN_NAMES}) VALUES('delete', old.rowid, {OLD_FTS_COLUMN_NAMES});
    END;
    CREATE TRIGGER {table_name}_insert AFTER INSERT ON {table_name} BEGIN
        INSERT INTO {FTS_TABLE_NAME}(rowid, {FTS_COLUMN_NAMES}) VALUES (new.rowid, {NEW_FTS_COLUMN_NAMES});
    END;
    CREATE TRIGGER {table_name}_update AFTER UPDATE ON {table_name} BEGIN
        INSERT INTO {FTS_TABLE_NAME}({FTS_TABLE_NAME}, rowid, {FTS_COLUMN_NAMES}) VALUES('delete', old.rowid, {OLD_FTS_COLUMN_NAMES});
        INSERT INTO {FTS_TABLE_NAME}(rowid, {FTS_COLUMN_NAMES}) VALUES (new.rowid, {NEW_FTS_COLUMN_NAMES});
    END;
    """

    # AI suggested for performance, though not sure if needed (and may be slower in some cases)
    # WAL mode persists across connections once set
    # Write-Ahead Logging allows multiple threads to read concurrently while a single thread writes
    #     PRAGMA journal_mode = WAL;
    #     PRAGMA synchronous = NORMAL;

    # TODO: can add generated columns after drop triggers
    # (remember to first drop columns in reverse order of creation) (not needed since creating table)
    CREATE_FULL_TEXT_SEARCH = f"""
    DROP TABLE IF EXISTS {table_name};
    CREATE TABLE IF NOT EXISTS {table_name}(rowid INTEGER PRIMARY KEY, {STORED_COLUMN_NAMES});

    CREATE UNIQUE INDEX IF NOT EXISTS ux__{table_name}__directory__name
    ON {table_name}(directory, name);

    {DROP_TRIGGERS}

    alter table {table_name} add column extension AS (lower(substr(name, instr(name, '.') + 1)));

    {REINDEX_FTS}

    {CREATE_TRIGGERS}
"""

    DELETE_BY_ROWID = f"delete from {table_name} where rowid = ?"
    INSERT_RECORDS = f"""
            insert into {table_name}({STORED_COLUMN_NAMES})
            values ({NAMED_STORED_COLUMN_NAMES})
            """

    def create_database(self, database_path: Path):
        with (
            closing(sqlite3.connect(database_path)) as connection,
            connection,  # Necessary for transaction management
        ):
            connection.executescript(self.CREATE_FULL_TEXT_SEARCH)

    def upsert_records(
        self,
        database_path: Path,
        delete_files: Iterable[DeleteRecord],
        insert_files: Iterable[InsertRecord],
    ):
        with (
            closing(sqlite3.connect(database_path)) as connection,
            connection,  # Necessary for transaction management (commits when closing)
        ):
            connection.executemany(self.DELETE_BY_ROWID, delete_files)
            connection.executemany(self.INSERT_RECORDS, insert_files)


FISHER_MODEL = FisherModel()


def create_path_dictionary(path: Path) -> InsertRecord:
    size = -1
    modified_time = -1

    if path.exists():
        try:
            stat_result = path.stat(follow_symlinks=False)
            size = stat_result.st_size
            modified_time = stat_result.st_mtime
        except OSError as e:
            logger.error(e)

    return {
        "directory": str(path.parent),
        "name": path.name,
        "size": size,
        "modified_time": modified_time,
        "version": FISHER_MODEL.version,
    }


def create_file_dictionary(directory: str, file: os.DirEntry) -> InsertRecord:
    size = file.stat().st_size
    modified_time = file.stat().st_mtime

    return {
        "directory": directory,
        "name": file.name,
        "size": size,
        "modified_time": modified_time,
        "version": FISHER_MODEL.version,
    }


def query_existing_files(
    database_path: Path, directory: str
) -> dict[str, dict[str, Any]]:
    with closing(sqlite3.connect(database_path)) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.execute(FISHER_MODEL.query_by_directory, (directory,))
        return {row["name"]: dict(row) for row in cursor}


def process_file_group(
    database_path: Path,
    dir_path: str,
    files: list[os.DirEntry],
    worker_result: WorkerResult,
) -> int:

    existing_records = query_existing_files(database_path, dir_path)
    files_to_delete = set(existing_records.keys())
    insert_files: list[InsertRecord] = []
    update_count = 0

    for file in files:
        try:
            file_detail = create_file_dictionary(dir_path, file)
        except OSError as e:
            logger.error(f"An error occurred: {e}")
            continue

        key = file.name

        existing_record = existing_records.get(key)
        if not existing_record:
            insert_files.append(file_detail)
            continue

        if (
            file_detail["modified_time"] != existing_record["modified_time"]
            or file_detail["size"] != existing_record["size"]
            or file_detail["version"] != existing_record["version"]
        ):
            # Update will perform delete first (key remains in files_to_delete)
            insert_files.append(file_detail)
            update_count += 1
        else:
            files_to_delete.discard(key)

    delete_files: list[DeleteRecord] = [
        (record["rowid"],)  # Intentional tuple for SQLite executemany
        for record in existing_records.values()
        if record["name"] in files_to_delete
    ]

    worker_result.database_deletes.extend(delete_files)
    worker_result.database_inserts.extend(insert_files)

    return update_count


def index_files(
    database_path: Path, root_dir: str, process_batch_fn: WorkerCallable
) -> None:
    result = fast_parallel_walk(database_path, root_dir, process_batch_fn)
    updates = sum(result.update_counts)

    logger.info(f"Deleting  files: {len(result.database_deletes) - updates}")
    logger.info(f"Inserting files: {len(result.database_inserts) - updates}")
    logger.info(f"Updating  files: {updates}")

    FISHER_MODEL.upsert_records(
        database_path, result.database_deletes, result.database_inserts
    )

    # TODO: need to add this after running bulk operations to improve performance and reduce fragmentation (though it may take a long time to run)
    # https://www.techonthenet.com/sqlite/auto_vacuum.php
    # with closing(sqlite3.connect(FISHER_MODEL.database_path)) as connection, connection:
    #     connection.execute("VACUUM")


# TODO: this handles the incremental indexing
def upsert_records(database_path: Path, upsert_files: list[dict[str, Any]]):
    # Takes 26 seconds for 1000 files (think related to delete and need indexes or something)
    start_time = time.perf_counter()

    with closing(sqlite3.connect(database_path)) as connection, connection:
        # logger.debug("upsert_records: Before delete")
        # TODO: improve performance issue (first try by refactoring table into data table and separate fts index)
        # This way, can index directory and name columns, which should fix performance issues
        connection.executemany(
            f"""
            delete from {FISHER_MODEL.table_name}
            where directory = :directory
            and name = :name
            """,
            upsert_files,
        )
        # logger.debug("upsert_records: After delete")

        # logger.debug("upsert_records: Before insert")
        connection.executemany(
            FISHER_MODEL.INSERT_RECORDS,
            # size = -1 (special marker to indicate file no longer exists)
            [e for e in upsert_files if e["size"] != -1],
        )
        # logger.debug("upsert_records: After insert")

        connection.commit()

    end_time = time.perf_counter()

    elapsed_time = end_time - start_time
    # Will display in Talon log
    # TODO: should I put this in the background logs or Talon logs
    # (this only is run during incremental by Talon)
    logger.debug(
        f"FISHer upsert_records: Time taken: {elapsed_time:.6f} seconds (files {len(upsert_files)})"
    )


def determine_fisher_lock_path(database_path: Path) -> Path:
    return database_path.with_name("FISHer.lck")


def main():
    if len(sys.argv) != 2:
        logger.debug("Pass DB path as parameter")
        return

    start_time = time.perf_counter()
    target_dir = "C:\\"

    database_path = Path(sys.argv[1])

    file_handler = logging.FileHandler(
        database_path.with_name("file_indexer_search_helper.log")
    )
    # TODO: write to console during testing
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(threadName)s] %(asctime)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # database_path.unlink(missing_ok=True)

    fisher_lock_path = determine_fisher_lock_path(database_path)
    unlink_fisher_lock_path = None
    try:
        if fisher_lock_path.exists():
            logger.error(f"Indexer is already running, see {fisher_lock_path}")
            return

        with fisher_lock_path.open("x") as file:
            unlink_fisher_lock_path = fisher_lock_path

            pid = os.getpid()
            file.write(str(pid))

        logger.debug(f"Database path: {database_path}")
        if not database_path.exists():
            FISHER_MODEL.create_database(database_path)

        index_files(database_path, target_dir, process_file_group)

        end_time = time.perf_counter()

        logger.debug(f"Completed processing in {end_time - start_time:.2f} seconds.")

        # TODO: optimize database after each bulk run
        # https://medium.com/@johnidouglasmarangon/full-text-search-in-sqlite-a-practical-guide-80a69c3f42a4
    except (OSError, ValueError) as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if unlink_fisher_lock_path:
            unlink_fisher_lock_path.unlink()


if __name__ == "__main__":
    main()
