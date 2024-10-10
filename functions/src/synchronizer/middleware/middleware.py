# type alias for a "Middleware" which is a List[Event] -> List[Event] callable


from typing import List, TypeAlias, Callable

from src.shared.event import Event

Middleware: TypeAlias = Callable[[List[Event]], List[Event]]
