from domain.non_data import DemoTask, NonDataStatusLabel
from domain.task_status import TaskStatus


def test_instance_access_returns_label_text_from_status_value() -> None:
    task = DemoTask(TaskStatus.IN_PROGRESS)

    assert task.label == 'Status: in_progress'


def test_class_access_returns_descriptor_object_itself() -> None:
    assert DemoTask.label is DemoTask.__dict__['label']
    assert isinstance(DemoTask.label, NonDataStatusLabel)


def test_instance_assignment_shadows_non_data_descriptor() -> None:
    task = DemoTask(TaskStatus.NEW)

    task.label = 'manual override'

    assert task.label == 'manual override'
    assert task.__dict__['label'] == 'manual override'


def test_shadowing_on_one_instance_does_not_affect_another() -> None:
    overridden_task = DemoTask(TaskStatus.NEW)
    untouched_task = DemoTask(TaskStatus.DONE)

    overridden_task.label = 'manual override'

    assert overridden_task.label == 'manual override'
    assert untouched_task.label == 'Status: done'
