from todotest.enum.db import VALID_KEYS

from util import SQLChecker, TestCasewithTmpDB


class DetabaseTestCase(TestCasewithTmpDB):
    def test_search(self):
        # 作成
        real_todo = self.sql_create_todo(self.tmp_file.name)

        # KEY
        for i in VALID_KEYS:
            todo = self.db.search_todo((i, real_todo[i]))[0]
            self.assertDictEqual(todo, real_todo)

        # さらに作成
        real_todos = [real_todo]
        for _ in range(3):
            real_todos.append(self.sql_create_todo(self.tmp_file.name))

        # ORDER
        self.assertListEqual(self.db.search_todo(order=("id", "ASC")), real_todos)
        self.assertListEqual(self.db.search_todo(order=("id", "DESC")), list(reversed(real_todos)))

        # LIMIT
        self.assertListEqual(self.db.search_todo(order=("id", "ASC"), limit=2), real_todos[:2])

    def test_create(self):
        # 作成
        todo = self.db.create_todo("hoge", "huga")

        # 確認
        with SQLChecker(self.tmp_file.name) as sql:
            for i in VALID_KEYS:
                real_todo = self.todo_translate(*sql.execute(f"SELECT * FROM todos WHERE {i} = ?", todo[i])[0])
                self.assertDictEqual(todo, real_todo)

    def test_exist(self):
        # 作成
        todo = self.sql_create_todo(self.tmp_file.name)

        # 確認
        for i in VALID_KEYS:
            self.assertTrue(self.db.exist_todo(i, todo[i]))

        # 削除
        with SQLChecker(self.tmp_file.name) as sql:
            sql.execute("DELETE FROM todos WHERE id = ?", todo["id"])

        # 確認
        for i in VALID_KEYS:
            self.assertFalse(self.db.exist_todo(i, todo[i]))

    def test_update(self):
        ...  # Todo あとでつくる

    def test_complete(self):
        # 作成
        todo = self.sql_create_todo(self.tmp_file.name)

        # 完了してないことを確認
        self.assertFalse(todo["completed"])

        # 完了
        self.db.complete_todo(todo["id"])

        # 完了したことを確認
        with SQLChecker(self.tmp_file.name) as sql:
            completed_todo = self.todo_translate(*sql.execute("SELECT * FROM todos WHERE id = ?", todo["id"])[0])
            self.assertTrue(completed_todo["completed"])
