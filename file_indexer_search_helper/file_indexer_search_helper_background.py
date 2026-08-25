import logging
import os
import queue
import sqlite3
import sys
import threading
import time
from collections import deque
from collections.abc import Callable, Generator, Iterable
from contextlib import closing, contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("file_indexer_search_helper")
logger.setLevel(logging.DEBUG)

DeleteRecord = tuple[int]
InsertRecord = dict[str, str | int | float]


def setup_logger(database_path: Path):
    handler = logging.FileHandler(
        database_path.with_name("file_indexer_search_helper.log")
    )
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(threadName)s] %(asctime)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@dataclass
class WorkerResult:
    database_changes: deque[DeleteRecord | InsertRecord] = field(
        default_factory=deque, init=False
    )

    delete_counts: deque[int] = field(default_factory=deque, init=False)
    insert_counts: deque[int] = field(default_factory=deque, init=False)
    update_counts: deque[int] = field(default_factory=deque, init=False)


WorkerCallable = Callable[
    [Path, str, list[os.DirEntry], WorkerResult], tuple[int, int, int]
]


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


MIN_CHANGE_COUNT = 1000


def worker(
    database_path: Path,
    dir_queue: queue.Queue[str],
    process_batch_fn: WorkerCallable,
    result: WorkerResult,
    update_queue: queue.Queue[bool],
) -> None:

    delete_count = insert_count = update_count = 0
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
                try:
                    batch_delete_count, batch_insert_count, batch_update_count = (
                        process_batch_fn(database_path, current_dir, files, result)
                    )
                except Exception:
                    # A single problematic directory must not terminate a worker and
                    # leave the directory queue blocked forever.
                    logger.exception("Error processing files in %s", current_dir)
                    continue

                delete_count += batch_delete_count
                insert_count += batch_insert_count
                update_count += batch_update_count

                if len(result.database_changes) > MIN_CHANGE_COUNT:
                    update_queue.put(True)

        except (PermissionError, FileNotFoundError):
            pass
        except OSError:
            logger.exception("Error processing directory: %s", current_dir)
        finally:
            dir_queue.task_done()

    result.delete_counts.append(delete_count)
    result.insert_counts.append(insert_count)
    result.update_counts.append(update_count)

    # 2. Acknowledge the 'None' sentinel task so dir_queue.join() unblocks cleanly
    dir_queue.task_done()


def update_database(
    database_path: Path, result: WorkerResult, min_change_count=MIN_CHANGE_COUNT
):
    # Strictly greater than to handle min_change_count=0 meaning ALL records (final group)
    while len(result.database_changes) > min_change_count:
        database_deletes: deque[DeleteRecord] = deque()
        database_inserts: deque[InsertRecord] = deque()

        count = (
            min_change_count if min_change_count > 0 else len(result.database_changes)
        )
        for _ in range(count):
            change = result.database_changes.popleft()
            if isinstance(change, tuple):  # DeleteRecord
                database_deletes.append(change)
            elif isinstance(change, dict):  # InsertRecord
                database_inserts.append(change)
            else:
                logger.error("Unexpected change: %s", change)

        FISHER_MODEL.bulk_upsert_records(
            database_path, database_deletes, database_inserts
        )


def update_database_worker(
    database_path: Path,
    update_queue: queue.Queue[bool],
    result: WorkerResult,
) -> None:
    for _ in iter(update_queue.get, False):
        try:
            update_database(database_path, result)
        except Exception:
            logger.exception("Error updating the database")
        finally:
            update_queue.task_done()

    # Acknowledge the 'False' sentinel task so update_queue.join() unblocks cleanly
    update_queue.task_done()


def background_index_files(
    database_path: Path,
    root_dir: str,
    process_batch_fn: WorkerCallable,
    num_workers: int = 16,
) -> None:
    dir_queue: queue.Queue[str] = queue.Queue()
    dir_queue.put(root_dir)

    worker_result = WorkerResult()
    update_queue: queue.Queue[bool] = queue.Queue()

    threads = [
        threading.Thread(
            target=worker,
            args=(
                database_path,
                dir_queue,
                process_batch_fn,
                worker_result,
                update_queue,
            ),
            daemon=True,
        )
        for _ in range(num_workers)
    ]

    for t in threads:
        t.start()

    update_thread = threading.Thread(
        target=update_database_worker,
        args=(database_path, update_queue, worker_result),
        daemon=True,
    )
    update_thread.start()

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

    update_queue.join()
    update_queue.put(False)
    update_queue.join()
    update_thread.join()

    # Process remaining changes
    if worker_result.database_changes:
        update_database(database_path, worker_result, 0)

    deletes = sum(worker_result.delete_counts)
    inserts = sum(worker_result.insert_counts)
    updates = sum(worker_result.update_counts)

    logger.info("Deleting  files: %d", deletes)
    logger.info("Inserting files: %d", inserts)
    logger.info("Updating  files: %d", updates)

    # TODO: need to add this after running bulk operations to improve performance and reduce fragmentation (though it may take a long time to run)
    # https://www.techonthenet.com/sqlite/auto_vacuum.php
    # with db_connection_transaction(FISHER_MODEL.database_path) as connection:
    #     connection.execute("VACUUM")


