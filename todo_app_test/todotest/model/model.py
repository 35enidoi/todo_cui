from todotest.database import DataBase
from todotest.types import Todo


class TodoModel:
    def __init__(self, db: DataBase):
        self.db = db

    def show_tasks(self) -> list[Todo]:
        return self.db.search_todo()

    def create_task(self, name: str, description: str) -> Todo:
        if description == "":
            description = None  # 情報がない場合Noneということにしておく
        return self.db.create_todo(name=name, description=description)

    def exist_task_from_name(self, name: str) -> bool:
        return self.db.exist_todo("name", name)
