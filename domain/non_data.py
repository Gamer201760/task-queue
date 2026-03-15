from domain.task_status import TaskStatus


class NonDataStatusLabel:
    """Non-data descriptor для чтения текстовой метки статуса"""

    def __get__(self, obj: object | None, objtype: type | None = None) -> object:
        if obj is None:
            return self
        return f'Status: {obj.status.value}'


class DemoTask:
    """Учебный класс для демонстрации non-data descriptor"""

    label = NonDataStatusLabel()

    def __init__(self, status: TaskStatus) -> None:
        self.status = status
