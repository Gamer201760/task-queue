from collections.abc import Callable, Iterable, Iterator

from domain.task import Task
from domain.task_status import TaskStatus

type TaskIteratorFactory = Callable[[], Iterator[Task]]


class TaskQueue(Iterable[Task]):
    def __init__(self, source: Iterable[Task] | TaskIteratorFactory) -> None:
        if callable(source):
            self._iterator_factory = source
        else:
            if iter(source) is source:
                raise TypeError('Нужен повторяемый источник или фабрика итераторов')

            self._iterator_factory = lambda: iter(source)

    def __iter__(self) -> Iterator[Task]:
        return self._iterator_factory()

    def filter_by_status(self, status: TaskStatus | str) -> 'TaskQueue':
        normalized_status = TaskStatus.normalize(status)

        def filtered_tasks() -> Iterator[Task]:
            for task in self:
                if task.status is normalized_status:
                    yield task

        return TaskQueue(filtered_tasks)

    def filter_by_priority(
        self,
        *,
        min_priority: int | None = None,
        max_priority: int | None = None,
    ) -> 'TaskQueue':
        def filtered_tasks() -> Iterator[Task]:
            for task in self:
                if not isinstance(task.priority, int):
                    continue

                if min_priority is not None and task.priority < min_priority:
                    continue
                if max_priority is not None and task.priority > max_priority:
                    continue
                yield task

        return TaskQueue(filtered_tasks)
