from todotest.enum.db import VALID_KEYS

from util import SQLChecker, TestCasewithTmpDB


class DetabaseTestCase(TestCasewithTmpDB):
    def test_search(self):
        # テスト値を追加
        with SQLChecker(self.tmp_file.name) as sql:
            sql.execute("INSERT INTO todos VALUES (?, ?, ?, 0, ?)", None, "hoge", "huga", 100)  # 1
            real_todo = self.db.todo_translate(*sql.execute("SELECT * FROM todos WHERE id = 1")[0])

        # KEY
        for i in VALID_KEYS:
            todo = self.db.search_todo((i, real_todo[i]))[0]
            self.assertEqual(todo, real_todo)

        # テスト値を追加
        with SQLChecker(self.tmp_file.name) as sql:
            sql.execute("INSERT INTO todos VALUES (?, ?, ?, 0, ?)", None, "a", "a", 0)  # 2
            sql.execute("INSERT INTO todos VALUES (?, ?, ?, 1, ?)", None, "zzzz", "zzzz", 10)  # 3
            real_todos = [self.db.todo_translate(*i) for i in sql.execute("SELECT * FROM todos ORDER BY id ASC")]

        # ORDER
        self.assertEqual(self.db.search_todo(order=("id", "ASC")), real_todos)
        self.assertEqual(self.db.search_todo(order=("id", "DESC")), list(reversed(real_todos)))

        # LIMIT
        self.assertEqual(self.db.search_todo(order=("id", "ASC"), limit=2), real_todos[:2])

    def test_create(self):
        todo = self.db.create_todo("hoge", "huga")

        for i in VALID_KEYS:
            self.assertEqual(self.db.search_todo(key=(i, todo[i]))[0], todo)

    def test_exist(self):
        self.assertFalse(self.db.exist_todo("id", 1))

        todo = self.db.create_todo("hoge", "huga")

        for i in VALID_KEYS:
            self.assertTrue(self.db.exist_todo(i, todo[i]))

    def test_update(self):
        ...  # Todo あとでつくる

    def test_complete(self):
        todo_id = self.db.create_todo("hoge", "huga")["id"]

        self.assertFalse(self.db.search_todo(("id", todo_id))[0]["completed"])
        self.db.complete_todo(todo_id)
        self.assertTrue(self.db.search_todo(("id", todo_id))[0]["completed"])
