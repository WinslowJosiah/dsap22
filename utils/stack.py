from typing import Any, Callable, Iterable, Optional
from .linked_list import SingleLinkedList


class Stack:
    def __init__(
        self,
        iterable: Optional[Iterable[Any]] = None
    ) -> None:
        """
        Create a stack.

        Parameters
        ----------
        iterable : iterable, optional
            Iterable to populate the stack with. The first element will
            be on the top, and the last element will be on the bottom.
        """
        self.stack: SingleLinkedList = SingleLinkedList(iterable)
        self.size: int = len(self.stack)

    def __len__(self) -> int:
        return self.size

    def __iter__(self):
        for val in self.stack:
            yield val

    def __getitem__(self, pos: int) -> Any:
        if pos >= 0:
            if pos >= len(self):
                raise IndexError("stack index out of range")

            return self.stack[pos]
        else:
            if abs(pos) > len(self):
                raise IndexError("stack index out of range")

            return self.stack[len(self) + pos]

    def __setitem__(self, pos: int, val: Any) -> None:
        if pos >= 0:
            if pos >= len(self):
                raise IndexError("stack assignment index out of range")

            self.stack[pos] = val
        else:
            if abs(pos) > len(self):
                raise IndexError("stack assignment index out of range")

            self.stack[len(self) + pos] = val

    def __str__(self) -> str:
        res = ", ".join(str(v) for v in self.stack)
        return f"[{res}]"

    def __repr__(self) -> str:
        items: list[Any] = [v for v in self.stack]

        if len(items) > 0:
            return f"{self.__class__.__name__}({items!r})"
        else:
            return f"{self.__class__.__name__}()"

    def clear(self) -> None:
        """
        Remove all elements of the stack.
        """
        self.stack.clear()
        self.size = 0

    def push(self, val: Any) -> None:
        """
        Push a value onto the top of the stack.

        Parameters
        ----------
        val
            Value to push.
        """
        self.stack.prepend(val)
        self.size += 1

    def pop(self) -> Any:
        """
        Pop a value from the top of the stack and remove it.

        Returns
        -------
        any
            Value which was popped.
        """
        if len(self) == 0:
            raise IndexError("pop from empty stack")

        val = self.stack.pop_front()
        self.size -= 1
        return val

    def peek(self) -> Any:
        """
        Peek at the top value of the stack without popping or removing
        it.

        Returns
        -------
        any
            Top value of the stack.
        """
        if len(self) == 0:
            raise IndexError("peek in empty stack")

        return self.stack[0]

    def do_operation(
        self,
        func: Callable[..., Iterable[Any] | Any],
        arity: int = 1
    ) -> None:
        """
        Call a function which takes the stack values as arguments, and
        push the result(s).

        Parameters
        ----------
        func : Callable
            Function to call. This should return one or more values to
            push onto the stack.
        arity : int, default 1
            Number of arguments to pass to `func`. These are popped from
            the stack.
        """
        func_args: list[Any] = []
        result: Iterable[Any] | Any = None
        try:
            for _ in range(arity):
                func_args.insert(0, self.pop())

            result = func(*func_args)
        # In case popping args / calculating result fails
        except Exception as e:
            for arg in func_args:
                self.push(arg)
            raise e

        try:
            iter(result)
        # If result is not iterable
        except TypeError:
            self.push(result)
        # If result is iterable
        else:
            for val in result:
                self.push(val)

    def __bool__(self) -> bool:
        return bool(self.stack)
