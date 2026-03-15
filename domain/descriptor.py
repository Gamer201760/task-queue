from domain.error import IntValidationError, StringValidationError


class String:
    def __init__(self, min_len: int = 1, max_len: int | None = None) -> None:
        if not isinstance(min_len, int):
            raise TypeError('min_len должно быть целым числом')
        if max_len is not None and not isinstance(max_len, int):
            raise TypeError('max_len должно быть целым числом или None')
        if max_len is not None and min_len > max_len:
            raise ValueError(
                f'min_len ({min_len}) не может превышать max_len ({max_len})'
            )
        self._min_len = min_len
        self._max_len = max_len

    def __set_name__(self, owner: type, name: str) -> None:
        self._attr = '_' + name

    def __get__(self, obj: object | None, objtype: type | None = None) -> object:
        if obj is None:
            return self
        try:
            return getattr(obj, self._attr)
        except AttributeError:
            raise AttributeError(
                f'атрибут {self._attr[1:]!r} ещё не инициализирован'
            ) from None  # from None нужен, чтобы прервать цепочку ошибок, мы скрываем их от пользователя

    def __set__(self, obj: object, value: object) -> None:
        if not isinstance(value, str):
            raise StringValidationError(f'{self._attr[1:]} должно быть строкой')

        if self._max_len is not None and len(value) > self._max_len:
            raise StringValidationError(
                f'{self._attr[1:]} не должно превышать {self._max_len} символов'
            )

        if len(value) < self._min_len:
            raise StringValidationError(
                f'{self._attr[1:]} должно быть не менее {self._min_len} символов'
            )

        setattr(obj, self._attr, value)


class Int:
    def __init__(self, min_value: int = 1, max_value: int | None = None) -> None:
        if not isinstance(min_value, int):
            raise TypeError('min_value должно быть целым числом')
        if max_value is not None and not isinstance(max_value, int):
            raise TypeError('max_value должно быть целым числом или None')
        if max_value is not None and min_value > max_value:
            raise ValueError(
                f'min_value ({min_value}) не может превышать max_value ({max_value})'
            )
        self._min = min_value
        self._max = max_value

    def __set_name__(self, owner: type, name: str) -> None:
        self._attr = '_' + name

    def __get__(self, obj: object | None, objtype: type | None = None) -> object:
        if obj is None:
            return self
        try:
            return getattr(obj, self._attr)
        except AttributeError:
            raise AttributeError(
                f'атрибут {self._attr[1:]!r} ещё не инициализирован'
            ) from None  # from None нужен, чтобы прервать цепочку ошибок мы скрываем их от пользователя

    def __set__(self, obj: object, value: object) -> None:
        if not isinstance(value, int):
            raise IntValidationError(f'{self._attr[1:]} должно быть целым числом (int)')

        if self._max is not None and value > self._max:
            raise IntValidationError(
                f'{self._attr[1:]} не должно превышать {self._max}'
            )

        if value < self._min:
            raise IntValidationError(
                f'{self._attr[1:]} должно быть не менее {self._min}'
            )

        setattr(obj, self._attr, value)
