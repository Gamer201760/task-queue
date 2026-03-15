class TaskError(Exception):
    """Базовая ошибка доменной модели задачи"""


class ValidationError(TaskError):
    """Ошибка валидации атрибута задачи"""


class StringValidationError(ValidationError):
    """Ошибка валидации строкового атрибута"""


class IntValidationError(ValidationError):
    """Ошибка валидации числового атрибута"""


class TaskStatusValidationError(ValidationError):
    """Ошибка валидации статуса задачи"""


class TaskStatusTransitionError(TaskError):
    """Ошибка недопустимого перехода статуса задачи"""
