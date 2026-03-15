import time
from typing import cast
from uuid import UUID

import pytest

import repository.api.mock as mock_module
from domain.error import TaskStatusValidationError
from domain.task import Task
from domain.task_status import TaskStatus
from repository.api.mock import MockExternalSource


@pytest.fixture(autouse=True)
def sleep_calls(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    calls: list[float] = []

    def fake_sleep(seconds: float) -> None:
        calls.append(seconds)

    monkeypatch.setattr(time, 'sleep', fake_sleep)
    monkeypatch.setattr(mock_module, 'sleep', fake_sleep, raising=False)

    module_time = getattr(mock_module, 'time', None)
    if module_time is not None:
        monkeypatch.setattr(module_time, 'sleep', fake_sleep)

    return calls


def _source_with_raw_tasks(
    monkeypatch: pytest.MonkeyPatch,
    raw_tasks: list[object],
) -> MockExternalSource:
    source = MockExternalSource()
    monkeypatch.setattr(source, '_fetch_tasks', lambda: raw_tasks)
    return source


def _expected_status(raw_status: object) -> TaskStatus:
    if isinstance(raw_status, TaskStatus):
        return raw_status
    return TaskStatus(str(raw_status))


def _assert_task_matches_raw_item(task: Task, raw_item: dict[str, object]) -> None:
    assert task.description == raw_item['description']
    assert task.priority == raw_item.get('priority', 1)

    if 'id' in raw_item:
        assert task.id == UUID(str(raw_item['id']))
    else:
        assert isinstance(task.id, UUID)

    if 'status' in raw_item:
        assert task.status is _expected_status(raw_item['status'])
    else:
        assert task.status is TaskStatus.NEW


def test_get_tasks_returns_non_empty_list_of_task() -> None:
    tasks = MockExternalSource().get_tasks()

    assert tasks
    assert all(isinstance(task, Task) for task in tasks)


def test_default_raw_payload_maps_to_task_fields_correctly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_tasks = cast(list[dict[str, object]], MockExternalSource()._fetch_tasks())
    source = _source_with_raw_tasks(monkeypatch, list(raw_tasks))
    tasks = source.get_tasks()

    assert len(tasks) == len(raw_tasks)
    for task, raw_item in zip(tasks, raw_tasks, strict=True):
        _assert_task_matches_raw_item(task, raw_item)


def test_generated_task_ids_are_uuid_backed_when_id_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    generated_id = UUID('12345678-1234-5678-1234-567812345678')
    monkeypatch.setattr(mock_module, 'uuid4', lambda: generated_id, raising=False)

    tasks = _source_with_raw_tasks(
        monkeypatch,
        [{'description': 'Create task from mock source', 'priority': 1}],
    ).get_tasks()

    assert len(tasks) == 1
    assert tasks[0].id == generated_id
    assert isinstance(tasks[0].id, UUID)


def test_missing_status_defaults_to_task_status_new(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tasks = _source_with_raw_tasks(
        monkeypatch,
        [{'description': 'Default status task', 'priority': 2}],
    ).get_tasks()

    assert len(tasks) == 1
    assert tasks[0].status is TaskStatus.NEW


def test_explicit_id_and_status_are_preserved_after_mapping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    explicit_id = '87654321-4321-8765-4321-876543218765'

    tasks = _source_with_raw_tasks(
        monkeypatch,
        [
            {
                'id': explicit_id,
                'description': 'Explicit status task',
                'priority': 3,
                'status': 'done',
            }
        ],
    ).get_tasks()

    assert len(tasks) == 1
    assert tasks[0].id == UUID(explicit_id)
    assert tasks[0].status is TaskStatus.DONE


def test_explicit_id_path_does_not_call_uuid_generator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        mock_module,
        'uuid4',
        lambda: (_ for _ in ()).throw(AssertionError('uuid4 should not be called')),
        raising=False,
    )

    tasks = _source_with_raw_tasks(
        monkeypatch,
        [
            {
                'id': '87654321-4321-8765-4321-876543218765',
                'description': 'Existing id task',
                'priority': 3,
                'status': 'done',
            }
        ],
    ).get_tasks()

    assert len(tasks) == 1
    assert tasks[0].id == UUID('87654321-4321-8765-4321-876543218765')


def test_invalid_explicit_id_propagates_uuid_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ValueError):
        _source_with_raw_tasks(
            monkeypatch,
            [
                {
                    'id': 'not-a-uuid',
                    'description': 'Bad id task',
                    'priority': 2,
                }
            ],
        ).get_tasks()


def test_invalid_explicit_status_propagates_status_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(TaskStatusValidationError):
        _source_with_raw_tasks(
            monkeypatch,
            [
                {
                    'id': '87654321-4321-8765-4321-876543218765',
                    'description': 'Bad status task',
                    'priority': 2,
                    'status': 'paused',
                }
            ],
        ).get_tasks()


def test_non_dict_raw_items_raise_type_error(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(TypeError):
        _source_with_raw_tasks(monkeypatch, ['not-a-task-mapping']).get_tasks()


def test_missing_description_raises_value_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ValueError, match='description'):
        _source_with_raw_tasks(
            monkeypatch, [{'priority': 4, 'status': 'new'}]
        ).get_tasks()


def test_missing_priority_defaults_to_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tasks = _source_with_raw_tasks(
        monkeypatch, [{'description': 'Missing priority'}]
    ).get_tasks()

    assert len(tasks) == 1
    assert tasks[0].description == 'Missing priority'
    assert tasks[0].priority == 1
    assert tasks[0].status is TaskStatus.NEW


def test_latency_uses_sleep_without_slowing_down_test(sleep_calls: list[float]) -> None:
    tasks = MockExternalSource().get_tasks()

    assert tasks
    assert sleep_calls == [1]
