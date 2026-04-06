import json
from pathlib import Path
from uuid import uuid4

from domain.task import Task
from domain.task_queue import TaskQueue
from domain.task_status import TaskStatus


class TaskJsonSource:
    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)

    def _task_from_raw(self, item: object) -> Task:
        if not isinstance(item, dict):
            raise TypeError('Каждая запись задачи должна быть словарём')

        missing_fields = [field for field in ('description',) if field not in item]
        if missing_fields:
            raise ValueError(
                'Отсутствуют обязательные поля задачи: ' + ', '.join(missing_fields)
            )

        if 'id' not in item:
            item['id'] = uuid4()

        priority = item.get('priority', 1)
        status = item.get('status', TaskStatus.NEW)

        return Task(
            item['id'],
            item['description'],
            priority,
            status,
        )

    def get_tasks(self) -> TaskQueue:
        def iter_raw_tasks():
            if not self._path.exists():
                raise FileNotFoundError(f'Файл с задачами не найден: {self._path}')
            if not self._path.is_file():
                raise IsADirectoryError(
                    f'Ожидался файл, но получен каталог: {self._path}'
                )

            with self._path.open(encoding='utf-8') as file:
                for line_number, line in enumerate(file, start=1):
                    raw_line = line.strip()
                    if not raw_line:
                        continue

                    try:
                        yield json.loads(raw_line)
                    except json.JSONDecodeError as err:
                        raise ValueError(
                            f'Некорректный JSONL в файле с задачами: {self._path}, строка {line_number}'
                        ) from err

        def iter_tasks():
            for item in iter_raw_tasks():
                yield self._task_from_raw(item)

        return TaskQueue(iter_tasks)
