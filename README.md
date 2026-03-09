# Лабораторная работа №1. Источники задач и контракты

Подсистема приёма задач в платформе обработки задач. Задачи поступают из различных источников, не связанных наследованием, но реализующих единый поведенческий контракт через `typing.Protocol`.

## Установка и запуск

Требуется Python 3.13+ и [uv](https://docs.astral.sh/uv/).

### Через Makefile

```bash
make install       # установить зависимости
make run           # запустить приложение
make test          # запустить тесты
make lint          # проверка линтером (ruff)
make typecheck     # проверка типов (mypy)
make pre-commit    # lint + typecheck + test
```

### Через uv напрямую

```bash
uv sync                                # установить зависимости
uv run python -m adapter.cli.main      # запуск приложения
uv run pytest -v                       # запустить тесты
uv run ruff check .                    # линтер
uv run mypy .                          # проверка типов
```

### Аргументы командной строки

| Аргумент | По умолчанию   | Описание                            |
| -------- | -------------- | ----------------------------------- |
| `--file` | `./tasks.json` | Путь до файла с задачами            |
| `--seed` | `1`            | Seed для генератора случайных задач |

```bash
uv run python -m adapter.cli.main --file path/to/tasks.json --seed 42
make run ARGS="--file path/to/tasks.json --seed 42"
```

## Архитектура

Проект следует принципам Clean Architecture. Зависимости направлены строго внутрь:

```
adapter/             точка входа (CLI)
repository/          реализации источников задач
  ├── api/           API заглушка
  ├── file/          чтение из файла
  └── generator/     программная генерация
usecase/             бизнес логика и контракт
domain/              ядро: сущность Task
```

**Направление зависимостей:** `adapter/ -> repository/ -> usecase/ -> domain/`

Внутренние слои ничего не знают о внешних. `domain/` не импортирует никого, `usecase/` зависит только от `domain/`.

### Контракт DataSource

Единый контракт для всех источников задач описан через `typing.Protocol`:

```python
@runtime_checkable
class DataSource(Protocol):
    def get_tasks(self) -> list[Task]: ...
```

Любой класс, реализующий метод `get_tasks() -> list[Task]`, автоматически удовлетворяет контракту. Общий базовый класс не нужен (duck typing). При добавлении источника в `ProcessTasks` выполняется runtime проверка через `isinstance(src, DataSource)`.

### Сущность Task

```python
@dataclass
class Task:
    id: int
    payload: dict
```

Минимальная структура: идентификатор и произвольные данные.

## Источники задач

В проекте реализованы три источника, каждый из которых удовлетворяет контракту `DataSource`:

### 1. Загрузка из файла (`TaskJsonSource`)

Читает задачи из JSON файла с валидацией формата.

```python
source = TaskJsonSource('./tasks.json')
tasks = source.get_tasks()  # -> [Task(id=33, payload={...}), Task(id=1233, payload={...})]
```

**Расположение:** [`repository/file/json.py`](repository/file/json.py)

### 2. Программная генерация (`RandomJobsSource`)

Генерирует случайные задачи с данными о температуре и влажности.

```python
source = RandomJobsSource(Random(42))
tasks = source.get_tasks()  # -> [Task(id=..., payload={'temperature': ..., 'humidity': ...}), ...]
```

**Расположение:** [`repository/generator/rand.py`](repository/generator/rand.py)

### 3. API заглушка (`MockExternalSource`)

Имитирует внешний источник задач с сетевой задержкой (`time.sleep`).

```python
source = MockExternalSource()
tasks = source.get_tasks()  # -> [Task(id=1, payload={'palka': 'copalka'})]
```

**Расположение:** [`repository/api/mock.py`](repository/api/mock.py)

## Как добавить новый источник

Достаточно создать класс с методом `get_tasks() -> list[Task]`. Наследование не требуется:

```python
# repository/my_source/source.py
from domain.task import Task

class MyNewSource:
    def get_tasks(self) -> list[Task]:
        return [Task(id=999, payload={'key': 'value'})]
```

После этого источник можно передать в `ProcessTasks`:

```python
process = ProcessTasks()
process.add_source(MyNewSource())  # isinstance проверка пройдёт автоматически
process.execute()
```

Существующий код изменять не нужно (Open/Closed Principle).
