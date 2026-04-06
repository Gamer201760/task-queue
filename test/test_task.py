from datetime import datetime
from uuid import UUID

import pytest

from domain.error import TaskStatusTransitionError, TaskStatusValidationError
from domain.task import Task
from domain.task_status import TaskStatus

TASK_ID = '12345678-1234-5678-1234-567812345678'


def make_task(
    *,
    description: str = 'Task description',
    priority: int = 3,
    status: TaskStatus | str = TaskStatus.NEW,
) -> Task:
    return Task(TASK_ID, description=description, priority=priority, status=status)


def test_id_property_returns_uuid() -> None:
    task = make_task()

    assert isinstance(task.id, UUID)
    assert task.id == UUID(TASK_ID)


def test_description_property_returns_assigned_value() -> None:
    task = make_task(description='Write direct task tests')

    assert task.description == 'Write direct task tests'


def test_priority_property_returns_assigned_value() -> None:
    task = make_task(priority=5)

    assert task.priority == 5


def test_created_at_is_timezone_aware_datetime() -> None:
    task = make_task()

    assert isinstance(task.created_at, datetime)
    assert task.created_at.tzinfo is not None
    assert task.created_at.utcoffset() is not None


def test_is_ready_is_true_for_new_task() -> None:
    task = make_task()

    assert task.is_ready is True


@pytest.mark.parametrize(
    ('status_value', 'expected_status'),
    [
        ('in_progress', TaskStatus.IN_PROGRESS),
        (TaskStatus.DONE, TaskStatus.DONE),
    ],
)
def test_status_can_be_initialized_from_string_or_enum(
    status_value: TaskStatus | str, expected_status: TaskStatus
) -> None:
    task = make_task(status=status_value)

    assert task.status is expected_status


def test_valid_status_transitions_succeed() -> None:
    task = make_task()

    task.status = TaskStatus.IN_PROGRESS
    task.status = TaskStatus.DONE

    assert task.status is TaskStatus.DONE


def test_same_status_assignment_is_allowed() -> None:
    task = make_task(status=TaskStatus.IN_PROGRESS)

    task.status = TaskStatus.IN_PROGRESS

    assert task.status is TaskStatus.IN_PROGRESS


@pytest.mark.parametrize(
    ('initial_status', 'next_status'),
    [
        (TaskStatus.NEW, TaskStatus.DONE),
        (TaskStatus.DONE, TaskStatus.NEW),
    ],
)
def test_invalid_status_transitions_raise_transition_error(
    initial_status: TaskStatus, next_status: TaskStatus
) -> None:
    task = make_task(status=initial_status)

    with pytest.raises(TaskStatusTransitionError):
        task.status = next_status


def test_invalid_status_string_raises_validation_error() -> None:
    with pytest.raises(TaskStatusValidationError):
        make_task(status='blocked')


def test_task_status_normalize_preserves_validation_messages() -> None:
    assert TaskStatus.normalize('done') is TaskStatus.DONE

    with pytest.raises(
        TaskStatusValidationError,
        match='Статус должен быть одним из: new, in_progress, done',
    ):
        TaskStatus.normalize('blocked')

    with pytest.raises(
        TaskStatusValidationError,
        match='Статус должен быть строкой или TaskStatus',
    ):
        TaskStatus.normalize(123)  # type: ignore[arg-type]


def test_is_ready_becomes_false_after_leaving_new_status() -> None:
    task = make_task()

    task.status = TaskStatus.IN_PROGRESS

    assert task.is_ready is False
