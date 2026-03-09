import logging

import pytest

from domain.task import Task
from repository.api.mock import MockExternalSource
from usecase.interface import DataSource
from usecase.process import ProcessTasks


class RecordingSource:
    def __init__(self, name: str) -> None:
        self.name = name
        self.calls: int = 0

    def get_tasks(self) -> list[Task]:
        self.calls += 1
        return [Task(id=1, payload={'source': self.name})]


def test_process_tasks_create_empty() -> None:
    process = ProcessTasks()

    assert process._sources == []


def test_process_tasks_create_with_sources(
    mock_external_source: MockExternalSource,
) -> None:
    sources: list[DataSource] = [mock_external_source]
    process = ProcessTasks(sources)

    assert process._sources is sources
    assert process._sources == sources


def test_add_source_valid(mock_external_source: MockExternalSource) -> None:
    process = ProcessTasks()

    process.add_source(mock_external_source)

    assert process._sources == [mock_external_source]


def test_add_source_invalid() -> None:
    process = ProcessTasks()

    with pytest.raises(TypeError):
        process.add_source(object())


def test_execute_logs_and_calls_sources(caplog: pytest.LogCaptureFixture) -> None:
    source_a = RecordingSource('a')
    source_b = RecordingSource('b')
    process = ProcessTasks([source_a, source_b])

    with caplog.at_level(logging.INFO, logger='usecase.process'):
        process.execute()

    assert source_a.calls == 1
    assert source_b.calls == 1
    assert any(
        'Process tasks from RecordingSource' in rec.message for rec in caplog.records
    )
