from cmd import Cmd
from datetime import datetime

from todotest.model import TodoModel
from todotest.utils.ui import trim_str, error_text, parse_args
from todotest.enum.db import VALID_KEYS, VALID_ORDERS


class View(Cmd):
    prompt = ">>> "
    intro = "Welcome to todo app!"

    def __init__(self, model: TodoModel):
        super().__init__()
        self.model = model

    def emptyline(self):
        return

# Todo関係コマンド

    def do_show(self, args):
        arg_names = (
            (("-k", "--key"), {"nargs": 2, "metavar": (list(VALID_KEYS), "KEY"), "help": "filter by keys."}),
            (("-o", "--order"), {"nargs": 2, "choices": list(VALID_KEYS) + list(VALID_ORDERS),
                                 "metavar": (list(VALID_KEYS), list(VALID_ORDERS)), "help": "sorting argorithm"}),
            (("-l", "--limit"), {"type": int, "help": "showing number"}),
        )
        args = parse_args(args, prog="show", args=arg_names, description="show Todos")
        if args is None:
            return

        if args.key is not None:
            if args.key[0] not in VALID_KEYS:
                print(error_text(f"key `{args.key[0]}` is not available"))
                return

        if args.order is not None:
            if args.order[0] not in VALID_KEYS:
                print(error_text(f"key `{args.order[0]}` is not available"))
                return
            elif args.order[1] not in VALID_ORDERS:
                print(error_text(f"order `{args.order[1]}` is not abailable"))
                return

        tasks = self.model.show_tasks(keys=args.key, order=args.order, limit=args.limit)

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
                trim_str(str(i["completed"]), 9),
                datetime.fromtimestamp(i["date"]).strftime("%Y/%m/%d").center(12)
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

# 特殊コマンド

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

    def do_exit(self, arg):
        if arg == "--help":
            print("exit: exit this program.")
            return
        return True

# デバッグ用コマンド

    def do_debug_switch(self, arg):
        if arg == "--help":
            print("switch mode into `debug mode`")
            return

        self.model.db.debug = not self.model.db.debug
        if self.model.db.debug:
            print("debug mode enabled")
            self.prompt = "(debug) " + self.prompt
        else:
            print("debug mode disabled")
            self.prompt = self.prompt[8:]
