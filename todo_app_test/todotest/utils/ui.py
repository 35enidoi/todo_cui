import shlex
import argparse
from typing import Union, Optional


def trim_str(string: str, limit: int) -> str:
    """文字を指定の長さに整える(中央揃え)"""
    if len(string) > limit:
        if limit < 6:
            tuduki = ".."
        else:
            tuduki = "..."
        return string[:limit-len(tuduki)] + tuduki
    else:
        return string.center(limit)


def error_text(string) -> str:
    """エラー文字の定型文"""
    return "error has occured: " + string


def parse_args(
        string: str,
        prog: str,
        args: tuple[tuple[tuple[str], Union[None, dict]]],
        description: Optional[str] = None) -> Union[None, argparse.Namespace]:
    """引数をargparseするやつ。もしparseに失敗(変なarg)だと自動で文字を出力してNoneを返す"""
    # 引数取り出し
    row_args = shlex.split(string)

    # フィルター作成
    parser = argparse.ArgumentParser(prog=prog, description=description)
    for names, keys in args:
        if keys is None:
            keys = dict()
        parser.add_argument(*names, **keys)

    try:
        return parser.parse_args(row_args)
    except SystemExit:
        return
