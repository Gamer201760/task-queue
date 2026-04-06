import argparse
from logging import INFO, basicConfig, getLogger
from random import Random

from domain.error import TaskStatusValidationError
from domain.task_status import TaskStatus
from repository.api.mock import MockExternalSource
from repository.file.json import TaskJsonSource
from repository.generator.rand import RandomJobsSource
from usecase.process import ProcessTasks

basicConfig(format='[%(levelname)s] %(name)s %(asctime)s %(message)s', level=INFO)
logger = getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--file', default='./tasks.jsonl', help='Путь до JSONL-файла с задачами'
    )
    parser.add_argument(
        '--seed', type=int, default=1, help='Seed для генератора случайных задач'
    )
    parser.add_argument('--status', help='Фильтр задач по статусу')
    parser.add_argument('--min-priority', type=int, help='Минимальный приоритет задач')
    parser.add_argument('--max-priority', type=int, help='Максимальный приоритет задач')
    args = parser.parse_args()

    if (
        args.min_priority is not None
        and args.max_priority is not None
        and args.min_priority > args.max_priority
    ):
        parser.error('--min-priority не может быть больше --max-priority')

    normalized_status = None
    if args.status is not None:
        try:
            normalized_status = TaskStatus.normalize(args.status)
        except TaskStatusValidationError as err:
            parser.error(str(err))

    # Сборка источников и запуск обработки
    logger.info('Waiting data...')
    process = ProcessTasks(
        [
            MockExternalSource(),
            TaskJsonSource(args.file),
        ]
    )
    process.add_source(
        RandomJobsSource(Random(args.seed)),
    )

    queue = process.build_queue()
    filtered_queue = queue

    if normalized_status is not None:
        filtered_queue = filtered_queue.filter_by_status(normalized_status)

    if args.min_priority is not None or args.max_priority is not None:
        filtered_queue = filtered_queue.filter_by_priority(
            min_priority=args.min_priority,
            max_priority=args.max_priority,
        )

    logger.info('Streaming tasks from the selected queue')
    process.execute(filtered_queue)


if __name__ == '__main__':
    main()
