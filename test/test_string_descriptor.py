import pytest

from domain.descriptor import String
from domain.error import StringValidationError


class DummyModel:
    name = String(min_len=2, max_len=10)


class UnlimitedLengthModel:
    description = String(min_len=2, max_len=None)


class DefaultMinLengthModel:
    code = String()


class MultiFieldModel:
    title = String(min_len=2, max_len=5)
    note = String(min_len=3, max_len=12)


def test_setting_valid_string_stores_value_and_returns_it() -> None:
    model = DummyModel()

    model.name = 'valid'

    assert model.name == 'valid'
    assert model._name == 'valid'


@pytest.mark.parametrize('value', [123, None, ['a', 'b']])
def test_setting_non_string_value_raises_string_validation_error(value: object) -> None:
    model = DummyModel()

    with pytest.raises(StringValidationError):
        model.name = value


def test_setting_string_shorter_than_min_len_raises_string_validation_error() -> None:
    model = DummyModel()

    with pytest.raises(StringValidationError):
        model.name = 'a'


def test_setting_whitespace_only_string_raises_string_validation_error() -> None:
    model = DummyModel()

    with pytest.raises(StringValidationError):
        model.name = '   '


def test_setting_string_longer_than_max_len_raises_string_validation_error() -> None:
    model = DummyModel()

    with pytest.raises(StringValidationError):
        model.name = 'a' * 11


def test_setting_string_exactly_at_min_len_boundary_succeeds() -> None:
    model = DummyModel()

    model.name = 'ab'

    assert model.name == 'ab'


def test_setting_string_exactly_at_max_len_boundary_succeeds() -> None:
    model = DummyModel()

    model.name = 'abcdefghij'

    assert model.name == 'abcdefghij'


def test_max_len_none_does_not_enforce_upper_bound() -> None:
    model = UnlimitedLengthModel()

    model.description = 'a' * 100

    assert model.description == 'a' * 100


def test_accessing_descriptor_on_class_returns_descriptor_instance() -> None:
    assert DummyModel.name is DummyModel.__dict__['name']
    assert isinstance(DummyModel.name, String)


def test_default_min_len_rejects_empty_string_and_accepts_single_character() -> None:
    model = DefaultMinLengthModel()

    with pytest.raises(StringValidationError):
        model.code = ''

    model.code = 'x'

    assert model.code == 'x'


def test_multiple_descriptor_fields_work_independently() -> None:
    model = MultiFieldModel()

    model.title = 'Task'
    model.note = 'Detailed'

    assert model.title == 'Task'
    assert model.note == 'Detailed'
    assert model._title == 'Task'
    assert model._note == 'Detailed'


def test_string_init_with_non_int_min_len_raises_type_error() -> None:
    string_descriptor = getattr(
        __import__('domain.descriptor', fromlist=['String']), 'String'
    )

    with pytest.raises(TypeError):
        string_descriptor(min_len='1')


def test_string_init_with_non_int_max_len_raises_type_error() -> None:
    string_descriptor = getattr(
        __import__('domain.descriptor', fromlist=['String']), 'String'
    )

    with pytest.raises(TypeError):
        string_descriptor(min_len=1, max_len='10')


def test_string_init_with_min_len_greater_than_max_len_raises_value_error() -> None:
    with pytest.raises(ValueError):
        String(min_len=5, max_len=3)


def test_string_init_with_valid_params_succeeds() -> None:
    descriptor = String(min_len=2, max_len=4)

    assert descriptor._min_len == 2
    assert descriptor._max_len == 4


def test_string_init_with_none_max_len_succeeds() -> None:
    descriptor = String(min_len=2, max_len=None)

    assert descriptor._min_len == 2
    assert descriptor._max_len is None


def test_accessing_uninitialized_string_descriptor_from_instance_raises_attribute_error() -> (
    None
):
    model = DummyModel()

    with pytest.raises(AttributeError):
        _ = model.name


def test_uninitialized_string_descriptor_error_mentions_public_field_name() -> None:
    model = DummyModel()

    with pytest.raises(AttributeError, match=r'\bname\b'):
        _ = model.name


def test_uninitialized_string_descriptor_error_does_not_expose_backing_private_name() -> (
    None
):
    model = DummyModel()

    with pytest.raises(AttributeError, match=r'^(?!.*_name).*name.*$'):
        _ = model.name
