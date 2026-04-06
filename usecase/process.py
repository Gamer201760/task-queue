from itertools import chain
from logging import getLogger

from domain.task_queue import TaskQueue
from usecase.interface import DataSource

logger = getLogger(__name__)


class ProcessTasks:
    def __init__(self, sources: list[DataSource] | None = None) -> None:
        self._sources = sources or []

    def add_source(self, src: DataSource) -> None:
        if isinstance(src, DataSource):
            self._sources.append(src)
        else:
            raise TypeError(
                f'Источник {src.__class__.__name__} должен соотвествовать контракту DataSource'
            )

    def build_queue(self) -> TaskQueue:
        source_queues = tuple(src.get_tasks() for src in self._sources)

        return TaskQueue(lambda: chain.from_iterable(source_queues))

    def execute(self, queue: TaskQueue | None = None) -> None:
        tasks = queue if queue is not None else self.build_queue()

        processed_count = 0
        for task in tasks:
            processed_count += 1
            logger.info('Process task: %s', task)

        logger.info('Processed tasks: %s', processed_count)
