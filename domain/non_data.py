from typing import Protocol, runtime_checkable

from domain.task_status import TaskStatus


@runtime_checkable
class SupportsStatus(Protocol):
    status: TaskStatus


class NonDataStatusLabel:
    """Non-data descriptor для чтения текстовой метки статуса"""

    def __get__(self, obj: object | None, objtype: type | None = None) -> object:
        if obj is None:
            return self
        if not isinstance(obj, SupportsStatus):
            raise TypeError('Дескриптор работает только с объектами со статусом задачи')
        return f'Status: {obj.status.value}'


class DemoTask:
    """Учебный класс для демонстрации non-data descriptor"""

    label = NonDataStatusLabel()

    def __init__(self, status: TaskStatus) -> None:
        self.status = status
