from domain.task import Task
from repository.api.mock import MockExternalSource
from repository.file.json import TaskJsonSource
from repository.generator.rand import RandomJobsSource
from usecase.interface import DataSource


class GoodSource:
    def get_tasks(self) -> list[Task]:
        return [Task(id=1, payload={'x': 1})]


class BadSource:
    def fetch(self) -> list[Task]:
        return [Task(id=1, payload={'x': 1})]


def test_datasource_protocol_accepts_implementor() -> None:
    source = GoodSource()

    assert isinstance(source, DataSource)


def test_datasource_protocol_rejects_missing_method() -> None:
    source = BadSource()

    assert not isinstance(source, DataSource)


def test_repository_sources_implement_protocol(
    mock_external_source: MockExternalSource,
    task_json_source: TaskJsonSource,
    random_jobs_source: RandomJobsSource,
) -> None:
    assert isinstance(mock_external_source, DataSource)
    assert isinstance(task_json_source, DataSource)
    assert isinstance(random_jobs_source, DataSource)
