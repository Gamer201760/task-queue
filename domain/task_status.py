from enum import Enum

from domain.error import TaskStatusValidationError


class TaskStatus(str, Enum):
    NEW = 'new'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'

    @classmethod
    def normalize(cls, value: 'TaskStatus | str') -> 'TaskStatus':
        if isinstance(value, cls):
            return value

        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as err:
                raise TaskStatusValidationError(
                    f'Статус должен быть одним из: {", ".join(item.value for item in cls)}'
                ) from err

        raise TaskStatusValidationError('Статус должен быть строкой или TaskStatus')
