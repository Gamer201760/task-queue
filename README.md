# Лабораторная работа №3 — Очередь задач (`TaskQueue`)

## Цель
Научиться строить ленивые коллекции задач, совместимые со стандартными конструкциями Python, и обеспечивать повторяемую итерацию без преждевременного накопления данных

## Модель `Task`
- основная модель описана в [`domain/task.py`](domain/task.py)
- статусы перечислены в [`domain/task_status.py`](domain/task_status.py)
- исключения домена (`TaskStatusValidationError`, `TaskStatusTransitionError`) и дескрипторы находятся в `domain`
- `Task` принимает `id`, `description`, `priority` и `status`, нормализует строковые статусы и обеспечивает допустимые переходы

## Очередь задач `TaskQueue`
- реализация находится в [`domain/task_queue.py`](domain/task_queue.py)
- поддерживает повторяемую итерацию через фабрику итераторов или повторно итерируемый источник
- ленивые фильтры `filter_by_status(...)` и `filter_by_priority(...)` возвращают новый `TaskQueue`, при этом задачи создаются по мере обхода
- совместима с `for`, `list`, `sum` и любыми другими API, работающими с `Iterable`
- пример использования:

```python
from domain.task_queue import TaskQueue
from domain.task_status import TaskStatus

queue = TaskQueue([...])  # любой повторяемый источник или iterator factory

for task in queue:
    print(task.description)

tasks = list(queue)
total_priority = sum(task.priority for task in queue)

filtered = queue.filter_by_status(TaskStatus.IN_PROGRESS).filter_by_priority(min_priority=2)
```

Фильтрация происходит лениво, новые итерации каждого `TaskQueue` заново создают источник, поэтому `queue` и `filtered` можно обходить многократно

## Источники задач
- контракт источника описан в [`usecase/interface.py`](usecase/interface.py) через `DataSource`
- обработка коллекции реализована в [`usecase/process.py`](usecase/process.py), `ProcessTasks.build_queue()` объединяет источники с помощью `itertools.chain` и возвращает `TaskQueue`
- `MockExternalSource` (`repository/api/mock.py`) имитирует внешний API, создаёт `Task` из полученных словарей и добавляет UUID/статус по умолчанию
- `TaskJsonSource` (`repository/file/json.py`) читает JSONL-файл `tasks.jsonl`, ожидает по одному JSON-объекту задачи на строку, проверяет обязательные поля, поддерживает `id`, `priority`, `status` и создаёт доменные `Task` по мере обхода очереди
- `RandomJobsSource` (`repository/generator/rand.py`) генерирует повторяемый набор сырого описания задач, преобразует в `Task` и возвращает `TaskQueue`

Все источники возвращают `TaskQueue`, поэтому создание доменных `Task` происходит лениво во время обхода. Для JSONL-источника это означает чтение файла построчно без кэширования всего содержимого: каждый новый обход очереди заново открывает файл и читает его сначала

Пример `tasks.jsonl`:

```json
{"id":"12345678-1234-5678-1234-567812345678", "description":"Проверить входные данные JSONL-источника", "priority":2, "status":"new"}
{"id":"87654321-4321-8765-4321-876543218765", "description":"Обновить статус задачи после обработки", "priority":3, "status":"in_progress"}
{"description":"Сформировать итоговый отчёт"}
```

## Use case и CLI
- `ProcessTasks.execute()` принимает очередь и логирует каждый `Task`, при необходимости строит очередь из добавленных источников
- `adapter/cli/main.py` собирает `MockExternalSource`, `TaskJsonSource` (по `--file`) и `RandomJobsSource` (по `--seed`), строит комбинированную очередь через `process.build_queue()`, при необходимости лениво применяет `filter_by_status(...)` и `filter_by_priority(...)`, после чего выполняет один потоковый проход по выбранной очереди
- CLI аргументы: `--file` (по умолчанию `./tasks.jsonl`), `--seed` (по умолчанию `1`), `--status`, `--min-priority`, `--max-priority`
- пример запуска:

```bash
uv run python -m adapter.cli.main --file ./tasks.jsonl --seed 42 --status in_progress --min-priority 2 --max-priority 4
```

## Запуск и проверки
Требуется Python 3.13+ и `uv`

### Через `make`

Аргументы CLI можно передавать через переменную `ARGS`

```bash
make install
make run
make run ARGS="--status in_progress"
make run ARGS="--file ./tasks.jsonl --seed 42 --min-priority 2 --max-priority 4"
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
