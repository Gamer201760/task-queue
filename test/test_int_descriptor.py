import pytest

from domain.descriptor import Int
from domain.error import IntValidationError


class DummyIntModel:
    priority = Int(min_value=2, max_value=10)


class UnlimitedMaxModel:
    count = Int(min_value=3, max_value=None)


class DefaultMinModel:
    identifier = Int()


class MultiFieldIntModel:
    retries = Int(min_value=1, max_value=5)
    timeout = Int(min_value=10, max_value=60)


class UnsetIntModel:
    age = Int(min_value=1, max_value=120)


def test_valid_assignment_stores_value_and_returns_it() -> None:
    model = DummyIntModel()

    model.priority = 7

    assert model.priority == 7
    assert model._priority == 7


def test_class_access_returns_descriptor_instance() -> None:
    assert DummyIntModel.priority is DummyIntModel.__dict__['priority']
    assert isinstance(DummyIntModel.priority, Int)


@pytest.mark.parametrize('value', ['1', None, 1.5, [1]])
def test_non_int_values_raise_int_validation_error(value: object) -> None:
    model = DummyIntModel()

    with pytest.raises(IntValidationError):
        model.priority = value


def test_value_below_min_raises_int_validation_error() -> None:
    model = DummyIntModel()

    with pytest.raises(IntValidationError):
        model.priority = 1


def test_value_above_max_raises_int_validation_error() -> None:
    model = DummyIntModel()

    with pytest.raises(IntValidationError):
        model.priority = 11


def test_exactly_min_value_succeeds() -> None:
    model = DummyIntModel()

    model.priority = 2

    assert model.priority == 2


def test_exactly_max_value_succeeds() -> None:
    model = DummyIntModel()

    model.priority = 10

    assert model.priority == 10


def test_max_value_none_allows_large_values() -> None:
    model = UnlimitedMaxModel()

    model.count = 10**9

    assert model.count == 10**9


def test_default_min_value_rejects_zero_and_accepts_one() -> None:
    model = DefaultMinModel()

    with pytest.raises(IntValidationError):
        model.identifier = 0

    model.identifier = 1

    assert model.identifier == 1


def test_multiple_descriptor_backed_int_fields_work_independently() -> None:
    model = MultiFieldIntModel()

    model.retries = 3
    model.timeout = 45

    assert model.retries == 3
    assert model.timeout == 45
    assert model._retries == 3
    assert model._timeout == 45


def test_init_with_non_int_min_value_raises_type_error() -> None:
    with pytest.raises(TypeError):
        Int(min_value='1')


def test_init_with_non_int_max_value_raises_type_error() -> None:
    with pytest.raises(TypeError):
        Int(min_value=1, max_value='10')


def test_init_with_min_value_greater_than_max_value_raises_value_error() -> None:
    with pytest.raises(ValueError):
        Int(min_value=5, max_value=3)


def test_init_with_valid_params_succeeds() -> None:
    descriptor = Int(min_value=2, max_value=4)

    assert descriptor._min == 2
    assert descriptor._max == 4


def test_reading_unset_attribute_raises_attribute_error_with_public_name() -> None:
    model = UnsetIntModel()

    with pytest.raises(AttributeError, match='age'):
        _ = model.age
