from typing import Any, Callable, Iterable, Optional

from .node import SNode, DNode


class SingleLinkedList:
    def __init__(
        self,
        iterable: Optional[Iterable[Any]] = None,
        mu: Optional[int] = None
    ) -> None:
        """
        Create a singly linked list.
        
        Parameters
        ----------
        iterable : iterable, optional
            Iterable to populate the linked list with.
        mu : int, optional
            Starting index of cycle, which ends at the end of
            `iterable`.
        """
        self.head: Optional[SNode] = None

        if iterable is not None:
            try:
                for val in reversed(iterable): # type: ignore
                    self.prepend(val)
            except TypeError:
                for val in iterable:
                    self.append(val)

            if mu is not None:
                self.insert_cycle(mu)

    def __len__(self) -> int:
        lam, mu = self.find_cycle()
        return lam + mu

    def __iter__(self):
        for p in self.iternodes():
            yield p.value

    def iternodes(self):
        """
        Yield each node in the linked list.

        This function yields each node as an `SNode` object. To iterate
        through each actual value instead, it is sufficient to use the
        `for`..`in` syntax.

        Yields
        ------
        SNode
            Node object within the linked list.
        """
        p = self.head
        for _ in range(len(self)):
            assert p is not None
            yield p
            p = p.next

    def __getitem__(self, pos: int) -> Any:
        # TODO: handle negative index
        if pos < 0:
            raise NotImplementedError(
                "__getitem__ for negative index is unimplemented"
            )

        lam, mu = self.find_cycle()

        # Bring index in iterable range
        if not (lam == 0 or pos < mu):
            pos = (pos - mu) % lam + mu

        if lam == 0 and pos >= mu:
            raise IndexError("linked list index out of range")

        p = self.head
        for _ in range(pos):
            assert p is not None
            p = p.next

        assert p is not None
        return p.value

    def __setitem__(self, pos: int, val: Any) -> None:
        # TODO: handle negative index
        if pos < 0:
            raise NotImplementedError(
                "__setitem__ for negative index is unimplemented"
            )

        lam, mu = self.find_cycle()

        # Bring index in iterable range
        if not (lam == 0 or pos < mu):
            pos = (pos - mu) % lam + mu

        if lam == 0 and pos >= mu:
            raise IndexError(
                "linked list assignment index out of range"
            )

        p = self.head
        for _ in range(pos):
            assert p is not None
            p = p.next

        assert p is not None
        p.value = val

    def __str__(self) -> str:
        if self.head is None:
            return "[]"

        lam, mu = self.find_cycle()

        start: list[Any] = []
        cycle: list[Any] = []
        p = self.head
        for i in range(lam + mu):
            if i < mu:
                start.append(p)
            else:
                cycle.append(p)
            assert p is not None
            p = p.next

        res = " -> ".join(str(p) for p in start)
        if len(cycle) > 0:
            res += f" -> [{' -> '.join(str(p) for p in cycle)} -> ...]"
        return f"[{res}]"

    def __repr__(self) -> str:
        if self.head is None:
            return f"{self.__class__.__name__}()"

        lam, mu = self.find_cycle()

        items: list[Any] = []
        p = self.head
        for _ in range(lam + mu):
            assert p is not None
            items.append(p.value)
            p = p.next

        if lam > 0:
            return f"{self.__class__.__name__}({items!r}, {mu})"
        else:
            return f"{self.__class__.__name__}({items!r})"

    def clear(self) -> None:
        """
        Remove all elements of the linked list.
        """
        self.head = None

    def append(self, val: Any) -> None:
        """
        Append object to the end of the linked list.

        Parameters
        ----------
        val
            Value to append.
        """
        temp = SNode(val)

        if self.head is None:
            self.head = temp
            return

        p = None
        for p in self.iternodes():
            p: Optional[SNode]
            pass
        assert p is not None

        temp.next = p.next
        p.next = temp

    def prepend(self, val: Any) -> None:
        """
        Prepend object to the beginning of the linked list.

        Parameters
        ----------
        val
            Value to prepend.
        """
        temp = SNode(val)
        temp.next = self.head
        self.head = temp

    def insert(self, pos: int, val: Any) -> None:
        """
        Insert object before index.

        Parameters
        ----------
        pos : int
            Index to insert value before.
        val
            Value to insert.
        """
        # TODO: handle negative index
        if pos < 0:
            raise NotImplementedError(
                "insert for negative index is unimplemented"
            )

        if pos == 0:
            self.prepend(val)

        lam, mu = self.find_cycle()

        if lam == 0 and pos >= mu:
            raise IndexError("insert index out of range")

        # Bring index in iterable range
        # (offset by 1)
        if not (lam == 0 or pos < (mu + 1)):
            pos = (pos - (mu + 1)) % lam + (mu + 1)

        temp = SNode(val)
        p = self.head
        for i in range(lam + mu):
            if i + 1 == pos:
                break
            assert p is not None
            p = p.next
        assert p is not None

        temp.next = p.next
        p.next = temp

    def pop_front(self) -> Any:
        """
        Remove item at the beginning of the linked list.

        Returns
        -------
        any
            Value which was removed.
        """
        if self.head is None:
            raise IndexError("pop_front from empty linked list")

        p = None
        for p in self.iternodes():
            p: Optional[SNode]
            pass

        assert p is not None
        if p.next == self.head:
            p.next = self.head.next

        val = self.head.value
        self.head = self.head.next
        return val

    def pop_back(self) -> Any:
        """
        Remove item at the end of the linked list.

        Returns
        -------
        any
            Value which was removed.
        """
        if self.head is None:
            raise IndexError("pop_back from empty linked list")

        if self.head.next is None or self.head.next == self.head:
            val = self.head.value
            self.clear()
            return val

        lam, mu = self.find_cycle()

        p = self.head
        for _ in range(lam + mu - 2):
            assert p is not None
            p = p.next
        assert p is not None
        assert p.next is not None

        val = p.next.value
        p.next = p.next.next
        return val

    def pop(self, pos: Optional[int] = None) -> Any:
        """
        Remove item at index (default last).

        Parameters
        ----------
        pos : int, optional
            Index to remove value at (default last).

        Returns
        -------
        any
            Value which was removed.
        """
        if self.head is None:
            raise IndexError("pop from empty linked list")

        if pos is not None:
            # TODO: handle negative index
            if pos < 0:
                raise NotImplementedError(
                    "pop for negative index is unimplemented"
                )

        lam, mu = self.find_cycle()

        if pos is None:
            pos = lam + mu - 1

        if pos == 0:
            return self.pop_front()

        if lam == 0 and pos >= mu:
            raise IndexError("pop index out of range")

        # Bring index in iterable range
        if not (lam == 0 or pos < mu):
            pos = (pos - mu) % lam + mu

        # Find target (the node before the node to remove)
        p = self.head
        for i in range(lam + mu):
            if i + 1 == pos:
                break
            assert p is not None
            p = p.next
        assert p is not None
        assert p.next is not None

        # If node is first node in cycle
        if pos == mu:
            # Relink last node to node after the one to remove
            last: Optional[SNode] = p
            for _ in range(lam):
                assert last is not None
                last = last.next
            assert last is not None

            last.next = p.next.next

        val = p.next.value
        p.next = p.next.next
        return val

    def index(self, val: Any) -> int:
        """
        Find first index of value.

        Parameters
        ----------
        val
            Value to find.

        Returns
        -------
        int
            First index of value.
        """
        for i, v in enumerate(self):
            if v == val:
                return i

        raise ValueError(f"{val!r} is not in linked list")

    def reverse(self) -> None:
        """
        Reverse the order of the linked list.
        """
        lam, _ = self.find_cycle()
        if lam > 0:
            raise NotImplementedError(
                "reverse for linked list with cycle is unimplemented"
            )

        previous = None
        current = self.head
        while current is not None:
            next = current.next
            current.next = previous
            previous = current
            current = next
        self.head = previous

    def sort_values(
        self,
        key: Optional[Callable[..., Any]] = None,
        reverse: bool = False
    ) -> None:
        """
        Sort the linked list in ascending order.

        The sort works by swapping the values of each item of the
        linked list.

        Parameters
        ----------
        key : Callable, optional
            Function to apply to each item before sorting.
        reverse : bool, default False
            If true, the list is sorted in descending order.
        """
        if self.head is None:
            return

        lam, mu = self.find_cycle()
        if lam > 0:
            raise NotImplementedError(
                "sort_values for linked list with cycle is "
                "unimplemented"
            )

        keys: list[Any] = []
        p = self.head
        for _ in range(lam + mu):
            assert p is not None
            keys.append(key(p.value) if key else p.value)
            p = p.next

        def should_swap(i: int):
            if reverse:
                return keys[i - 1] < keys[i]
            else:
                return keys[i - 1] > keys[i]

        n = lam + mu
        while n > 1:
            new_n = 0
            p = self.head
            for i in range(1, n):
                assert p is not None
                assert p.next is not None

                if should_swap(i):
                    keys[i - 1], keys[i] = keys[i], keys[i - 1]

                    p.value, p.next.value = p.next.value, p.value
                    new_n = i
                p = p.next
            n = new_n

    def sort_items(
        self,
        key: Optional[Callable[..., Any]] = None,
        reverse: bool = False
    ) -> None:
        """
        Sort the linked list in ascending order.

        The sort works by swapping the items of the linked list.

        Parameters
        ----------
        key : Callable, optional
            Function to apply to each item before sorting.
        reverse : bool, default False
            If true, the list is sorted in descending order.
        """
        if self.head is None:
            return

        lam, mu = self.find_cycle()
        if lam > 0:
            raise NotImplementedError(
                "sort_values for linked list with cycle is "
                "unimplemented"
            )

        keys: list[Any] = []
        p = self.head
        for _ in range(lam + mu):
            assert p is not None
            keys.append(key(p.value) if key else p.value)
            p = p.next

        def should_swap(i: int):
            if reverse:
                return keys[i - 1] < keys[i]
            else:
                return keys[i - 1] > keys[i]

        n = lam + mu
        while n > 1:
            new_n = 0
            o = None
            p = self.head
            for i in range(1, n):
                assert p is not None
                assert p.next is not None

                if should_swap(i):
                    keys[i - 1], keys[i] = keys[i], keys[i - 1]

                    q: SNode = p.next
                    p.next = q.next
                    q.next = p
                    if o is None:
                        self.head = q
                    else:
                        o.next = q
                    p, q = q, p

                    new_n = i
                o, p = p, p.next
            n = new_n

    def insert_cycle(self, mu: int) -> None:
        """
        Insert a cycle in the linked list.

        Parameters
        ----------
        mu : int
            Starting index of the desired cycle, which the final item
            will point to.
        """
        target = None
        p = None
        for i, p in enumerate(self.iternodes()):
            p: Optional[SNode]
            if i == mu:
                target = p

        if target is None:
            raise IndexError("cycle index out of range")
        assert p is not None

        p.next = target

    def find_cycle(self) -> tuple[int, int]:
        """
        Detect a cycle using Floyd's tortoise and hare algorithm.

        Returns
        -------
        lam : int
            Length of the detected cycle. If no cycle is detected,
            `lam` will be 0.
        mu : int
            Starting index of the detected cycle. If no cycle is
            detected, `mu` will be the length of the linked list.
        """
        if self.head is None:
            # Cycle length of 0, starting past the end
            return 0, 0

        tortoise = self.head.next
        if tortoise is None:
            # Cycle length of 0, starting past the end
            return 0, 1
        hare = tortoise.next

        # Initial "race"
        size = 2
        while tortoise != hare:
            assert tortoise is not None
            tortoise = tortoise.next
            for _ in range(2):
                if hare is None:
                    # Cycle length of 0, starting past the end
                    return 0, size
                hare = hare.next
                size += 1

        # Find starting position of cycle
        mu = 0
        tortoise = self.head
        while tortoise != hare:
            assert tortoise is not None and hare is not None
            tortoise = tortoise.next
            hare = hare.next
            mu += 1

        # Find length of cycle
        lam = 1
        assert tortoise is not None
        hare = tortoise.next
        while tortoise != hare:
            assert hare is not None
            hare = hare.next
            lam += 1

        # Cycle length of lam, starting at mu
        return lam, mu

    def remove_cycle(self) -> None:
        """
        Remove a cycle from the linked list.
        """
        if self.head is None:
            return

        p = None
        for p in self.iternodes():
            p: Optional[SNode]
            pass
        assert p is not None

        p.next = None

    def __add__(self, iterable: Iterable[Any]):
        new_list: SingleLinkedList = SingleLinkedList(self)
        for val in iterable:
            new_list.append(val)
        return new_list

    def __iadd__(self, iterable: Iterable[Any]):
        for val in iterable:
            self.append(val)
        return self

    def __mul__(self, count: int):
        if self.head is None or count <= 0:
            return SingleLinkedList()

        new_list: SingleLinkedList = SingleLinkedList(self)
        for _ in range(count - 1):
            new_list += self
        return new_list

    def __imul__(self, count: int):
        if self.head is None:
            return self

        if count <= 0:
            self.clear()
            return self

        n = len(self)
        for _ in range(count - 1):
            p = self.head
            for _ in range(n):
                assert p is not None
                self.append(p.value)
                p = p.next

        return self

    def __bool__(self) -> bool:
        return self.head is not None


