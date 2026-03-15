import time
from uuid import uuid4

from domain.task import Task


class MockExternalSource:
    def _fetch_tasks(self) -> list[object]:
        time.sleep(1)
        return [
            {
                'description': 'Check external queue',
                'priority': 1,
            },
            {
                'id': 'f3a9b7f7-3b23-4f87-aef7-1d22d587d9f1',
                'description': 'Sync remote task state',
                'priority': 2,
                'status': 'in_progress',
            },
        ]

    def get_tasks(self) -> list[Task]:
        tasks: list[Task] = []

        for item in self._fetch_tasks():
            if not isinstance(item, dict):
                raise TypeError('Каждая запись задачи должна быть словарём')

            missing_fields = [field for field in ('description',) if field not in item]
            if missing_fields:
                raise ValueError(
                    'Отсутствуют обязательные поля задачи: ' + ', '.join(missing_fields)
                )

            task_id = item['id'] if 'id' in item else uuid4()
            priority = item.get('priority', 1)

            if 'status' in item:
                task = Task(
                    task_id,
                    item['description'],
                    priority,
                    item['status'],
                )
            else:
                task = Task(
                    task_id,
                    item['description'],
                    priority,
                )

            tasks.append(task)

        return tasks
