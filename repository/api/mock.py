import time

from domain.task import Task


class MockExternalSource:
    def get_tasks(self) -> list[Task]:
        time.sleep(1)  # задержка, имитация хождения по сети
        return [Task(id=1, payload={'palka': 'copalka'})]
