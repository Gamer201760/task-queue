from collections.abc import Iterator
from itertools import islice
from typing import cast
from uuid import UUID

import pytest

from domain.error import TaskStatusValidationError
from domain.task import Task
from domain.task_queue import TaskQueue
from domain.task_status import TaskStatus


def _task(
    index: int,
    *,
    description: str | None = None,
    priority: int = 1,
    status: TaskStatus | str = TaskStatus.NEW,
) -> Task:
    task_description = description if description is not None else f'task {index}'
    return Task(UUID(int=index + 1), task_description, priority, status)


def test_task_queue_is_compatible_with_for_list_and_sum() -> None:
    source_tasks = (
        _task(1, description='Write report', priority=1),
        _task(
            2,
            description='Review report',
            priority=2,
            status=TaskStatus.IN_PROGRESS,
        ),
        _task(3, description='Publish report', priority=3, status=TaskStatus.DONE),
    )
    queue = TaskQueue(source_tasks)

    descriptions_from_for: list[str] = []
    for task in queue:
        descriptions_from_for.append(cast(str, task.description))

    listed_tasks = list(queue)

    assert descriptions_from_for == ['Write report', 'Review report', 'Publish report']
    assert [task.description for task in listed_tasks] == [
        'Write report',
        'Review report',
        'Publish report',
    ]
    assert sum(cast(int, task.priority) for task in queue) == 6


def test_task_queue_creates_new_iterator_for_each_traversal() -> None:
    source_tasks = (
        _task(1, description='Collect requirements'),
        _task(2, description='Implement queue'),
    )
    iterator_factory_calls = 0

    def iterator_factory() -> Iterator[Task]:
        nonlocal iterator_factory_calls
        iterator_factory_calls += 1
        yield from source_tasks

    queue = TaskQueue(iterator_factory)

    assert iterator_factory_calls == 0

    first_iterator = iter(queue)
    second_iterator = iter(queue)

    assert first_iterator is not second_iterator
    assert list(first_iterator) == list(source_tasks)
    assert list(second_iterator) == list(source_tasks)
    assert iterator_factory_calls == 2


def test_list_over_task_queue_uses_iterator_factory_once_and_returns_all_tasks() -> (
    None
):
    source_tasks = (
        _task(1, description='Collect requirements'),
        _task(2, description='Implement queue'),
        _task(3, description='Review queue'),
    )
    iterator_factory_calls = 0

    def iterator_factory() -> Iterator[Task]:
        nonlocal iterator_factory_calls
        iterator_factory_calls += 1
        yield from source_tasks

    queue = TaskQueue(iterator_factory)

    listed_tasks = list(queue)

    assert listed_tasks == list(source_tasks)
    assert iterator_factory_calls == 1


def test_task_queue_rejects_one_shot_iterator_objects() -> None:
    one_shot_iterator = (_task(index) for index in range(3))

    with pytest.raises(TypeError, match='итератор|iterator'):
        TaskQueue(one_shot_iterator)


def test_task_queue_iterator_raises_stop_iteration_after_last_task() -> None:
    queue = TaskQueue(
        (
            _task(1, description='First task'),
            _task(2, description='Second task'),
        )
    )

    iterator = iter(queue)

    assert next(iterator).description == 'First task'
    assert next(iterator).description == 'Second task'

    with pytest.raises(StopIteration):
        next(iterator)

    with pytest.raises(StopIteration):
        next(iterator)


def test_filter_by_status_returns_lazy_task_queue() -> None:
    source_tasks = (
        _task(1, description='Draft task', status=TaskStatus.NEW),
        _task(2, description='Deploy task', status=TaskStatus.DONE),
        _task(3, description='Review task', status=TaskStatus.IN_PROGRESS),
        _task(4, description='Archive task', status=TaskStatus.DONE),
    )
    iterator_factory_calls = 0
    produced_descriptions: list[str] = []

    def iterator_factory() -> Iterator[Task]:
        nonlocal iterator_factory_calls
        iterator_factory_calls += 1
        for task in source_tasks:
            produced_descriptions.append(cast(str, task.description))
            yield task

    queue = TaskQueue(iterator_factory)
    filtered = queue.filter_by_status('done')

    assert isinstance(filtered, TaskQueue)
    assert filtered is not queue
    assert iterator_factory_calls == 0
    assert produced_descriptions == []

    assert [task.description for task in filtered] == ['Deploy task', 'Archive task']
    assert iterator_factory_calls == 1
    assert produced_descriptions == [
        'Draft task',
        'Deploy task',
        'Review task',
        'Archive task',
    ]

    produced_descriptions.clear()

    assert [task.description for task in filtered] == ['Deploy task', 'Archive task']
    assert iterator_factory_calls == 2
    assert produced_descriptions == [
        'Draft task',
        'Deploy task',
        'Review task',
        'Archive task',
    ]


def test_filter_by_status_preserves_status_validation_message() -> None:
    queue = TaskQueue((_task(1),))

    with pytest.raises(
        TaskStatusValidationError,
        match='Статус должен быть одним из: new, in_progress, done',
    ):
        queue.filter_by_status('blocked')


def test_filter_by_priority_returns_lazy_task_queue_with_inclusive_bounds() -> None:
    source_tasks = (
        _task(1, priority=1),
        _task(2, priority=2),
        _task(3, priority=3),
        _task(4, priority=4),
        _task(5, priority=5),
    )
    iterator_factory_calls = 0
    produced_priorities: list[int] = []

    def iterator_factory() -> Iterator[Task]:
        nonlocal iterator_factory_calls
        iterator_factory_calls += 1
        for task in source_tasks:
            produced_priorities.append(cast(int, task.priority))
            yield task

    queue = TaskQueue(iterator_factory)
    filtered = queue.filter_by_priority(min_priority=2, max_priority=4)

    assert isinstance(filtered, TaskQueue)
    assert filtered is not queue
    assert iterator_factory_calls == 0
    assert produced_priorities == []

    assert [task.priority for task in filtered] == [2, 3, 4]
    assert iterator_factory_calls == 1
    assert produced_priorities == [1, 2, 3, 4, 5]


def test_large_queue_from_iterator_factory_is_consumed_incrementally() -> None:
    total_tasks = 10_000
    iterator_factory_calls = 0
    produced_count = 0

    def iterator_factory() -> Iterator[Task]:
        nonlocal iterator_factory_calls, produced_count
        iterator_factory_calls += 1
        for index in range(total_tasks):
            produced_count += 1
            yield _task(index, priority=(index % 5) + 1)

    queue = TaskQueue(iterator_factory)
    filtered = queue.filter_by_priority(min_priority=5, max_priority=5)

    assert iterator_factory_calls == 0
    assert produced_count == 0

    first_three = list(islice(filtered, 3))

    assert [task.description for task in first_three] == ['task 4', 'task 9', 'task 14']
    assert [task.priority for task in first_three] == [5, 5, 5]
    assert iterator_factory_calls == 1
    assert produced_count == 15
    assert produced_count < total_tasks
