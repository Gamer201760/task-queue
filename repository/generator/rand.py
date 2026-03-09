from random import Random

from domain.task import Task


class RandomJobsSource:
    def __init__(self, rnd: Random) -> None:
        self._rnd = rnd

    # Количество задач и данные определяются генератором
    def get_tasks(self) -> list[Task]:
        return [
            Task(
                id=self._rnd.randint(10, 100000),
                payload={
                    'temperature': self._rnd.randint(-50, 100),
                    'humidity': self._rnd.randint(0, 100),
                },
            )
            for _ in range(self._rnd.randint(10, 30))
        ]
