import sqlite3
from tempfile import TemporaryFile
from unittest import TestCase
from os import remove as os_file_remove
from random import choices
from string import digits, ascii_letters

from todotest.database import DataBase
from todotest.enum.types import Todo, Union


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
    @property
    def random_name(self) -> str:
        return "".join(choices(ascii_letters, k=20))

    @property
    def random_description(self) -> str:
        return "".join(choices(ascii_letters, k=100))

    @property
    def random_time(self) -> str:
        return "".join(choices(digits, k=8))

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

    @staticmethod
    def sql_create_todo(path: str):
        name = "".join(choices(ascii_letters, k=20))
        descriprion = "".join(choices(ascii_letters, k=100))
        time = "".join(choices(digits, k=8))
        with SQLChecker(path) as sql:
            sql.execute("INSERT INTO todos VALUES (?, ?, ?, 0, ?)", None, name, descriprion, time)
            todo = sql.execute("SELECT * FROM todos WHERE name = ?", name)[0]

        return TestCasewithTmpDB.todo_translate(*todo)

    @staticmethod
    def todo_translate(id: int, name: str, description: Union[str, None], completed: bool, date: int) -> Todo:
        return Todo(id=id, name=name, description=description, completed=bool(completed), date=date)