@dataclass(frozen=True)
class FisherModel:
    # database_path: Path

    # Don't add type hint to make immutable (even during instantiation)

    # TODO: may not want to call table "file" since reserved keyword in Microsoft SQL Server T-SQL
    table_name = "file"
    ignore_table_name = "ignore_file"

    select_count = f"select count(1) as count from {table_name}"

    query_by_directory = f"select rowid, directory, name, size, modified_time, version from {table_name} where directory = ?"

    # TODO: does the user ever need to change this (or is this when I update the code?)
    # Store version number in Talon database (via storage) to allow first time upgrades such as dropping table or full reindex
    version = 1

    # Logic from esshop
    FTS_TABLE_NAME = f"{table_name}_fts_idx"

    # Logic from esshop (though not sure if this is the best way to do it)
    # (ideally would have static class variables, though this looked complicated and unsure if needed)

    # TODO: should name be renamed filename? Or no, since table is named "file"?
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

    # https://www.geeksforgeeks.org/sqlite-full-text-search/

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

    CREATE_FULL_TEXT_SEARCH = f"""

    CREATE TABLE IF NOT EXISTS {table_name}(rowid INTEGER PRIMARY KEY, {STORED_COLUMN_NAMES});

    CREATE UNIQUE INDEX IF NOT EXISTS ux__{table_name}__directory__name
    ON {table_name}(directory, name);

    alter table {table_name} add column extension AS (lower(substr(name, instr(name, '.') + 1)));

    CREATE VIRTUAL TABLE IF NOT EXISTS {FTS_TABLE_NAME} USING fts5({FTS_COLUMN_NAMES}, content='{table_name}', tokenize = 'porter trigram');

    {CREATE_TRIGGERS}

    CREATE TABLE IF NOT EXISTS {ignore_table_name}(rowid INTEGER PRIMARY KEY, directory, name);

    CREATE UNIQUE INDEX IF NOT EXISTS ux__{ignore_table_name}__directory__name
    ON {ignore_table_name}(directory, name);
"""

    DELETE_BY_ROWID_HANDLE_IGNORE = f"""
            delete from {table_name} as f
            where f.rowid = ?
            and not exists (
                select 1
                from {ignore_table_name} as i
                where i.directory = f.directory
                and i.name = f.name
            )
            """

    INSERT_RECORDS_HANDLE_IGNORE = f"""
            insert into {table_name}({STORED_COLUMN_NAMES})
            select {NAMED_STORED_COLUMN_NAMES}
            where not exists (
                select 1
                from {ignore_table_name}
                where directory = :directory
                and name = :name
            )
            """

    INSERT_INCREMENTAL_RECORDS = f"""
            insert into {table_name}({STORED_COLUMN_NAMES})
            values ({NAMED_STORED_COLUMN_NAMES})
            """

    DELETE_BY_DIRECTORY_FILENAME = f"""
            delete from {table_name}
            where directory = :directory
            and name = :name
            """

    INSERT_IGNORE_RECORDS = f"""
            insert or ignore into {ignore_table_name}(directory, name)
            values (:directory, :name)
            """

    DELETE_ALL_IGNORE_RECORDS = f"DELETE FROM {ignore_table_name}"

    def create_database(self, database_path: Path):
        with db_connection(database_path) as connection:
            # Specify outside of connection (persistent and only needs to be specified once)
            connection.execute("PRAGMA journal_mode = WAL;")

            with db_transaction(connection):
                connection.executescript(self.CREATE_FULL_TEXT_SEARCH)

    def bulk_upsert_records(
        self,
        database_path: Path,
        delete_files: Iterable[DeleteRecord],
        insert_files: Iterable[InsertRecord],
    ):
        start_time = time.perf_counter()
        with db_connection_transaction(database_path) as connection:
            if delete_files:
                connection.executemany(self.DELETE_BY_ROWID_HANDLE_IGNORE, delete_files)

            if insert_files:
                connection.executemany(self.INSERT_RECORDS_HANDLE_IGNORE, insert_files)

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time

        if elapsed_time >= 1:
            logger.debug("bulk_upsert_records took %.2f seconds.", elapsed_time)


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
    with db_query(database_path, use_row_factory=True) as connection:
        cursor = connection.execute(FISHER_MODEL.query_by_directory, (directory,))
        rows = cursor.fetchall()

    return {row["name"]: dict(row) for row in rows}


