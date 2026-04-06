import json
import os
import stat
from pathlib import Path
from uuid import UUID

import pytest

from domain.task import Task
from domain.task_status import TaskStatus
from repository.file.json import TaskJsonSource


def _write_jsonl_file(tmp_path: Path, payload: list[object]) -> Path:
    path = tmp_path / 'tasks.jsonl'
    path.write_text(
        '\n'.join(json.dumps(item) for item in payload) + '\n',
        encoding='utf-8',
    )
    return path


def test_get_tasks_returns_task_objects_for_valid_json_with_full_fields(
    tmp_path: Path,
) -> None:
    path = _write_jsonl_file(
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

    tasks = list(TaskJsonSource(path).get_tasks())

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
    path = _write_jsonl_file(
        tmp_path,
        [{'description': 'Create task from JSON'}],
    )

    tasks = list(TaskJsonSource(path).get_tasks())

    assert len(tasks) == 1
    assert isinstance(tasks[0].id, UUID)
    assert tasks[0].description == 'Create task from JSON'
    assert tasks[0].priority == 1
    assert tasks[0].status is TaskStatus.NEW


def test_get_tasks_raises_file_not_found_error_for_missing_file(
    tmp_path: Path,
) -> None:
    missing_path = tmp_path / 'missing.jsonl'

    with pytest.raises(FileNotFoundError):
        list(TaskJsonSource(missing_path).get_tasks())


def test_get_tasks_raises_is_a_directory_error_for_directory_path(
    tmp_path: Path,
) -> None:
    with pytest.raises(IsADirectoryError):
        list(TaskJsonSource(tmp_path).get_tasks())


def test_get_tasks_raises_value_error_for_invalid_jsonl_line(tmp_path: Path) -> None:
    path = tmp_path / 'invalid.jsonl'
    path.write_text('{"broken": \n', encoding='utf-8')

    with pytest.raises(ValueError, match='строка 1'):
        list(TaskJsonSource(path).get_tasks())


def test_get_tasks_raises_type_error_when_jsonl_line_is_not_a_dict(
    tmp_path: Path,
) -> None:
    path = _write_jsonl_file(
        tmp_path,
        ['not-a-task-mapping'],
    )

    with pytest.raises(TypeError):
        list(TaskJsonSource(path).get_tasks())


def test_get_tasks_raises_type_error_when_list_item_is_not_a_dict(
    tmp_path: Path,
) -> None:
    path = _write_jsonl_file(
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
        list(TaskJsonSource(path).get_tasks())


def test_get_tasks_raises_value_error_when_description_is_missing(
    tmp_path: Path,
) -> None:
    path = _write_jsonl_file(tmp_path, [{'priority': 2, 'status': 'new'}])

    with pytest.raises(ValueError, match='description'):
        list(TaskJsonSource(path).get_tasks())


def test_get_tasks_defaults_priority_to_one_when_priority_is_missing(
    tmp_path: Path,
) -> None:
    path = _write_jsonl_file(tmp_path, [{'description': 'Missing priority'}])

    tasks = list(TaskJsonSource(path).get_tasks())

    assert len(tasks) == 1
    assert tasks[0].description == 'Missing priority'
    assert tasks[0].priority == 1
    assert tasks[0].status is TaskStatus.NEW


def test_get_tasks_raises_permission_error_for_unreadable_file(
    tmp_path: Path,
) -> None:
    path = _write_jsonl_file(
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
            list(TaskJsonSource(path).get_tasks())
    finally:
        path.chmod(original_mode)


def test_get_tasks_reopens_jsonl_file_for_each_new_iteration(tmp_path: Path) -> None:
    path = _write_jsonl_file(
        tmp_path,
        [{'description': 'First version', 'priority': 1, 'status': 'new'}],
    )
    queue = TaskJsonSource(path).get_tasks()

    first_pass = list(queue)

    path.write_text(
        json.dumps(
            {
                'description': 'Second version',
                'priority': 2,
                'status': 'done',
            }
        )
        + '\n',
        encoding='utf-8',
    )

    second_pass = list(queue)

    assert [task.description for task in first_pass] == ['First version']
    assert [task.description for task in second_pass] == ['Second version']
    assert second_pass[0].priority == 2
    assert second_pass[0].status is TaskStatus.DONE
