import argparse
from logging import INFO, basicConfig, getLogger
from random import Random

from repository.api.mock import MockExternalSource
from repository.file.json import TaskJsonSource
from repository.generator.rand import RandomJobsSource
from usecase.process import ProcessTasks

basicConfig(format='[%(levelname)s] %(name)s %(asctime)s %(message)s', level=INFO)
logger = getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--file', default='./tasks.json', help='Путь до файла с задачами'
    )
    parser.add_argument(
        '--seed', type=int, default=1, help='Seed для генератора случайных задач'
    )
    args = parser.parse_args()

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
    process.execute()


if __name__ == '__main__':
    main()
