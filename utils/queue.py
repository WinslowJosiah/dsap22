from typing import Any, Generator, Iterable, Optional
from .linked_list import DLList


class Queue:
    def __init__(
        self,
        iterable: Optional[Iterable[Any]] = None
    ) -> None:
        """
        Create a queue.

        Parameters
        ----------
        iterable: iterable, optional
            Iterable to populate the queue with.
        """

        self.queue: DLList = DLList(iterable)
        self.size: int = len(self.queue)

    def __len__(self) -> int:
        return self.size

    def __iter__(self) -> Generator[Any, None, None]:
        for val in self.queue:
            yield val

    def __reversed__(self) -> Generator[Any, None, None]:
        for val in reversed(self.queue):
            yield val

    def __getitem__(self, pos: int) -> Any:
        if pos >= 0:
            if pos >= len(self):
                raise IndexError("queue index out of range")

            return self.queue[pos]
        else:
            if abs(pos) > len(self):
                raise IndexError("queue index out of range")

            return self.queue[len(self) + pos]

    def __setitem__(self, pos: int, val: Any) -> None:
        if pos >= 0:
            if pos >= len(self):
                raise IndexError("queue assignment index out of range")

            self.queue[pos] = val
        else:
            if abs(pos) > len(self):
                raise IndexError("queue assignment index out of range")

            self.queue[len(self) + pos] = val

    def __str__(self) -> str:
        res = ", ".join(str(v) for v in self.queue)
        return f"[{res}]"

    def __repr__(self) -> str:
        items: list[Any] = [v for v in self.queue]

        if len(items) > 0:
            return f"{self.__class__.__name__}({items!r})"
        else:
            return f"{self.__class__.__name__}()"

    def clear(self) -> None:
        """
        Remove all elements of the queue.
        """
        self.queue.clear()
        self.size = 0

    def enqueue(self, val: Any) -> None:
        """
        Add a value to the queue at the end.

        Parameters
        ----------
        val
            Value to enqueue.
        """
        self.queue.append(val)
        self.size += 1

    def dequeue(self) -> Any:
        """
        Remove a value from the queue at the start.

        Returns
        -------
        any
            Value that was dequeued.
        """
        if len(self) == 0:
            raise IndexError("dequeue from empty queue")

        val = self.queue.pop_front()
        self.size -= 1
        return val

    def peek(self) -> Any:
        """
        Peek at the starting value of the queue without dequeueing or
        removing it.

        Returns
        -------
        any
            Starting value of the queue.
        """
        if len(self) == 0:
            raise IndexError("peek in empty queue")

        return self.queue[0]

    def __bool__(self) -> bool:
        return bool(self.queue)
