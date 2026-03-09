from typing import Iterable, Protocol, runtime_checkable

from domain.task import Task


@runtime_checkable
class DataSource(Protocol):
    def get_tasks(self) -> Iterable[Task]: ...
