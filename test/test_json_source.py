import json
import os
import stat
from pathlib import Path
from uuid import UUID

import pytest

from domain.task import Task
from domain.task_status import TaskStatus
from repository.file.json import TaskJsonSource


def _write_json_file(tmp_path: Path, payload: object) -> Path:
    path = tmp_path / 'tasks.json'
    path.write_text(json.dumps(payload), encoding='utf-8')
    return path


def test_get_tasks_returns_task_objects_for_valid_json_with_full_fields(
    tmp_path: Path,
) -> None:
    path = _write_json_file(
        tmp_path,
        [
            {
                'id': '12345678-1234-5678-1234-567812345678',
                'description': 'Write JSON tests',
                'priority': 3,
                'status': 'in_progress',
            },
            {
                'id': '87654321-4321-8765-4321-876543218765',
                'description': 'Review JSON tests',
                'priority': 5,
                'status': 'done',
            },
        ],
    )

    tasks = TaskJsonSource(path).get_tasks()

    assert len(tasks) == 2
    assert all(isinstance(task, Task) for task in tasks)

    assert tasks[0].id == UUID('12345678-1234-5678-1234-567812345678')
    assert tasks[0].description == 'Write JSON tests'
    assert tasks[0].priority == 3
    assert tasks[0].status is TaskStatus.IN_PROGRESS

    assert tasks[1].id == UUID('87654321-4321-8765-4321-876543218765')
    assert tasks[1].description == 'Review JSON tests'
    assert tasks[1].priority == 5
    assert tasks[1].status is TaskStatus.DONE


def test_get_tasks_generates_uuid_and_defaults_priority_and_status_when_optional_fields_are_missing(
    tmp_path: Path,
) -> None:
    path = _write_json_file(
        tmp_path,
        [{'description': 'Create task from JSON'}],
    )

    tasks = TaskJsonSource(path).get_tasks()

    assert len(tasks) == 1
    assert isinstance(tasks[0].id, UUID)
    assert tasks[0].description == 'Create task from JSON'
    assert tasks[0].priority == 1
    assert tasks[0].status is TaskStatus.NEW


def test_get_tasks_raises_file_not_found_error_for_missing_file(
    tmp_path: Path,
) -> None:
    missing_path = tmp_path / 'missing.json'

    with pytest.raises(FileNotFoundError):
        TaskJsonSource(missing_path).get_tasks()


def test_get_tasks_raises_is_a_directory_error_for_directory_path(
    tmp_path: Path,
) -> None:
    with pytest.raises(IsADirectoryError):
        TaskJsonSource(tmp_path).get_tasks()


def test_get_tasks_raises_value_error_for_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / 'invalid.json'
    path.write_text('{"broken": ', encoding='utf-8')

    with pytest.raises(ValueError):
        TaskJsonSource(path).get_tasks()


def test_get_tasks_raises_type_error_when_json_root_is_not_a_list(
    tmp_path: Path,
) -> None:
    path = _write_json_file(
        tmp_path,
        {
            'id': '12345678-1234-5678-1234-567812345678',
            'description': 'Single task object',
            'priority': 2,
        },
    )

    with pytest.raises(TypeError):
        TaskJsonSource(path).get_tasks()


def test_get_tasks_raises_type_error_when_list_item_is_not_a_dict(
    tmp_path: Path,
) -> None:
    path = _write_json_file(
        tmp_path,
        [
            {
                'id': '12345678-1234-5678-1234-567812345678',
                'description': 'Valid task',
                'priority': 2,
                'status': 'new',
            },
            'not-a-task-mapping',
        ],
    )

    with pytest.raises(TypeError):
        TaskJsonSource(path).get_tasks()


def test_get_tasks_raises_value_error_when_description_is_missing(
    tmp_path: Path,
) -> None:
    path = _write_json_file(tmp_path, [{'priority': 2, 'status': 'new'}])

    with pytest.raises(ValueError, match='description'):
        TaskJsonSource(path).get_tasks()


def test_get_tasks_defaults_priority_to_one_when_priority_is_missing(
    tmp_path: Path,
) -> None:
    path = _write_json_file(tmp_path, [{'description': 'Missing priority'}])

    tasks = TaskJsonSource(path).get_tasks()

    assert len(tasks) == 1
    assert tasks[0].description == 'Missing priority'
    assert tasks[0].priority == 1
    assert tasks[0].status is TaskStatus.NEW


def test_get_tasks_raises_permission_error_for_unreadable_file(
    tmp_path: Path,
) -> None:
    path = _write_json_file(
        tmp_path,
        [{'description': 'Hidden task', 'priority': 4, 'status': 'new'}],
    )
    original_mode = stat.S_IMODE(path.stat().st_mode)
    path.chmod(0)

    try:
        if os.access(path, os.R_OK):
            pytest.skip(
                'permission bits are not enforced reliably on this platform/filesystem'
            )

        with pytest.raises(PermissionError):
            TaskJsonSource(path).get_tasks()
    finally:
        path.chmod(original_mode)
