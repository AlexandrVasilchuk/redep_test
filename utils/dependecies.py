import inspect
from typing import Any, Callable, Coroutine


class Depends:
    """Класс зависимости.

    Используется для передачи зависимостей в функции при использовании инъекции зависимостей.
    """

    def __init__(self, value: Callable[[], Coroutine[Any, Any, Any]]):
        self.value = value


def inject_db(
    function: Callable[..., Coroutine[Any, Any, Any]]
) -> Callable[..., Coroutine[Any, Any, Any]]:
    """Декоратор для инъекции зависимостей в функцию.

    Args:
        function (Callable[..., Coroutine[Any, Any, Any]]): Функция, в которую необходимо внедрить зависимости.

    Returns:
        Callable[..., Coroutine[Any, Any, Any]]: Обернутая функция с внедренными зависимостями.
    """
    sig = inspect.signature(function)

    async def wrapper(*args, **kwargs):
        """Обертка для функции с инъекцией зависимостей.

        Args:
            *args: Позиционные аргументы функции.
            **kwargs: Именованные аргументы функции.

        Returns:
            Coroutine[Any, Any, Any]: Результат выполнения обернутой функции.
        """
        for param in sig.parameters.values():
            if isinstance(param.default, Depends):
                async for session in param.default.value():
                    kwargs[param.name] = session
                    await function(*args, **kwargs)

    return wrapper
