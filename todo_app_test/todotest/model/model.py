from typing import Optional

from todotest.database import DataBase
from todotest.enum.types import Todo


class TodoModel:
    def __init__(self, db: DataBase):
        self.db = db

    def show_tasks(self,
                   keys: Optional[tuple[str, str]] = None,
                   order: Optional[tuple[str]] = None,
                   limit: Optional[int] = None) -> list[Todo]:
        return self.db.search_todo(key=keys, order=order, limit=limit)

    def create_task(self, name: str, description: str) -> Todo:
        if description == "":
            description = None  # 情報がない場合Noneということにしておく
        return self.db.create_todo(name=name, description=description)

    def exist_task_from_name(self, name: str) -> bool:
        return self.db.exist_todo("name", name)

    def exist_task_from_id(self, id: str) -> bool:
        return self.db.exist_todo("id", id)

    def update(self, id: str) -> bool:
        return self.db.complete_todo(id=id)
