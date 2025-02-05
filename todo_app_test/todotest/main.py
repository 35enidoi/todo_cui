# from os import path

from todotest.database import DataBase
from todotest.model import TodoModel
from todotest.ui import View


def main():
    # db_path = path.abspath(path.join(path.dirname(__file__), "todo.db"))
    db = DataBase()
    model = TodoModel(db)
    view = View(model)
    view.cmdloop()
