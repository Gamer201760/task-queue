from pathlib import Path

import pytest

from domain.task import Task
from repository.file.json import TaskJsonSource


def test_json_source_reads_valid_file(valid_json_file: Path) -> None:
    source = TaskJsonSource(valid_json_file)

    tasks = source.get_tasks()

    assert tasks == [
        Task(id=1, payload={'name': 'alpha'}),
        Task(id=2, payload={'name': 'beta'}),
    ]


def test_json_source_missing_file(tmp_path: Path) -> None:
    source = TaskJsonSource(tmp_path / 'missing.json')

    with pytest.raises(FileNotFoundError):
        source.get_tasks()


def test_json_source_path_is_directory(tmp_path: Path) -> None:
    source = TaskJsonSource(tmp_path)

    with pytest.raises(IsADirectoryError):
        source.get_tasks()


def test_json_source_invalid_json(invalid_json_file: Path) -> None:
    source = TaskJsonSource(invalid_json_file)

    with pytest.raises(ValueError):
        source.get_tasks()


def test_json_source_root_not_list(non_list_json_file: Path) -> None:
    source = TaskJsonSource(non_list_json_file)

    with pytest.raises(TypeError):
        source.get_tasks()


def test_json_source_unreadable_file(tmp_path: Path) -> None:
    path = tmp_path / 'locked.json'
    path.write_text('[]', encoding='utf-8')
    path.chmod(0o000)
    source = TaskJsonSource(path)

    with pytest.raises(OSError):
        source.get_tasks()

    path.chmod(0o644)
