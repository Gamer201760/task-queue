from random import Random
from uuid import UUID

from domain.task import Task
from domain.task_queue import TaskQueue
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
        return UUID(
            int=self._rnd.getrandbits(128), version=4
        )  # Нужно для повторяемости тестов

    def _task_from_raw(self, raw_task: object) -> Task:
        if not isinstance(raw_task, dict):
            raise TypeError('Каждая запись задачи должна быть словарём')

        missing_fields = [field for field in ('description',) if field not in raw_task]
        if missing_fields:
            raise ValueError(
                'Отсутствуют обязательные поля задачи: ' + ', '.join(missing_fields)
            )

        if 'id' not in raw_task:
            raw_task['id'] = self._generate_task_id()

        priority = raw_task.get('priority', 1)
        status = raw_task.get('status', TaskStatus.NEW)

        return Task(
            raw_task['id'],
            raw_task['description'],
            priority,
            status,
        )

    def get_tasks(self) -> TaskQueue:
        payload: list[object] | None = None

        def load_raw_tasks() -> list[object]:
            nonlocal payload

            if payload is None:
                payload = list(self._generate_raw_tasks())

            return payload

        def iter_tasks():
            for raw_task in load_raw_tasks():
                yield self._task_from_raw(raw_task)

        return TaskQueue(iter_tasks)
