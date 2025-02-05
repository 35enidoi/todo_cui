from typing import TypedDict, Union


class Todo(TypedDict):
    id: int
    name: str
    description: Union[str, None]
    is_completed: bool
    unix_time: int