def process_file_group(
    database_path: Path,
    dir_path: str,
    files: list[os.DirEntry],
    worker_result: WorkerResult,
) -> tuple[int, int, int]:

    existing_records = query_existing_files(database_path, dir_path)
    files_to_delete = set(existing_records.keys())
    changes: list[DeleteRecord | InsertRecord] = []
    insert_count = 0
    update_count = 0

    for file in files:
        try:
            file_detail = create_file_dictionary(dir_path, file)
        except OSError:
            logger.exception("Error processing file: %s", file)
            continue

        key = file.name

        # TODO: could remove instead, which also removes need for files_to_delete
        existing_record = existing_records.get(key)
        if not existing_record:
            changes.append(file_detail)
            insert_count += 1
            continue

        files_to_delete.discard(key)
        if (
            file_detail["modified_time"] != existing_record["modified_time"]
            or file_detail["size"] != existing_record["size"]
            or file_detail["version"] != existing_record["version"]
        ):
            # Update will perform delete first
            changes.append((existing_record["rowid"],))
            changes.append(file_detail)
            update_count += 1

    delete_files: list[DeleteRecord] = [
        (record["rowid"],)  # Intentional tuple for SQLite executemany
        for record in existing_records.values()
        if record["name"] in files_to_delete
    ]
    worker_result.database_changes.extend(delete_files)
    worker_result.database_changes.extend(changes)

    return (len(delete_files), insert_count, update_count)


# This handles the incremental indexing
def upsert_records(database_path: Path, upsert_files: list[dict[str, Any]]):
    start_time = time.perf_counter()

    # size = -1 (special marker to indicate file no longer exists)
    insert_files = [e for e in upsert_files if e["size"] != -1]
    is_bulk_running = determine_fisher_lock_path(database_path).exists()

    with db_connection_transaction(database_path) as connection:
        # These files are being handled by the incremental and can be ignored by the bulk
        if is_bulk_running:
            connection.executemany(FISHER_MODEL.INSERT_IGNORE_RECORDS, insert_files)

        connection.executemany(FISHER_MODEL.DELETE_BY_DIRECTORY_FILENAME, upsert_files)
        connection.executemany(FISHER_MODEL.INSERT_INCREMENTAL_RECORDS, insert_files)

    end_time = time.perf_counter()

    # Will display in Talon log
    # TODO: should I put this in the background logs or Talon logs
    # (this only is run during incremental by Talon)
    logger.debug(
        "FISHer upsert_records: Time taken: %.6f seconds (files %d)",
        end_time - start_time,
        len(upsert_files),
    )


def bulk_cleanup(database_path: Path):
    with db_connection_transaction(database_path) as connection:
        connection.execute(FISHER_MODEL.DELETE_ALL_IGNORE_RECORDS)


@contextmanager
def db_query(
    database_path: Path, use_row_factory=False
) -> Generator[sqlite3.Connection, None, None]:
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute("PRAGMA synchronous = NORMAL;")

        # Memory-map up to 256MB of the DB file
        connection.execute("PRAGMA mmap_size = 268435456;")

        if use_row_factory:
            connection.row_factory = sqlite3.Row

        yield connection


@contextmanager
def db_connection(database_path: Path) -> Generator[sqlite3.Connection, None, None]:
    """
    Manages a SQLite connection safely.

    Automatically ensures the database connection closes properly.
    """
    with closing(sqlite3.connect(database_path, timeout=30)) as connection:
        connection.execute("PRAGMA synchronous = NORMAL;")
        connection.execute("PRAGMA cache_size = -64000;")  # 64MB cache

        yield connection


@contextmanager
def db_transaction(
    connection: sqlite3.Connection,
) -> Generator[sqlite3.Connection, None, None]:
    """Manages an IMMEDIATE transaction using native sqlite3 rollback/commit logic."""
    if not connection.in_transaction:
        connection.execute("BEGIN IMMEDIATE;")

    with connection:
        yield connection


@contextmanager
def db_connection_transaction(
    database_path: Path,
) -> Generator[sqlite3.Connection, None, None]:

    with db_connection(database_path) as connection, db_transaction(connection):
        yield connection


def determine_fisher_lock_path(database_path: Path) -> Path:
    return database_path.with_name("FISHer.lck")


def main():
    if len(sys.argv) != 2:
        logger.debug("Pass DB path as parameter")
        return

    start_time = time.perf_counter()
    target_dir = "C:\\"

    database_path = Path(sys.argv[1])
    setup_logger(database_path)

    fisher_lock_path = determine_fisher_lock_path(database_path)
    unlink_fisher_lock_path = None
    try:
        try:
            with fisher_lock_path.open("x") as file:
                unlink_fisher_lock_path = fisher_lock_path

                pid = os.getpid()
                file.write(str(pid))
        except OSError:
            logger.error("Indexer is already running, see %s", fisher_lock_path)
            return

        logger.debug("Database path: %s", database_path)
        if not database_path.exists():
            FISHER_MODEL.create_database(database_path)

        background_index_files(database_path, target_dir, process_file_group)
        unlink_fisher_lock_path.unlink(missing_ok=True)

        # Done after lock is released, since while lock exists, could still add records to table
        # TODO: is this the correct place for this?
        bulk_cleanup(database_path)

        end_time = time.perf_counter()

        logger.debug("Completed processing in %.2f seconds.", end_time - start_time)

        # TODO: optimize database after each bulk run
        # https://medium.com/@johnidouglasmarangon/full-text-search-in-sqlite-a-practical-guide-80a69c3f42a4
    finally:
        if unlink_fisher_lock_path:
            unlink_fisher_lock_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
