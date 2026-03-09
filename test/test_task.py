import pytest

from domain.task import Task


def test_task_constructor() -> None:
    task = Task(id=10, payload={'key': 'value'})

    assert task.id == 10
    assert task.payload == {'key': 'value'}


def test_from_json_valid() -> None:
    data = {'id': 5, 'payload': {'x': 1}}

    task = Task.from_json(data)

    assert task == Task(id=5, payload={'x': 1})


def test_from_json_missing_id() -> None:
    data = {'payload': {'x': 1}}

    with pytest.raises(ValueError):
        Task.from_json(data)


def test_from_json_missing_payload() -> None:
    data = {'id': 1}

    with pytest.raises(ValueError):
        Task.from_json(data)


def test_from_json_non_dict() -> None:
    with pytest.raises(TypeError):
        Task.from_json([1, 2, 3])


def test_from_json_invalid_id_type() -> None:
    data = {'id': '1', 'payload': {'x': 1}}

    with pytest.raises(TypeError):
        Task.from_json(data)


def test_from_json_invalid_payload_type() -> None:
    data = {'id': 1, 'payload': ['x']}

    with pytest.raises(TypeError):
        Task.from_json(data)
