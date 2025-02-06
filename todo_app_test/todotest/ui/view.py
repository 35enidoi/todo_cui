from cmd import Cmd
from datetime import datetime

from todotest.model import TodoModel
from todotest.utils.ui import trim_str, error_text, parse_args


class View(Cmd):
    prompt = ">>> "
    intro = "Welcome to todo app!"

    def __init__(self, model: TodoModel):
        super().__init__()
        self.model = model

    def emptyline(self):
        return

    def do_help(self, arg):
        commands = [i[3:] for i in self.get_names() if i[:3] == "do_"]

        # help単体の時の挙動
        if arg == "":
            print("avaible commands")
            print("="*15)
            print(" ".join(commands))
            return

        arg_names = (
            (("command",), {"help": "command name"}),
        )
        args = parse_args(arg, prog="help", args=arg_names, description="show command help message")
        if args is None:
            return

        if args.command in commands:
            func = getattr(self, "do_" + args.command)
            func("--help")
        else:
            print(error_text(f"command `{args.command}` is not available."))

    def do_show(self, args):
        arg_names = ()
        args = parse_args(args, prog="show", args=arg_names, description="show Todos")
        if args is None:
            return

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
        arg_names = (
            (("name",), {"help": "Todo name"}),
            (("-d", "--description"), {"default": "", "help": "Todo description"})
        )
        args = parse_args(arg, prog="create", args=arg_names, description="create Todo")
        if args is None:
            return

        name = args.name
        description = args.description

        if self.model.exist_task_from_name(name):
            # もう既に存在している場合
            print(error_text(f"name `{name}` is already exists"))
            return

        created_todo = self.model.create_task(name, description)
        print("create successful!")
        print(f"todo id: {created_todo['id']}")

    def do_exit(self, arg):
        if arg == "--help":
            print("exit: exit this program.")
            return
        return True

    def do_debug_switch(self, _):
        self.model.db.debug = not self.model.db.debug
        if self.model.db.debug:
            print("debug mode enabled")
            self.prompt = "(debug) " + self.prompt
        else:
            print("debug mode disabled")
            self.prompt = self.prompt[8:]
