import json
from pathlib import Path

from domain.task import Task


class TaskJsonSource:
    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)

    def get_tasks(self) -> list[Task]:
        if not self._path.exists():
            raise FileNotFoundError(f'Файл с задачами не найден: {self._path}')
        if not self._path.is_file():
            raise IsADirectoryError(f'Ожидался файл, но получен каталог: {self._path}')

        # Чтение файла и парсинг JSON
        try:
            text = self._path.read_text(encoding='utf-8')
        except OSError as e:
            raise OSError(f'Не удалось прочитать файл с задачами: {self._path}') from e

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f'Некорректный JSON в файле с задачами: {self._path}'
            ) from e

        if not isinstance(data, list):
            raise TypeError(
                f'Корневой элемент JSON должен быть списком задач, получено: {type(data).__name__}'
            )

        # Каждый элемент массива превращаем в Task
        return [Task.from_json(item) for item in data]
