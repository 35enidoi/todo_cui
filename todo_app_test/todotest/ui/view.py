from cmd import Cmd
from datetime import datetime

from todotest.model import TodoModel
from todotest.utils.ui import trim_str, error_text


class View(Cmd):
    intro = "Welcome to todo app!"

    def __init__(self, model: TodoModel):
        super().__init__()
        self.model = model

    def do_show(self, _):
        tasks = self.model.show_tasks()

        if len(tasks) == 0:
            print("no tasks available")
            return

        print("|  id  |    name    |     description     | completed |     date     |")
        print("-"*70)
        row_text = "| {} | {} | {} | {} | {} |"
        for i in tasks:
            text = row_text.format(
                str(i["id"]).center(4),
                trim_str(i["name"], 10),
                trim_str(str(i["description"]), 19),
                trim_str(str(i["is_completed"]), 9),
                datetime.fromtimestamp(i["unix_time"]).strftime("%Y/%m/%d").center(12)
            )

            print(text)

    def do_create(self, arg: str):
        args = arg.split(" ")

        if arg == "":
            print(error_text("no args"))
            return

        name = args[0]
        description = " ".join(args[1:])
        created_todo = self.model.create_task(name, description)
        print("create successful!")
        print(f"todo id: {created_todo['id']}")

    def do_exit(self, _):
        return True
