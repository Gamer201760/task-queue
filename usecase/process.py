from logging import getLogger

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

    def execute(self) -> None:
        for src in self._sources:
            logger.info(
                f'Process tasks from {src.__class__.__name__}: {src.get_tasks()}'
            )
