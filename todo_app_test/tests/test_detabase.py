from todotest.enum.db import VALID_KEYS

from util import SQLChecker, TestCasewithTmpDB


class DetabaseTestCase(TestCasewithTmpDB):
    def test_search(self):
        # テスト値を追加
        real_todo = self.sql_create_todo(self.tmp_file.name)

        # KEY
        for i in VALID_KEYS:
            todo = self.db.search_todo((i, real_todo[i]))[0]
            self.assertEqual(todo, real_todo)

        # テスト値を追加
        real_todos = [real_todo]
        for _ in range(3):
            real_todos.append(self.sql_create_todo(self.tmp_file.name))

        # ORDER
        self.assertEqual(self.db.search_todo(order=("id", "ASC")), real_todos)
        self.assertEqual(self.db.search_todo(order=("id", "DESC")), list(reversed(real_todos)))

        # LIMIT
        self.assertEqual(self.db.search_todo(order=("id", "ASC"), limit=2), real_todos[:2])

    def test_create(self):
        todo = self.db.create_todo("hoge", "huga")

        with SQLChecker(self.tmp_file.name) as sql:
            for i in VALID_KEYS:
                real_todo = self.todo_translate(*sql.execute(f"SELECT * FROM todos WHERE {i} = ?", todo[i])[0])
                self.assertEqual(todo, real_todo)

    def test_exist(self):
        self.assertFalse(self.db.exist_todo("id", 1))

        todo = self.sql_create_todo(self.tmp_file.name)

        for i in VALID_KEYS:
            self.assertTrue(self.db.exist_todo(i, todo[i]))

    def test_update(self):
        ...  # Todo あとでつくる

    def test_complete(self):
        todo = self.sql_create_todo(self.tmp_file.name)

        self.assertFalse(todo["completed"])

        self.db.complete_todo(todo["id"])

        with SQLChecker(self.tmp_file.name) as sql:
            completed_todo = self.db.todo_translate(*sql.execute("SELECT * FROM todos WHERE id = ?", todo["id"])[0])
            self.assertTrue(completed_todo["completed"])
