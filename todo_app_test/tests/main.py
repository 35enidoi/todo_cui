from os import listdir, path as ospath
from sys import path as syspath
import importlib
import unittest


syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), "../")))


test_list = []

for i in listdir(ospath.dirname(__file__)):
    if i.startswith("test_") and i.endswith(".py"):
        module_name = i[:-3]
        try:
            importlib.import_module(name=module_name)
        except ImportError:
            pass
        else:
            test_list.append(module_name)


if __name__ == "__main__":
    print(f"start {len(test_list)} tests...")
    for i in test_list:
        print("="*50)
        print(i)
        unittest.main(i, exit=False)
    print("="*50)
