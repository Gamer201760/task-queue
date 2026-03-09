from dataclasses import dataclass


@dataclass
class Task:
    id: int
    payload: dict

    # Фабрика из сырого JSON объекта с валидацией
    @classmethod
    def from_json(cls, obj: object) -> 'Task':
        if not isinstance(obj, dict):
            raise TypeError(f'Task JSON must be an object, got {type(obj).__name__}')

        if 'id' not in obj:
            raise ValueError("Не найден параметер 'id'")
        if 'payload' not in obj:
            raise ValueError("Не найден параметер 'payload'")

        task_id = obj['id']
        payload = obj['payload']

        if not isinstance(task_id, int):
            raise TypeError(
                f'Task.id должен быть int, получили {type(task_id).__name__}'
            )
        if not isinstance(payload, dict):
            raise TypeError(
                f'Task.payload должен быть dict, получили {type(payload).__name__}'
            )

        return cls(id=task_id, payload=payload)
