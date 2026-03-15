# Лабораторная работа №2 — Дескрипторы и `property`

## Цель
Освоить защиту инвариантов доменной модели через пользовательские дескрипторы и `property`

В центре проекта находится класс `Task` с безопасным публичным API, валидацией полей и контролируемыми переходами статуса

## Модель `Task`
- основная модель находится в [`domain/task.py`](domain/task.py)
- перечисление статусов находится в [`domain/task_status.py`](domain/task_status.py)
- ошибки домена находятся в [`domain/error.py`](domain/error.py)
- `Task(id: str | UUID, description: str, priority: int = 1, status: TaskStatus | str = TaskStatus.NEW)` принимает строковый UUID или `UUID`, а внутри хранит значение как `UUID`
- `description` и `priority` валидируются дескрипторами `String` и `Int` из [`domain/descriptor.py`](domain/descriptor.py), если `priority` не передан, используется значение `1`
- `status` реализован через `Enum + property`, строковое значение нормализуется в `TaskStatus`, а недопустимые переходы вызывают `TaskStatusTransitionError`
- `created_at` заполняется автоматически при создании объекта
- `is_ready` возвращает `True`, пока задача находится в статусе `TaskStatus.NEW`

### Демонстрация дескрипторов
- data descriptors показаны в [`domain/descriptor.py`](domain/descriptor.py) через `String` и `Int`
- non-data descriptor показан в [`domain/non_data.py`](domain/non_data.py) через `NonDataStatusLabel`
- учебный класс `DemoTask` показывает, что non-data descriptor можно затенить атрибутом экземпляра

### Разрешённые переходы статуса
- `new -> in_progress`
- `in_progress -> done`
- повторное присваивание того же статуса допустимо

## Источники задач
- контракт источника описан в [`usecase/interface.py`](usecase/interface.py) через `DataSource`
- обработчик источников находится в [`usecase/process.py`](usecase/process.py)
- CLI находится в [`adapter/cli/main.py`](adapter/cli/main.py)
- каждый источник сам преобразует сырые данные в доменный `Task`

### `TaskJsonSource`
- реализация находится в [`repository/file/json.py`](repository/file/json.py)
- пример входного файла находится в [`tasks.json`](tasks.json)
- источник читает JSON-файл и ожидает корневой список объектов
- обязательные поля элемента: `description`
- опциональные поля: `id`, `priority`, `status`
- если `id` отсутствует, источник генерирует `uuid4()`
- если `priority` отсутствует, используется значение `1`
- если `status` отсутствует, используется значение по умолчанию из `Task`

Пример элемента JSON

```json
{
  "description": "Подготовить отчёт",
  "priority": 2,
  "id": "12345678-1234-5678-1234-567812345678",
  "status": "in_progress"
}
```

### `MockExternalSource`
- реализация находится в [`repository/api/mock.py`](repository/api/mock.py)
- источник имитирует внешний API
- получает сырой список задач во внутреннем `_fetch_tasks()`
- преобразует каждый словарь в `Task`
- при отсутствии `id` генерирует новый UUID
- при отсутствии `priority` использует `1`
- при отсутствии `status` оставляет значение по умолчанию

### `RandomJobsSource`
- реализация находится в [`repository/generator/rand.py`](repository/generator/rand.py)
- источник генерирует сырые записи задач с помощью `random.Random`
- затем преобразует их в `Task`
- создаёт UUID и случайные поля так, чтобы результат был воспроизводим при одинаковом seed
- поддерживает проверку обязательных полей до создания доменного объекта
- если `priority` отсутствует в сырой записи, использует `1`

## Запуск и проверки
Требуется Python 3.13+ и `uv`

### Через `make`

```bash
make install
make run
make test
make lint
make typecheck
make pre-commit
```

### Через `uv`

```bash
uv sync
uv run python -m adapter.cli.main
uv run pytest -v
uv run ruff check .
uv run mypy .
```

### Аргументы CLI
- `--file` — путь до JSON-файла с задачами, по умолчанию `./tasks.json`
- `--seed` — seed для `RandomJobsSource`, по умолчанию `1`

Пример запуска

```bash
uv run python -m adapter.cli.main --file ./tasks.json --seed 42
```

## Тесты
- тесты дескрипторов находятся в [`test/test_string_descriptor.py`](test/test_string_descriptor.py) и [`test/test_int_descriptor.py`](test/test_int_descriptor.py)
- тест non-data descriptor находится в [`test/test_non_data_descriptor.py`](test/test_non_data_descriptor.py)
- прямые тесты модели `Task` находятся в [`test/test_task.py`](test/test_task.py) и [`test/test_task_default_priority.py`](test/test_task_default_priority.py)
- тесты источников находятся в [`test/test_json_source.py`](test/test_json_source.py), [`test/test_mock_source.py`](test/test_mock_source.py) и [`test/test_rand_source.py`](test/test_rand_source.py)
- покрываются UUID, статусы, обязательные поля, значения по умолчанию и ошибки валидации
