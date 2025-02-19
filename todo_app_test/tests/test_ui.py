from unittest.mock import patch, MagicMock
from datetime import datetime

from todotest.model import TodoModel
from todotest.ui import View
from todotest.utils.ui import trim_str
from todotest.enum.types import Todo

from util import TestCasewithTmpDB, SQLChecker


class ViewTestCase(TestCasewithTmpDB):
    def setUp(self):
        super().setUp()
        self.model = TodoModel(self.db)
        self.view = View(self.model)

    def tearDown(self):
        super().tearDown()
        del self.model
        del self.view

    @patch("builtins.print")
    def test_show(self, mock_print: MagicMock):
        def todo_to_print_list(todo: Todo):
            return [
             str(todo["id"]), trim_str(todo["name"], 10).strip(), trim_str(todo["description"], 19).strip(),
             str(bool(todo["completed"])), datetime.fromtimestamp(todo["date"]).strftime("%Y/%m/%d")
            ]

        def print_check_beforethird(mock: MagicMock) -> list[list[str]]:
            """printの一行目と二行目を確かめて三行目以降を返す"""
            def strip_values(printed: str) -> list[str]:
                ret = []
                for i in printed.split("|"):
                    if i == "":
                        continue
                    else:
                        ret.append(i.strip())
                return ret

            # 一行目
            first_seqtion = strip_values(mock.call_args_list[0].args[0])
            self.assertListEqual(["id", "name", "description", "completed", "date"], first_seqtion)
            # 二行目
            second_seqtion = mock.call_args_list[1].args[0]
            self.assertEqual("-"*70, second_seqtion)
            # 三行目以降(返り値)
            return [strip_values(i.args[0]) for i in mock.call_args_list[2:]]

        # 標準状態(タスク無し)での実行
        self.view.do_show("")

        # 確認
        mock_print.assert_called_once_with("no tasks available")

        # 初期化
        mock_print.reset_mock()

        # タスク追加
        todo = self.sql_create_todo(self.tmp_file.name)

        # 実行
        self.view.do_show("")

        # 取り出し&確認
        seqtions = print_check_beforethird(mock_print)

        self.assertEqual(1, len(seqtions))

        third_seqtion = seqtions[0]
        self.assertListEqual(todo_to_print_list(todo), third_seqtion)

        # 初期化
        mock_print.reset_mock()

        # タスクをさらに追加
        todos = [todo]
        for _ in range(3):
            todos.append(self.sql_create_todo(self.tmp_file.name))

        # 実行
        self.view.do_show("")

        # 確認
        seqtions = print_check_beforethird(mock_print)

        self.assertEqual(4, len(seqtions))

        for pos, value in enumerate(seqtions):
            self.assertListEqual(todo_to_print_list(todos[pos]), value)

        # 初期化
        mock_print.reset_mock()

        # キー指定実行
        self.view.do_show(f"-k id {todos[0]['id']}")

        # 確認
        seqtions = print_check_beforethird(mock_print)
        self.assertEqual(1, len(seqtions))
        self.assertListEqual(todo_to_print_list(todos[0]), seqtions[0])

        # 初期化
        mock_print.reset_mock()

        # 順序実行
        self.view.do_show("-o id DESC")

        # 確認
        seqtions = print_check_beforethird(mock_print)

        for pos, value in enumerate(seqtions):
            self.assertListEqual(todo_to_print_list(todos[-1*(pos+1)]), value)

        # 初期化
        mock_print.reset_mock()

        # limit実行
        self.view.do_show("-l 2")

        # 確認
        seqtions = print_check_beforethird(mock_print)

        self.assertEqual(2, len(seqtions))
        for pos, value in enumerate(seqtions):
            self.assertEqual(todo_to_print_list(todos[pos]), value)

    @patch("builtins.print")
    def test_create(self, mock_print: MagicMock):
        # 存在しないことを確認
        with SQLChecker(self.tmp_file.name) as sql:
            todos = [self.todo_translate(*i) for i in sql.execute("SELECT * FROM todos")]
        self.assertListEqual([], todos)

        # 実行
        self.view.do_create("hogehoge -d hugahuga")

        # 確認
        with SQLChecker(self.tmp_file.name) as sql:
            todos = [self.todo_translate(*i) for i in sql.execute("SELECT * FROM todos")]

        self.assertEqual(1, len(todos))  # 一個あるか

        todo = todos[0]

        self.assertEqual(1, todo["id"])  # idが1か
        self.assertEqual("hogehoge", todo["name"])  # nameがhogehogeか
        self.assertEqual("hugahuga", todo["description"])  # descriptionがhugahugaか

        # printした物が2個あるか
        self.assertEqual(2, len(mock_print.call_args_list))

        # 取り出し
        first_seqtion = mock_print.call_args_list[0].args[0]
        second_seqtion = mock_print.call_args_list[1].args[0]

        # 一行目
        self.assertEqual("create successful!", first_seqtion)

        # 二行目
        self.assertEqual(f"todo id: {todo['id']}", second_seqtion)

        # 初期化
        mock_print.reset_mock()

        # 実行(名前被りエラー)
        self.view.do_create(str(todo["name"]))

        # 確認
        mock_print.assert_called_once_with(f"error has occured: name `{todo['name']}` is already exists")

    @patch("builtins.print")
    def test_complete(self, mock_print: MagicMock):
        # 何もないことを確認
        with SQLChecker(self.tmp_file.name) as sql:
            self.assertFalse(bool(sql.execute("SELECT EXISTS (SELECT 1 FROM todos)")[0][0]))

        # 実行(id不適合エラー)
        self.view.do_complete("1")

        # 確認
        mock_print.assert_called_once_with("error has occured: todo id `1` is not exists")

        # 初期化
        mock_print.reset_mock()

        # 作成
        todo = self.sql_create_todo(self.tmp_file.name)

        # 完了したものがないことを確認
        with SQLChecker(self.tmp_file.name) as sql:
            self.assertEqual(0, len(sql.execute("SELECT * FROM todos WHERE completed = 1")))

        # 実行
        self.view.do_complete(str(todo["id"]))

        # 完了したものがあることを確認
        with SQLChecker(self.tmp_file.name) as sql:
            completed_todos = sql.execute("SELECT * FROM todos WHERE completed = 1")

        # 一つだけか確認
        self.assertEqual(1, len(completed_todos))

        # 取り出し
        completed_todo = self.todo_translate(*completed_todos[0])

        # 比較
        completed_todo["completed"] = False
        self.assertDictEqual(todo, completed_todo)
        completed_todo["completed"] = True

        # 実行(完了済みエラー)
        self.view.do_complete(str(completed_todo["id"]))

        mock_print.assert_called_once_with("error has occured: this todo is already completed")
