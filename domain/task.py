from datetime import datetime, timezone
from uuid import UUID

from domain.descriptor import Int, String
from domain.error import TaskStatusTransitionError
from domain.task_status import TaskStatus


class Task:
    description = String(min_len=1)
    priority = Int(min_value=1)
    _ALLOWED_STATUS_TRANSITIONS = frozenset(
        {
            (TaskStatus.NEW, TaskStatus.IN_PROGRESS),
            (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
        }
    )

    def __init__(
        self,
        id: str | UUID,
        description: str,
        priority: int = 1,
        status: TaskStatus | str = TaskStatus.NEW,
    ) -> None:
        self._id = UUID(str(id))
        self.description = description
        self.priority = priority
        self.status = status
        self._created_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return (
            f'Task(id={str(self.id)!r}, description={self.description!r}, '
            f'priority={self.priority}, status={self.status.value!r})'
        )

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def status(self) -> TaskStatus:
        return self._status

    @status.setter
    def status(self, value: TaskStatus | str) -> None:
        next_status = TaskStatus.normalize(value)
        current_status = getattr(
            self, '_status', None
        )  # При первом присваивании из __init__ атрибут _status ещё может не существовать

        if current_status is not None and current_status is not next_status:
            transition = (current_status, next_status)
            if transition not in self._ALLOWED_STATUS_TRANSITIONS:
                raise TaskStatusTransitionError(
                    f'Недопустимый переход статуса: {current_status.value} -> {next_status.value}'
                )

        self._status = next_status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def is_ready(self) -> bool:
        return self._status is TaskStatus.NEW
