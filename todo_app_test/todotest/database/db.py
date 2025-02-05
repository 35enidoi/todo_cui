import sqlite3
from typing import Any, Union, Optional
from datetime import datetime

from todotest.types import Todo


class DataBase:
    def __init__(self, database: str = ":memory:"):
        self.__con = sqlite3.connect(database)
        self.__con.execute("""
CREATE TABLE IF NOT EXISTS todos (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL UNIQUE,
description TEXT,
is_completed INTEGER NOT NULL,
unix_time INTEGER
)
""")

    def __execute(self, sql: str, value: tuple[Any, ...]):
        try:
            cursor = self.__con.execute(sql, value)
            ret = cursor.fetchall()
            cursor.close()
            return ret
        except Exception as e:
            print("Error has occured while execute SQL.")
            print(f"SQL: {sql}")
            print(f"params: {value}")
            raise e

    def _search_todo(self,
                     key: Optional[tuple[str, str]] = None,  # key, value
                     order: Optional[tuple[str, str]] = None,
                     limit: Optional[int] = None):  # key, order
        VALID_KEYS = {"id", "name", "is_completed", "description", "unix_time"}
        ORDERS = {"ASC", "DESC"}
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
            elif order[1] not in ORDERS:
                raise ValueError

            add_phrases.append(f"ORDER BY {order[0]} {order[1]}")

        if limit is not None:
            # LIMIT文
            add_phrases.append("LIMIT ?")
            add_params.append(limit)

        sql = "SELECT * FROM todos " + " ".join(add_phrases)
        return [self.todo_translate(*i) for i in self.__execute(sql, tuple(add_params))]

    def search_todo_from_id(self, id: int) -> Todo:
        return self._search_todo(key=("id", id))[0]

    def search_todo_from_name(self, name: str) -> Todo:
        return self._search_todo(key=("name", name))[0]

    def search_todo_from_completed(self, is_completed: str) -> list[Todo]:
        return self._search_todo(key=("is_completed", is_completed))

    def create_todo(self, name: str, description: Union[str, None]):
        self.__execute("INSERT INTO todos VALUES (?, ?, ?, 0, ?)", (None, name, description, int(datetime.now().timestamp())))
        return self.search_todo_from_name(name)

    def update_todo(self, id: int, name: Optional[str] = None, description: Optional[str] = None) -> None:
        add_str = ""
        add_list = []

        if name is not None:
            add_str += " name = ?"
            add_list.append(name)
        elif description is not None:
            add_str += " description = ?"
            add_list.append(description)

        if len(add_list) == 0:
            return
        else:
            sql = "UPDATE todos SET" + add_str + " WHERE id = ?"
            value = tuple(add_list) + (id, )
            self.__execute(sql, value)

    def complete_todo(self, id: int) -> None:
        self.__execute("UPDATE todos SET is_completed = 1 WHERE id = ?", (id,))

    @staticmethod
    def todo_translate(id: int, name: str, description: Union[str, None], is_completed: bool, unix_time: int) -> Todo:
        return Todo(id=id, name=name, description=description, is_completed=bool(is_completed), unix_time=unix_time)
