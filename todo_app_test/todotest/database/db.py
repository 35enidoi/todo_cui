import sqlite3
from typing import Any, Union, Optional
from datetime import datetime

from todotest.enum.types import Todo
from todotest.enum.db import VALID_KEYS, VALID_ORDERS


class DataBase:
    def __init__(self, database: str = ":memory:"):
        self.debug = False
        self.__con = sqlite3.connect(database)
        self.__con.execute("""
CREATE TABLE IF NOT EXISTS todos (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL UNIQUE,
description TEXT,
completed INTEGER NOT NULL,
date INTEGER
)
""")

    def __execute(self, sql: str, value: tuple[Any, ...]):
        try:
            cursor = self.__con.execute(sql, value)
            ret = cursor.fetchall()
            cursor.close()
            if self.debug:
                print("="*15)
                print(f"SQL: {sql}")
                print(f"params: {value}")
                print(f"return: {ret}")
                print("="*15)
            self.__con.commit()
            return ret
        except Exception as e:
            print("Error has occured while execute SQL.")
            print(f"SQL: {sql}")
            print(f"params: {value}")
            raise e

    def exist_todo(self,
                   key: str,
                   value: str) -> bool:
        if key not in VALID_KEYS:
            raise ValueError
        else:
            return bool(self.__execute(f"SELECT EXISTS (SELECT 1 FROM todos WHERE {key} = ?)", (value,))[0][0])

    def search_todo(self,
                    key: Optional[tuple[str, str]] = None,  # key, value
                    order: Optional[tuple[str, str]] = None,
                    limit: Optional[int] = None):  # key, order
        add_phrases = []
        add_params = []
        if key is not None:
            # WHERE文
            if key[0] not in VALID_KEYS:
                raise ValueError

            add_phrases.append(f"WHERE {key[0]} = ?")
            add_params.append(key[1])

        if order is not None:
            # ORDER文
            if order[0] not in VALID_KEYS:
                raise ValueError
            elif order[1] not in VALID_ORDERS:
                raise ValueError

            add_phrases.append(f"ORDER BY {order[0]} {order[1]}")

        if limit is not None:
            # LIMIT文
            add_phrases.append("LIMIT ?")
            add_params.append(limit)

        sql = "SELECT * FROM todos " + " ".join(add_phrases)
        return [self.todo_translate(*i) for i in self.__execute(sql, tuple(add_params))]

    def create_todo(self, name: str, description: Union[str, None]):
        self.__execute("INSERT INTO todos VALUES (?, ?, ?, 0, ?)", (None, name, description, int(datetime.now().timestamp())))
        return self.search_todo(key=("name", name))[0]

    def update_todo(self, id: str, **changes: Any):
        if not self.exist_todo("id", id):
            raise ValueError
        elif any((key not in VALID_KEYS for key in changes.keys())):
            raise ValueError
        else:
            add_sql = " ".join((f"{i} = ?" for i in changes.keys()))
            values = tuple(changes.values())

            sql = "UPDATE todos SET " + add_sql + " WHERE id = ?"
            self.__execute(sql, values + (id, ))

    def complete_todo(self, id: int) -> None:
        self.update_todo(id=id, completed=True)

    @staticmethod
    def todo_translate(id: int, name: str, description: Union[str, None], completed: bool, date: int) -> Todo:
        return Todo(id=id, name=name, description=description, completed=bool(completed), date=date)
