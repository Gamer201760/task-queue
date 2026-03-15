from uuid import UUID

from domain.task import Task
from domain.task_status import TaskStatus


def test_task_defaults_priority_to_one_when_omitted() -> None:
    task_id = '12345678-1234-5678-1234-567812345678'

    task = Task(task_id, description='Task without explicit priority')

    assert task.id == UUID(task_id)
    assert task.description == 'Task without explicit priority'
    assert task.priority == 1
    assert task.status is TaskStatus.NEW