class DoubleLinkedList:
    def __init__(
        self,
        iterable: Optional[Iterable[Any]] = None,
        circular: bool = False
    ) -> None:
        """
        Create a doubly linked list.

        Parameters
        ----------
        iterable: iterable, optional
            Iterable to populate the linked list with.
        circular: bool, default False
            True if the list is circular (where the node after the tail
            is the head, and the node before the head is the tail).
        """
        self.head: Optional[DNode] = None
        self.tail: Optional[DNode] = None

        if iterable is not None:
            for val in iterable:
                self.append(val)

            if circular:
                self.insert_cycle()

    def __len__(self) -> int:
        n = 0
        for _ in self:
            n += 1
        return n

    def __iter__(self):
        for p in self.iternodes():
            yield p.value

    def iternodes(self):
        """
        Yield each node in the linked list.

        This function yields each node as a `DNode` object. To iterate
        through each actual value instead, it is sufficient to use the
        `for`..`in` syntax.

        Yields
        ------
        SNode
            Node object within the linked list.
        """
        p = self.head
        while p is not None:
            yield p
            p = p.next
            if p == self.head:
                break

    def __reversed__(self):
        for p in self.reversednodes():
            yield p.value

    def reversednodes(self):
        """
        Yield each node in the linked list in reverse.

        This function yields each node as a `DNode` object. To iterate
        through each actual value instead, it is sufficient to use the
        `for`..`in reversed(`..`)` syntax.

        Yields
        ------
        SNode
            Node object within the linked list.
        """
        p = self.tail
        while p is not None:
            yield p
            p = p.prev
            if p == self.tail:
                break

    def __getitem__(self, pos: int) -> Any:
        if pos >= 0:
            p = self.head
            assert p is not None
            for _ in range(pos):
                p = p.next
                if p is None:
                    raise IndexError("linked list index out of range")
        else:
            p = self.tail
            assert p is not None
            for _ in range(abs(pos) - 1):
                p = p.prev
                if p is None:
                    raise IndexError("linked list index out of range")

        return p.value

    def __setitem__(self, pos: int, val: Any) -> None:
        if pos >= 0:
            p = self.head
            if p is None:
                raise IndexError("linked list index out of range")

            for _ in range(pos):
                p = p.next
                if p is None:
                    raise IndexError("linked list index out of range")
        else:
            p = self.tail
            if p is None:
                raise IndexError("linked list index out of range")

            for _ in range(abs(pos) - 1):
                p = p.prev
                if p is None:
                    raise IndexError("linked list index out of range")

        p.value = val

    def __str__(self) -> str:
        items_str: str = " <-> ".join(str(p) for p in self)

        if self.find_cycle():
            return f"[... {items_str} <-> ...]"
        else:
            return f"[{items_str}]"

    def __repr__(self) -> str:
        items: list[Any] = [p for p in self]

        if self.find_cycle():
            return f"{self.__class__.__name__}({items!r}, True)"
        else:
            return f"{self.__class__.__name__}({items!r})"

    def clear(self) -> None:
        """
        Remove all elements of the linked list.
        """
        self.head = None
        self.tail = None

    def append(self, val: Any) -> None:
        """
        Append object to the end of the linked list.

        Parameters
        ----------
        val
            Value to append.
        """
        if self.head is None or self.tail is None:
            self.prepend(val)
            return

        temp = DNode(val)

        temp.prev = self.tail
        temp.next = self.tail.next
        self.tail.next = temp
        self.tail = temp
        if self.head.prev is not None:
            self.head.prev = self.tail

    def prepend(self, val: Any) -> None:
        """
        Prepend object to the beginning of the linked list.

        Parameters
        ----------
        val
            Value to prepend.
        """
        temp = DNode(val)

        if self.head is None or self.tail is None:
            self.head = temp
            self.tail = temp
            return

        temp.next = self.head
        temp.prev = self.head.prev
        self.head.prev = temp
        self.head = temp
        if self.tail.next is not None:
            self.tail.next = self.head

    def insert(self, pos: int, val: Any) -> None:
        """
        Insert object before index.

        Parameters
        ----------
        pos : int
            Index to insert value before.
        val
            Value to insert.
        """
        temp = DNode(val)

        if pos == 0:
            self.prepend(val)
            return

        assert self.head is not None
        assert self.tail is not None
        if pos >= 0:
            p = self.head
            if p is None and pos > 0:
                raise IndexError("insert index out of range")

            for i in range(pos):
                # If inserting just after end of list
                print(i, pos, p, self.tail)
                if i + 1 == pos and p == self.tail:
                    self.append(val)
                    return

                p = p.next
                if p is None:
                    raise IndexError("insert index out of range")
        else:
            p = self.tail
            if p is None and pos < -1:
                raise IndexError("insert index out of range")

            for i in range(-1, pos, -1):
                p = p.prev
                if p is None:
                    raise IndexError("insert index out of range")

        temp.next = p
        if p.prev is None or p.prev == self.tail:
            temp.prev = p.prev
            self.head = temp
        else:
            temp.prev = p.prev
            p.prev.next = temp
        p.prev = temp

    def pop_front(self) -> Any:
        """
        Remove item at the beginning of the linked list.

        Returns
        -------
        any
            Value which was removed.
        """
        if self.head is None or self.tail is None:
            raise IndexError("pop_front from empty linked list")

        val = self.head.value

        if self.head.next is None:
            self.tail = self.head.prev
        else:
            self.head.next.prev = self.head.prev

        if self.head.prev is None:
            self.head = self.head.next
        else:
            self.head.prev.next = self.head.next

        return val

    def pop_back(self) -> Any:
        """
        Remove item at the end of the linked list.

        Returns
        -------
        any
            Value which was removed.
        """
        if self.head is None or self.tail is None:
            raise IndexError("pop_back from empty linked list")

        val = self.tail.value

        if self.tail.prev is None:
            self.head = self.tail.next
        else:
            self.tail.prev.next = self.tail.next

        if self.tail.next is None:
            self.tail = self.tail.prev
        else:
            self.tail.next.prev = self.tail.prev

        return val

    def pop(self, pos: int = -1) -> Any:
        """
        Remove item at index (default last).

        Parameters
        ----------
        pos : int, default -1
            Index to remove value at (default last).

        Returns
        -------
        any
            Value which was removed.
        """
        if self.head is None or self.tail is None:
            raise IndexError("pop from empty linked list")

        if pos >= 0:
            p = self.head
            assert p is not None
            for _ in range(pos):
                p = p.next
                if p is None:
                    raise IndexError("pop index out of range")
        else:
            p = self.tail
            assert p is not None
            for _ in range(abs(pos) - 1):
                p = p.prev
                if p is None:
                    raise IndexError("pop index out of range")

        val = p.value

        if p.prev is None:
            self.head = p.next
        else:
            p.prev.next = p.next

        if p.next is None:
            self.tail = p.prev
        else:
            p.next.prev = p.prev

        return val

    def index(self, val: Any) -> int:
        """
        Find first index of value.

        Parameters
        ----------
        val
            Value to find.

        Returns
        -------
        int
            First index of value.
        """
        for i, v in enumerate(self):
            if v == val:
                return i

        raise ValueError(f"{val!r} is not in linked list")

    def reverse(self) -> None:
        """
        Reverse the order of the linked list.
        """
        has_cycle = self.find_cycle()
        self.remove_cycle()

        temp: Optional[DNode] = None
        current = self.head
        self.tail = self.head

        while current is not None:
            temp = current.prev
            current.prev = current.next
            current.next = temp
            current = current.prev

        if temp is not None:
            self.head = temp.prev

        if has_cycle:
            self.insert_cycle()

    def sort_values(
        self,
        key: Optional[Callable[..., Any]] = None,
        reverse: bool = False
    ) -> None:
        """
        Sort the linked list in ascending order.

        The sort works by swapping the values of each item of the
        linked list.

        Parameters
        ----------
        key : Callable, optional
            Function to apply to each item before sorting.
        reverse : bool, default False
            If true, the list is sorted in descending order.
        """
        if self.head is None:
            return

        has_cycle = self.find_cycle()
        self.remove_cycle()

        keys: list[Any] = []
        for v in self:
            keys.append(key(v) if key else v)

        def should_swap(i: int):
            if reverse:
                return keys[i - 1] < keys[i]
            else:
                return keys[i - 1] > keys[i]

        n = len(self)
        while n > 1:
            new_n = 0
            p = self.head
            for i in range(1, n):
                assert p is not None
                assert p.next is not None

                if should_swap(i):
                    keys[i - 1], keys[i] = keys[i], keys[i - 1]

                    p.value, p.next.value = p.next.value, p.value
                    new_n = i
                p = p.next
            n = new_n

        if has_cycle:
            self.insert_cycle()

    def sort_items(
        self,
        key: Optional[Callable[..., Any]] = None,
        reverse: bool = False
    ) -> None:
        """
        Sort the linked list in ascending order.

        The sort works by swapping the items of the linked list.

        Parameters
        ----------
        key : Callable, optional
            Function to apply to each item before sorting.
        reverse : bool, default False
            If true, the list is sorted in descending order.
        """
        if self.head is None:
            return

        has_cycle = self.find_cycle()
        self.remove_cycle()

        keys: list[Any] = []
        for v in self:
            keys.append(key(v) if key else v)

        def should_swap(i: int):
            if reverse:
                return keys[i - 1] < keys[i]
            else:
                return keys[i - 1] > keys[i]

        n = len(self)
        while n > 1:
            new_n = 0
            o = None
            p = self.head
            for i in range(1, n):
                assert p is not None
                assert p.next is not None

                if should_swap(i):
                    keys[i - 1], keys[i] = keys[i], keys[i - 1]

                    q: DNode = p.next
                    r = q.next
                    p.next = q.next
                    q.prev = p.prev
                    q.next = p
                    p.prev = q
                    if o is None:
                        self.head = q
                    else:
                        o.next = q
                    if r is None:
                        self.tail = p
                    else:
                        r.prev = p
                    p, q = q, p

                    new_n = i
                o, p = p, p.next
            n = new_n

        if has_cycle:
            self.insert_cycle()

    def insert_cycle(self) -> None:
        """
        Insert a cycle in the linked list.
        """
        if self.head is None or self.tail is None:
            return

        self.head.prev = self.tail
        self.tail.next = self.head

    def find_cycle(self) -> bool:
        """
        Detect a cycle in the linked list.

        Note that, in a doubly linked list, the only valid cycle is one
        where the node after the tail is the head, and the node before
        the head is the tail.

        Returns
        -------
        bool
            True if cycle exists, False otherwise.
        """
        if self.head is None or self.tail is None:
            return False

        loop_at_head = (self.head.prev == self.tail)
        loop_at_tail = (self.tail.next == self.head)

        if loop_at_head != loop_at_tail:
            raise RuntimeError(
                "linked list circular at "
                + ("head" if loop_at_head else "tail")
                + ", but not at "
                + ("tail" if loop_at_tail else "head")
            )

        return loop_at_head

    def remove_cycle(self) -> None:
        """
        Remove a cycle from the linked list.
        """
        if self.head is None or self.tail is None:
            return

        self.head.prev = None
        self.tail.next = None

    def __add__(self, iterable: Iterable[Any]):
        has_cycle = self.find_cycle()
        if isinstance(iterable, self.__class__):
            has_cycle = has_cycle or iterable.find_cycle()

        new_list: DoubleLinkedList = DoubleLinkedList(self, has_cycle)
        for val in iterable:
            new_list.append(val)
        return new_list

    def __iadd__(self, iterable: Iterable[Any]):
        for val in iterable:
            self.append(val)
        return self

    def __mul__(self, count: int):
        if self.head is None or count <= 0:
            return DoubleLinkedList()

        new_list: DoubleLinkedList = DoubleLinkedList(self)
        for _ in range(count - 1):
            new_list += self
        return new_list

    def __imul__(self, count: int):
        if self.head is None:
            return self

        if count <= 0:
            self.clear()
            return self

        n = len(self)
        for _ in range(count - 1):
            p = self.head
            for _ in range(n):
                assert p is not None
                self.append(p.value)
                p = p.next

        return self

    def __bool__(self) -> bool:
        return self.head is not None and self.tail is not None
