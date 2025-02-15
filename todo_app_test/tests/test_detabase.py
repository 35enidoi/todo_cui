import unittest
from todotest.database import DataBase


class DetabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.db = DataBase()

    def tearDown(self):
        del self.db

    def test_hoge(self):
        self.assertEqual(1, 1)
