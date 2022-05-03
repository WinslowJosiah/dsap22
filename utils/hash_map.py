import sys
from typing import (Any, Generator, Hashable, Iterable, Mapping,
    MutableMapping, NamedTuple, Optional)


class HashElement(NamedTuple):
    hash: int
    key: Hashable
    value: Any


class HashMap(MutableMapping[Hashable, Any]):
    MAX_LOAD = 0.75
    MIN_LOAD = MAX_LOAD / 4
    MIN_SIZE = 8
    PERTURB_SHIFT = 5

    def __init__(
        self,
        # I would like "Mapping[Hashable, Any]", but somehow this doesn't
        # allow for initializing this with regular old dicts
        obj: Optional[
            Mapping[Any, Any] | Iterable[tuple[Hashable, Any]]
        ] = None,
        **kwargs: Any
    ):
        """
        Create a hash map.

        Parameters
        ----------
        obj : mapping or iterable of tuple of (any, any), optional
            Mapping, or iterable of key-value pairs, to populate the
            hashmap with.
        **kwargs
            These parameters will be used to populate the hashmap.
        """
        self.clear()
        self.update(obj, **kwargs)

    def __len__(self):
        return self._used

    def __iter__(self) -> Generator[Hashable, None, None]:
        for entry in self._entries:
            if entry is None:
                continue
            yield entry.key

    def __reversed__(self) -> Generator[Hashable, None, None]:
        for entry in reversed(self._entries):
            if entry is None:
                continue
            yield entry.key

    def __getitem__(self, key: Hashable) -> Any:
        key_hash = hash(key)
        for i in self._probe(key_hash):
            index = self._indices[i]
            # If index is unoccupied
            if index is None:
                # There is no item here
                raise KeyError(repr(key))

            entry = self._entries[index]
            # If entry is occupied
            if entry is not None:
                # If entry's key/hash is equal to the new key/hash
                if entry.hash == key_hash and entry.key == key:
                    # Return this entry's value
                    return entry.value

    def __setitem__(self, key: Hashable, val: Any):
        key_hash = hash(key)
        element = HashElement(key_hash, key, val)
        for i in self._probe(key_hash):
            index = self._indices[i]
            # If index is unoccupied
            if index is None:
                # Store new element and index into entries and indices lists
                self._indices[i] = len(self._entries)
                self._entries.append(element)
                # One more entry is used; one more entry is filled
                self._used += 1
                self._fill += 1
                # Stop probing
                break

            entry = self._entries[index]
            # If entry is occupied
            if entry is not None:
                # If entry's key/hash is equal to the new key/hash
                if entry.hash == key_hash and entry.key == key:
                    # Replace this entry with the new element
                    self._entries[index] = element
                    # Stop probing
                    break

        # If load factor of filled elements is not above maximum, return
        if self._fill / self._size <= self.MAX_LOAD:
            return

        # Double size, if necessary
        if self._used / self._size > self.MAX_LOAD:
            self._size *= 2
        self._resize()

    def __delitem__(self, key: Hashable):
        key_hash = hash(key)
        for i in self._probe(key_hash):
            index = self._indices[i]
            # If index is unoccupied
            if index is None:
                # There is no item here
                raise KeyError(repr(key))

            entry = self._entries[index]
            # If entry is occupied
            if entry is not None:
                # If entry's key/hash is equal to the new key/hash
                if entry.hash == key_hash and entry.key == key:
                    # Set this entry to None, effectively deleting it
                    self._entries[index] = None
                    # One less entry is used
                    self._used -= 1
                    # Stop probing
                    break

        # If load factor of used elements is not below minimum, return
        if self._used / self._size >= self.MIN_LOAD:
            return

        # Halve size, if possible
        if self._size > self.MIN_SIZE:
            self._size //= 2
        self._resize()

    def __contains__(self, key: Hashable) -> bool:
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True

    def __str__(self) -> str:
        return str(dict(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({dict(self)!r})"

    def get(self, key: Hashable, default: Any = None):
        """
        Return the value for `key` if `key` is in the hash map, else
        `default`.

        Parameters
        ----------
        key
            Key in the hash map.
        default, optional
            Default value to return if `key` is not in the hash map.

        Returns
        -------
        any
            Value for `key` if `key` is in the hash map, else `default`.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, key: Hashable, default: Any = None):
        """
        If `key` is in the hash map, return its value. If not, insert
        `key` with a value of `default` and return `default`.

        Parameters
        ----------
        key
            Key in the hash map.
        default, optional
            Default value to return and set if `key` is not in the hash
            map.

        Returns
        -------
        any
            Value for `key` if `key` is in the hash map, else `default`.
        """
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def update(
        self,
        obj: Optional[
            Mapping[Hashable, Any] | Iterable[tuple[Hashable, Any]]
        ] = None,
        **kwargs: Any
    ):
        """
        Update the hash map with the key-value pairs from `obj`,
        overwriting existing keys.

        Parameters
        ----------
        obj : mapping or iterable of tuple of (any, any), optional
            Mapping, or iterable of key-value pairs, to populate the
            hashmap with.
        **kwargs
            These parameters will be used to populate the hashmap.
        """
        if obj is not None:
            v: Any  # Make the type checker happy

            # If object is a mapping
            if isinstance(obj, Mapping):
                # Loop over its items with items()
                for k, v in obj.items():
                    self[k] = v
            # If object is an iterable of key-value pairs
            else:
                # Loop over its items directly
                for k, v in obj:
                    self[k] = v

        if kwargs is not None:
            # Loop over the items of kwargs
            for k, v in kwargs.items():
                self[k] = v

    # Empty object that is not the same as any other object
    __marker = object()

    def pop(self, key: Hashable, default: Any = __marker) -> Any:
        """
        If `key` is in the hash map, remove it and return its value,
        else return `default` if given.

        Parameters
        ----------
        key
            Key in the hash map.
        default, optional
            Default value to return if `key` is not in the hash map.

        Returns
        -------
        any
            Value which was popped.
        """
        marker = self.__marker

        try:
            val: Any = self[key]
        # If key does not exist
        except KeyError as e:
            # If default was not provided
            if default is marker:
                # Raise the KeyError
                raise e
            # If default was provided, return it
            return default
        # If key does exist
        else:
            # Delete it and return the value
            del self[key]
            return val

    def popitem(self) -> tuple[Hashable, Any]:
        """
        Remove and return a key-value pair from the hash map. Pairs are
        returned in LIFO order.

        Returns
        -------
        tuple of (any, any)
            Key-value pair which was popped.
        """
        # This for loop does not iterate more than once!
        # It's the least complicated way I can think of to get the last key
        for k in reversed(self):
            v: Any = self[k]
            del self[k]
            return (k, v)

        # If we did not enter the loop, the hash map is empty
        raise KeyError("hash map is empty")

    def copy(self) -> "HashMap":
        """
        Return a shallow copy of the hash map.

        Returns
        -------
        HashMap
            Shallow copy of the hash map.
        """
        return self.__class__(self)

    def clear(self):
        """
        Remove all items from the hash map.
        """
        # Number of index slots used to store values
        self._used: int = 0
        # Number of index slots that ever stored values
        self._fill: int = 0
        # Number of index slots
        self._size: int = self.MIN_SIZE

        # Slots in which to store indices of key-value pairs
        self._indices: list[Optional[int]] = [None for _ in range(self._size)]
        # List of key-value pairs
        self._entries: list[Optional[HashElement]] = []

    @classmethod
    def fromkeys(
        cls,
        iterable: Iterable[Hashable],
        val: Any = None
    ) -> "HashMap":
        """
        Create a new hash map with keys from `iterable` and values set
        to `val`.

        Parameters
        ----------
        iterable : iterable
            Iterable to populate the hash map's keys with.
        val, default None
            Value for each key in the hash map.

        Returns
        -------
        HashMap
            Hash map with keys from `iterable` and values set to `val`.
        """
        result = cls()
        for k in iterable:
            result[k] = val
        return result

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False

        if len(self) != len(other):
            return False

        for k, v in self.items():
            try:
                other_v = other[k]
            except KeyError:
                return False

            if v != other_v:
                return False

        return True

    def __or__(self, other: Mapping[Hashable, Any]) -> "HashMap":
        result = self.copy()
        result.update(other)
        return result

    def __ror__(self, other: Mapping[Hashable, Any]) -> "HashMap":
        result = self.copy()
        result.update(self)
        return result

    def __ior__(self, other: Mapping[Hashable, Any]) -> "HashMap":
        self.update(other)
        return self

    def __bool__(self) -> bool:
        return bool(len(self))

    # Private methods

    def _resize(self):
        """
        Resize the hash map by rebuilding its list of indices.
        """
        # Rebuild the list of indices with the desired size
        self._indices = [None for _ in range(self._size)]
        # Remove all deleted elements of the list of entries
        self._entries = list(filter(None, self._entries))
        # There are no entries filling the list that aren't used
        self._fill = self._used
        # Store the indices for each entry
        for i, entry in enumerate(self._entries):
            assert entry is not None
            for j in self._probe(entry.hash):
                if self._indices[j] is None:
                    self._indices[j] = i
                    break

    def _probe(self, key_hash: int) -> Generator[int, Any, Any]:
        """
        Generate a sequence of indices to try storing an entry with key
        hash `key_hash` into.

        Parameters
        ----------
        key_hash : int
            Hash of the key to store.

        Yields
        ------
        int
            Index to attempt to store the entry into.
        """
        # Calculate initial index
        i: int = key_hash % self._size
        # Create (unsigned) perturbation value
        perturb: int = key_hash
        if perturb < 0:
            perturb += sys.maxsize

        # This loop will not end on its own; the caller must break out of it
        while True:
            yield i
            # Calculate new index
            i = (5 * i + 1 + perturb) % self._size
            # Shift bits of perturbation
            perturb >>= self.PERTURB_SHIFT
