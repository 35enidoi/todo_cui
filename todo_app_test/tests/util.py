import sqlite3
from tempfile import TemporaryFile
from unittest import TestCase
from os import remove as os_file_remove

from todotest.database import DataBase


class SQLChecker:
    def __init__(self, dbpath: str):
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


class TestCasewithTmpDB(TestCase):
    @classmethod
    def setUpClass(cls):
        # tmpファイルの作成
        cls.tmp_file = TemporaryFile(delete=False)
        cls.tmp_file.close()

    @classmethod
    def tearDownClass(cls):
        # tmpファイル削除
        os_file_remove(cls.tmp_file.name)
        del cls.tmp_file

    def setUp(self):
        self.db = DataBase(self.tmp_file.name)

    def tearDown(self):
        del self.db
        # ファイルの初期化
        open(self.tmp_file.name, mode="wb").close()
