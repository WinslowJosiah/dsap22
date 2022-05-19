from typing import Any, Generator, Iterable, Mapping, Optional


class Trie:
    def __init__(
        self,
        obj: Optional[Mapping[str, Any] | Iterable[tuple[str, Any]]] = None,
        **kwargs: Any
    ):
        """
        Create a trie (prefix tree).

        Parameters
        ----------
        obj : mapping or iterable of tuple of (str, any), optional
            Mapping, or iterable of key-value pairs, to populate the
            trie with.
        **kwargs
            These parameters will be used to populate the trie.
        """
        self.clear()
        self.update(obj, **kwargs)

    def __len__(self) -> int:
        self._sort_edges()
        self_length = 1 if self.is_word else 0
        return self_length + sum(len(e) for e in self.edges.values())

    def __iter__(self) -> Generator[str, None, None]:
        self._sort_edges()

        if self.is_word:
            yield ""

        for prefix, node in self.edges.items():
            for word in node:
                yield prefix + word

    def iterpairs(self) -> Generator[tuple[str, Any], None, None]:
        """
        Yield each word-data pair in the trie in sorted order by word.

        This function yields each pair as a tuple in the form `(word,
        data)`. To iterate through each word instead, it is sufficient
        to use the `for`..`in` syntax.

        Yields
        ------
        tuple of (str, any)
            Current word-data pair in the trie.
        """
        self._sort_edges()

        if self.is_word:
            yield ("", self.data)

        for prefix, node in self.edges.items():
            for word, data in node.iterpairs():
                yield (prefix + word, data)

    def __reversed__(self) -> Generator[str, None, None]:
        self._sort_edges()

        for prefix, node in reversed(self.edges.items()):
            for word in reversed(node):
                yield prefix + word

        if self.is_word:
            yield ""

    def reversedpairs(self) -> Generator[tuple[str, Any], None, None]:
        """
        Yield each word-data pair in the trie in reverse sorted order by
        word.

        This function yields each pair as a tuple in the form `(word,
        data)`. To iterate through each word instead, it is sufficient
        to use the `for`..`in reversed(`..`)` syntax.

        Yields
        ------
        tuple of (str, any)
            Current word-data pair in the trie.
        """
        self._sort_edges()

        for prefix, node in reversed(self.edges.items()):
            for word, data in node.reversedpairs():
                yield (prefix + word, data)

        if self.is_word:
            yield ("", self.data)

    def __getitem__(self, key: str) -> Any:
        node = self._walk_prefix(key)
        if node.is_word:
            return node.data

        raise KeyError(repr(key))

    def __setitem__(self, key: str, val: Any):
        node = self._walk_prefix(key, populate=True)
        node.data = val
        node.is_word = True

    def __delitem__(self, key: str):
        def delitem_helper(node: Trie, k: str) -> bool:
            if not k:
                if not node.is_word:
                    raise KeyError(repr(key))
                node.clear()
                return True

            if k[0] not in node.edges:
                raise KeyError(repr(key))

            if delitem_helper(node.edges[k[0]], k[1:]):
                del node.edges[k[0]]

            return not node.edges

        delitem_helper(self, key)

    def __contains__(self, key: str) -> bool:
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True

    def __str__(self) -> str:
        def str_helper(node: Trie, word: str = "", level: int = 0) -> str:
            line = f"{word!r}: {repr(node.data) if node.is_word else '...'}"
            if node.edges:
                line += "\n"

            return line + "\n".join([
                str_helper(new_node, word + c, level + 1)
                for c, new_node in node.edges.items()
            ])

        return str_helper(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({[p for p in self.iterpairs()]})"

    def update(
        self,
        obj: Optional[Mapping[str, Any] | Iterable[tuple[str, Any]]] = None,
        **kwargs: Any
    ):
        """
        Update the trie with the word-data pairs from `obj`, overwriting
        existing words.

        Parameters
        ----------
        obj : mapping or iterable of tuple of (str, any), optional
            Mapping, or iterable of word-data pairs, to populate the
            trie with.
        **kwargs
            These parameters will be used to populate the trie.
        """
        if obj is not None:
            v: Any  # Make the type checker happy

            # If object is a mapping
            if isinstance(obj, Mapping):
                # Loop over its items with items()
                for k, v in obj.items():
                    # The type checker still isn't happy
                    assert isinstance(k, str)
                    self[k] = v
            else:
                # Loop over its items directly
                for k, v in obj:
                    self[k] = v

        if kwargs is not None:
            # Loop over the items of kwargs
            for k, v in kwargs.items():
                self[k] = v

    def prune(self, prefix: str):
        """
        Remove all nodes starting with `prefix` from the trie.

        To remove only a single word from the trie (if it exists),
        use the `del` syntax.

        Parameters
        ----------
        prefix : str
            Prefix of nodes to remove.
        """
        def prune_helper(node: Trie, p: str) -> bool:
            if not p:
                node.clear()
                return True

            if p[0] not in node.edges:
                raise ValueError(f"{prefix!r} not found as prefix in trie")

            if prune_helper(node.edges[p[0]], p[1:]):
                del node.edges[p[0]]

            return not node.edges

        prune_helper(self, prefix)

    def query(self, prefix: str) -> Generator[str, None, None]:
        """
        Search the trie for all words starting with `prefix`.

        Parameters
        ----------
        prefix : str
            Prefix of words to consider.

        Yields
        ------
        str
            Current word.

        See Also
        --------
        querypairs : Search for all words starting with `prefix`, and yield
            word-data pairs.
        """
        try:
            node = self._walk_prefix(prefix)
            for word in node:
                yield prefix + word
        except KeyError:
            return

    def querypairs(
        self,
        prefix: str
    ) -> Generator[tuple[str, Any], None, None]:
        """
        Search the trie for all words starting with `prefix`, and yield
        word-data pairs.

        Parameters
        ----------
        prefix : str
            Prefix of words to consider.

        Yields
        ------
        tuple of (str, any)
            Current word-data pair.

        See Also
        --------
        querypairs : Search for all words starting with `prefix`, and yield
            word-data pairs.
        """
        try:
            node = self._walk_prefix(prefix)
            for word, data in node.iterpairs():
                yield (prefix + word, data)
        except KeyError:
            return

    def clear(self):
        """
        Remove all values from the trie.
        """
        self.data: Optional[Any] = None
        self.is_word: bool = False
        self.edges: dict[str, Trie] = {}
        self.is_sorted: bool = True

    def __bool__(self) -> bool:
        for _ in self:
            return True
        return False

    # Private methods

    def _walk_prefix(self, prefix: str, populate: bool = False) -> "Trie":
        """
        Walk from this node to a node representing words that start with
        `prefix`.

        Parameters
        ----------
        prefix : str
            Prefix of words to consider.
        populate : bool, default False
            If true, add an empty node to nonexistent edges. If false,
            raise a KeyError for nonexistent edges.

        Returns
        -------
        Trie
            Node representing words that start with `prefix`.
        """
        node = self
        for c in prefix:
            if c not in node.edges:
                if not populate:
                    raise KeyError(repr(prefix))
                node.edges[c] = self.__class__()
                node.is_sorted = False
            node = node.edges[c]
        return node

    def _sort_edges(self):
        """
        Sort this node's edges, if `self.is_sorted` is false.
        """
        if not self.is_sorted:
            self.edges = dict(sorted(self.edges.items()))
            self.is_sorted = True
