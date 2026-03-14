from random import Random
from typing import cast
from uuid import UUID

from domain.task import Task
from domain.task_status import TaskStatus


class RandomJobsSource:
    def __init__(self, rnd: Random) -> None:
        self._rnd = rnd

    def _generate_raw_tasks(self) -> list[dict[str, object]]:
        actions = ('Review', 'Update', 'Prepare', 'Check', 'Close')
        targets = (
            'backlog',
            'task queue',
            'release notes',
            'support inbox',
            'deployment plan',
        )
        statuses = tuple(status.value for status in TaskStatus)

        raw_tasks: list[dict[str, object]] = []
        for _ in range(self._rnd.randint(1, 5)):
            raw_task: dict[str, object] = {
                'id': self._generate_task_id(),
                'description': f'{self._rnd.choice(actions)} {self._rnd.choice(targets)}',
                'priority': self._rnd.randint(1, 5),
            }

            if self._rnd.choice((True, False)):
                raw_task['status'] = self._rnd.choice(statuses)

            raw_tasks.append(raw_task)

        return raw_tasks

    def _generate_task_id(self) -> UUID:
        return UUID(int=self._rnd.getrandbits(128), version=4)

    def _task_from_raw(self, raw_task: object) -> Task:
        if not isinstance(raw_task, dict):
            raise TypeError('Each raw task must be a dict')

        missing_fields = [
            field for field in ('description', 'priority') if field not in raw_task
        ]
        if missing_fields:
            raise ValueError(
                'Missing required task fields: ' + ', '.join(missing_fields)
            )

        task_id = (
            cast(str | UUID, raw_task['id'])
            if 'id' in raw_task
            else self._generate_task_id()
        )
        description = cast(str, raw_task['description'])
        priority = cast(int, raw_task['priority'])

        if 'status' in raw_task:
            return Task(
                task_id,
                description,
                priority,
                cast(TaskStatus | str, raw_task['status']),
            )

        return Task(task_id, description, priority)

    def get_tasks(self) -> list[Task]:
        return [
            self._task_from_raw(raw_task) for raw_task in self._generate_raw_tasks()
        ]
