import sqlite3
import pathlib
from contextlib import contextmanager
import pprint

__version__ = "0.2"

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
        self, filename_or_conn=None, memory=False, **kwargs,
    ):
        assert (filename_or_conn is not None and not memory) or (
            filename_or_conn is None and memory
        ), "Either specify a filename_or_conn or pass memory=True"
        if memory or filename_or_conn == ":memory:":
            self.conn = sqlite3.connect(":memory:", isolation_level=None, **kwargs)
        elif isinstance(filename_or_conn, (str, pathlib.Path)):
            self.conn = sqlite3.connect(
                str(filename_or_conn), isolation_level=None, **kwargs
            )
        else:
            self.conn = filename_or_conn
            self.conn.isolation_level = None

        with transaction(self.conn) as c:

            c.execute(
                "CREATE TABLE IF NOT EXISTS Counter (key text NOT NULL PRIMARY KEY, value integer)"
            )

        # if fast:
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
        return f"{type(self).__name__}(Connection={self.conn!r}, items={pprint.pformat(self.conn.execute('SELECT * FROM Counter').fetchall())})"

    def vacuum(self):
        self.conn.execute("VACUUM;")

    def close(self):
        self.conn.close()
