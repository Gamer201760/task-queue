import json
from pathlib import Path
from random import Random

import pytest

from domain.task import Task
from repository.api.mock import MockExternalSource
from repository.file.json import TaskJsonSource
from repository.generator.rand import RandomJobsSource
from usecase.process import ProcessTasks


@pytest.fixture
def task() -> Task:
    return Task(id=1, payload={'name': 'alpha'})


@pytest.fixture
def tasks() -> list[Task]:
    return [
        Task(id=1, payload={'name': 'alpha'}),
        Task(id=2, payload={'name': 'beta'}),
    ]


@pytest.fixture
def valid_json_file(tmp_path: Path) -> Path:
    path = tmp_path / 'tasks.json'
    data = [
        {'id': 1, 'payload': {'name': 'alpha'}},
        {'id': 2, 'payload': {'name': 'beta'}},
    ]
    path.write_text(json.dumps(data), encoding='utf-8')
    return path


@pytest.fixture
def invalid_json_file(tmp_path: Path) -> Path:
    path = tmp_path / 'invalid.json'
    path.write_text('{invalid', encoding='utf-8')
    return path


@pytest.fixture
def non_list_json_file(tmp_path: Path) -> Path:
    path = tmp_path / 'not_list.json'
    path.write_text(
        json.dumps({'id': 1, 'payload': {'name': 'alpha'}}), encoding='utf-8'
    )
    return path


@pytest.fixture
def seeded_random() -> Random:
    return Random(123)


@pytest.fixture
def mock_external_source() -> MockExternalSource:
    return MockExternalSource()


@pytest.fixture
def task_json_source(valid_json_file: Path) -> TaskJsonSource:
    return TaskJsonSource(valid_json_file)


@pytest.fixture
def random_jobs_source(seeded_random: Random) -> RandomJobsSource:
    return RandomJobsSource(seeded_random)


@pytest.fixture
def process_tasks_with_sources(
    mock_external_source: MockExternalSource,
    task_json_source: TaskJsonSource,
    random_jobs_source: RandomJobsSource,
) -> ProcessTasks:
    return ProcessTasks([mock_external_source, task_json_source, random_jobs_source])
