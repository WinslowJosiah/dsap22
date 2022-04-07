from typing import Any, Optional


class SNode:
    def __init__(self, value: Any = None) -> None:
        """
        Create a node for a singly linked list.

        Parameters
        ----------
        value
            Value of this node.
        """
        self.next: Optional[SNode] = None
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"


class DNode:
    def __init__(self, value: Any = None) -> None:
        """
        Create a node for a doubly linked list.

        Parameters
        ----------
        value
            Value of this node.
        """
        self.next: Optional[DNode] = None
        self.prev: Optional[DNode] = None
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"
