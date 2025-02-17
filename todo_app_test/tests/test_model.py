from random import choice

from todotest.model import TodoModel
from todotest.enum.db import VALID_KEYS

from util import TestCasewithTmpDB, SQLChecker


class ModelTestCase(TestCasewithTmpDB):
    def setUp(self):
        super().setUp()
        self.model = TodoModel(self.db)

    def tearDown(self):
        super().tearDown()
        del self.model

    def test_show(self):
        # Todo作成
        real_todos = [self.sql_create_todo(self.tmp_file.name) for _ in range(5)]

        # 一覧表示
        self.assertListEqual(real_todos, self.model.show_tasks())

        # key検索
        random_todo = choice(real_todos)
        ret = self.model.show_tasks(("id", random_todo["id"]))[0]
        self.assertDictEqual(random_todo, ret)

        self.assertListEqual([], self.model.show_tasks(("completed", True)))
        self.assertListEqual(real_todos, self.model.show_tasks(("completed", False)))

        # order
        ret = self.model.show_tasks(order=("id", "ASC"))
        self.assertListEqual(sorted(real_todos, key=lambda x: x["id"]), ret)
        ret = self.model.show_tasks(order=("id", "DESC"))
        self.assertListEqual(sorted(real_todos, key=lambda x: -1*x["id"]), ret)

        # limit
        ret = self.model.show_tasks(order=("id", "ASC"), limit=2)
        self.assertListEqual(real_todos[:2], ret)

    def test_create(self):
        # 実行
        todo = self.model.create_task("hoge", "huga")

        # 確認
        with SQLChecker(self.tmp_file.name) as sql:
            for i in VALID_KEYS:
                real_todo = self.todo_translate(*sql.execute(f"SELECT * FROM todos WHERE {i} = ?", todo[i])[0])
                self.assertDictEqual(real_todo, todo)

    def test_complete(self):  # model側の関数名間違えてるので後で修正する予定
        # 作成
        todo = self.sql_create_todo(self.tmp_file.name)

        # 完了してないのを確認
        self.assertFalse(todo["completed"])

        # 実行
        self.model.update(todo["id"])

        # 確認
        with SQLChecker(self.tmp_file.name) as sql:
            real_todo = self.todo_translate(*sql.execute("SELECT * FROM todos WHERE id = ?", todo["id"])[0])
        self.assertTrue(real_todo["completed"])

    def test_exist_from_id(self):
        # 作成
        todo = self.sql_create_todo(self.tmp_file.name)

        # 確認
        self.assertTrue(self.model.exist_task_from_id(todo["id"]))

        # 削除
        with SQLChecker(self.tmp_file.name) as sql:
            sql.execute("DELETE FROM todos WHERE id = ?", todo["id"])

        # 確認
        self.assertFalse(self.model.exist_task_from_id(todo["id"]))

    def test_exist_from_name(self):
        # 作成
        todo = self.sql_create_todo(self.tmp_file.name)

        # 確認
        self.assertTrue(self.model.exist_task_from_name(todo["name"]))

        # 削除
        with SQLChecker(self.tmp_file.name) as sql:
            sql.execute("DELETE FROM todos WHERE id = ?", todo["id"])

        # 確認
        self.assertFalse(self.model.exist_task_from_name(todo["name"]))
