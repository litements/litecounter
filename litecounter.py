import sqlite3
from contextlib import contextmanager
import pprint

__version__ = "0.1.1"

# SQLite works better in autocommit mode when using short DML (INSERT / UPDATE / DELETE) statements
# source: https://charlesleifer.com/blog/going-fast-with-sqlite-and-python/
@contextmanager
def transaction(conn: sqlite3.Connection):
    # We must issue a "BEGIN" explicitly when running in auto-commit mode.
    conn.execute("BEGIN")
    try:
        # Yield control back to the caller.
        yield conn
    except:
        conn.rollback()  # Roll back all changes if an exception occurs.
        raise
    else:
        conn.commit()


class SQLCounter:
    def __init__(
        self, dbname, check_same_thread=False, fast=True, **kwargs,
    ):
        self.dbname = dbname
        self.conn = sqlite3.connect(
            self.dbname,
            check_same_thread=check_same_thread,
            isolation_level=None,
            **kwargs,
        )

        with transaction(self.conn) as c:

            c.execute(
                "CREATE TABLE IF NOT EXISTS Counter (key text NOT NULL PRIMARY KEY, value integer)"
            )

        if fast:
            self.conn.execute("PRAGMA journal_mode = 'WAL';")
            self.conn.execute("PRAGMA temp_store = 2;")
            self.conn.execute("PRAGMA synchronous = 1;")
            self.conn.execute(f"PRAGMA cache_size = {-1 * 64_000};")

    def incr(self, key):
        self.conn.execute(
            "INSERT INTO Counter VALUES (?, 1) ON CONFLICT(key) DO UPDATE SET value = value + 1",
            (key,),
        )
        return

    def decr(self, key):
        self.conn.execute(
            "INSERT INTO Counter VALUES (?, -1) ON CONFLICT(key) DO UPDATE SET value = value - 1",
            (key,),
        )
        return

    def count(self, key):
        c = self.conn.execute("SELECT value FROM Counter WHERE Key=?", (key,))
        row = c.fetchone()
        if row is None:
            return None
        return row[0]

    def zero(self, key):
        self.conn.execute(
            "INSERT INTO Counter VALUES (?, 0) ON CONFLICT(key) DO UPDATE SET value = 0",
            (key,),
        )
        return

    def delete(self, key):
        """
        Delete counter key, if the key does NOT exist
        it will just ignore it (no exceptions raised)
        """

        self.conn.execute("DELETE FROM Counter WHERE key=?", (key,))

    def __repr__(self):
        return f"{type(self).__name__}(dbname={self.dbname!r}, items={pprint.pformat(self.conn.execute('SELECT * FROM Counter').fetchall())})"

    def vacuum(self):
        self.conn.execute("VACUUM;")

    def close(self):
        self.conn.close()
