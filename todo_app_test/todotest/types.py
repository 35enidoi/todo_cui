from typing import TypedDict, Union


class Todo(TypedDict):
    id: int
    name: str
    description: Union[str, None]
    completed: bool
    date: int
