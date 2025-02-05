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
