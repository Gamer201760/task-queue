from random import Random

from domain.task import Task
from repository.generator.rand import RandomJobsSource


def test_random_source_returns_tasks(seeded_random: Random) -> None:
    source = RandomJobsSource(seeded_random)

    tasks = source.get_tasks()

    assert isinstance(tasks, list)
    assert tasks
    assert all(isinstance(task, Task) for task in tasks)


def test_random_source_deterministic_with_fixed_seed() -> None:
    source_a = RandomJobsSource(Random(123))
    source_b = RandomJobsSource(Random(123))

    tasks_a = source_a.get_tasks()
    tasks_b = source_b.get_tasks()

    assert tasks_a == tasks_b


def test_random_source_task_payload_keys(seeded_random: Random) -> None:
    source = RandomJobsSource(seeded_random)

    tasks = source.get_tasks()

    for task in tasks:
        assert isinstance(task.id, int)
        assert 'temperature' in task.payload
        assert 'humidity' in task.payload
