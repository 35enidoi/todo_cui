import sqlite3
from typing import Optional


class SQLChecker:
    def __init__(self, dbpath: Optional[str] = ":memory:"):
        self.path = dbpath
        self.con = sqlite3.connect(dbpath)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.con.commit()
        self.con.close()
        return

    def execute(self, sql: str, *params):
        cursor = self.con.cursor()
        cursor.execute(sql, params)
        ret = cursor.fetchall()
        cursor.close()
        return ret
