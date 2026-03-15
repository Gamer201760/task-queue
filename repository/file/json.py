import json
from pathlib import Path
from uuid import uuid4

from domain.task import Task


class TaskJsonSource:
    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)

    def get_tasks(self) -> list[Task]:
        if not self._path.exists():
            raise FileNotFoundError(f'Файл с задачами не найден: {self._path}')
        if not self._path.is_file():
            raise IsADirectoryError(f'Ожидался файл, но получен каталог: {self._path}')

        try:
            with self._path.open(encoding='utf-8') as file:
                raw_tasks = json.load(file)
        except json.JSONDecodeError as err:
            raise ValueError(
                f'Некорректный JSON в файле с задачами: {self._path}'
            ) from err

        if not isinstance(raw_tasks, list):
            raise TypeError(
                f'Корневой элемент JSON должен быть списком задач, получено: {type(raw_tasks).__name__}'
            )

        tasks: list[Task] = []
        for item in raw_tasks:
            if not isinstance(item, dict):
                raise TypeError('Каждый элемент JSON должен быть объектом задачи')

            required_fields = ('description',)
            missing_fields = [field for field in required_fields if field not in item]
            if missing_fields:
                raise ValueError(
                    'Отсутствуют обязательные поля задачи: ' + ', '.join(missing_fields)
                )

            priority = item.get('priority', 1)

            if 'status' in item:
                task = Task(
                    item.get('id', uuid4()),
                    item['description'],
                    priority,
                    item['status'],
                )
            else:
                task = Task(
                    item.get('id', uuid4()),
                    item['description'],
                    priority,
                )

            tasks.append(task)

        return tasks
