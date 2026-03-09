import pytest

from domain.task import Task
from repository.api import mock as mock_module


def test_mock_source_returns_tasks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mock_module.time, 'sleep', lambda _: None)
    source = mock_module.MockExternalSource()

    tasks = source.get_tasks()

    assert tasks == [Task(id=1, payload={'palka': 'copalka'})]


def test_mock_source_task_contents(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mock_module.time, 'sleep', lambda _: None)
    source = mock_module.MockExternalSource()

    task = source.get_tasks()[0]

    assert task.id == 1
    assert task.payload == {'palka': 'copalka'}
