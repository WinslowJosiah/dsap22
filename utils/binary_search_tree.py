from typing import Any, Generator, Iterable, Optional


class BSTree:
    class Node:
        def __init__(self,
            value: Any,
            balance: int = 0,
            left: Optional["BSTree.Node"] = None,
            right: Optional["BSTree.Node"] = None,
        ):
            """
            Create a node for a self-balancing binary search tree.

            Parameters
            ----------
            value
                Value of this node.
            balance: int
                Balance factor of this node.
            left: BSTree.Node, optional
                Left child of this node.
            right: BSTree.Node, optional
                Right child of this node.
            """
            self.left: Optional[BSTree.Node] = left
            self.right: Optional[BSTree.Node] = right

            self.value: Any = value
            self.bf: int = balance

        def __len__(self) -> int:
            left_len = 0
            right_len = 0
            if self.left is not None:
                left_len = len(self.left)
            if self.right is not None:
                right_len = len(self.right)

            return 1 + left_len + right_len

        def __iter__(self) -> Generator[Any, None, None]:
            # Note: this will do an inorder traversal of this node.
            val: Any  # This line makes the static type checker happy

            # Recursively traverse left subtree
            if self.left is not None:
                for val in self.left:
                    yield val
            # Visit this node
            yield self.value
            # Recursively traverse right subtree
            if self.right is not None:
                for val in self.right:
                    yield val

        def __reversed__(self) -> Generator[Any, None, None]:
            # Note: this will do a reverse inorder traversal of this node.
            val: Any  # This line makes the static type checker happy

            # Recursively traverse right subtree
            if self.right is not None:
                for val in reversed(self.right):
                    yield val
            # Visit this node
            yield self.value
            # Recursively traverse left subtree
            if self.left is not None:
                for val in reversed(self.left):
                    yield val

        def __str__(self) -> str:
            return str(self.value)

        def __repr__(self) -> str:
            return (
                f"{self.__class__.__name__}("
                    f"{self.value!r}, balance={self.bf!r}"
                ")"
            )

        def height(self) -> int:
            """
            Get the height of the subtree.

            The height is defined as the length of the longest path from
            the root node to any leaf node. Note that subtrees with no
            children have a height of 0.

            Returns
            -------
            int
                Height of this subtree.
            """
            # Default child heights are -1 so the +1 later results in 0
            left_height = -1
            right_height = -1
            if self.left is not None:
                left_height = self.left.height()
            if self.right is not None:
                right_height = self.right.height()

            return max(left_height, right_height) + 1

        def find_min(self) -> Any:
            """
            Find the minimum element of the subtree.

            Returns
            -------
            any
                Value of minimum element.
            """
            node: Optional[BSTree.Node] = self
            while node.left is not None:
                node = node.left
            return node.value

        def find_max(self) -> Any:
            """
            Find the maximum element of the subtree.

            Returns
            -------
            any
                Value of maximum element.
            """
            node: Optional[BSTree.Node] = self
            while node.right is not None:
                node = node.right
            return node.value

        def insert(self, val: Any) -> "BSTree.Node":
            """
            Insert a value into the subtree.

            The insertion is done partly in-place, but not entirely. It
            is thus recommended to store the result back to the node
            being operated on.

            Parameters
            ----------
            val
                Value to insert.

            Returns
            -------
            BSTree.Node
                Root node of subtree after the value is inserted.
            """
            if val == self.value:
                raise RuntimeError("value is already present")

            # If value belongs in left subtree
            if val < self.value:
                if self.left is None:
                    # Create left subtree if it doesn't exist
                    self.left = BSTree.Node(val)
                    self.bf -= 1
                else:
                    old_bf = self.left.bf
                    # If left subtree exists, insert this value in it
                    self.left = self.left.insert(val)

                    if (
                        # If left subtree balance factor got more non-positive
                        old_bf <= 0 and self.left.bf < old_bf
                        # or more non-negative
                        or old_bf >= 0 and self.left.bf > old_bf
                    ):
                        # The left subtree must have increased in height
                        self.bf -= 1
            # If value belongs in right subtree
            elif val > self.value:
                if self.right is None:
                    # Create right subtree if it doesn't exist
                    self.right = BSTree.Node(val)
                    self.bf += 1
                else:
                    old_bf = self.right.bf
                    # If right subtree exists, insert this value into it
                    self.right = self.right.insert(val)

                    if (
                        # If right subtree balance factor got more non-positive
                        old_bf <= 0 and self.right.bf < old_bf
                        # or more non-negative
                        or old_bf >= 0 and self.right.bf > old_bf
                    ):
                        # The right subtree must have increased in height
                        self.bf += 1

            # Make sure it stays balanced
            return self.balance()

        def delete(self, val: Any) -> Optional["BSTree.Node"]:
            """
            Delete a value from the subtree.

            The deletion is done partly in-place, but not entirely. It
            is thus recommended to store the result back to the node
            being operated on.

            Parameters
            ----------
            val
                Value to delete.

            Returns
            -------
            BSTree.Node
                Root node of subtree after the value is deleted.
            """
            # If value would be in left subtree
            if val < self.value:
                # If there is no left subtree, the value doesn't exist
                if self.left is None:
                    raise RuntimeError("value is not present")

                old_bf = self.left.bf
                # Delete this value from the left subtree
                self.left = self.left.delete(val)

                if (
                    # If left subtree no longer exists
                    self.left is None
                    # or its balance factor changed to 0
                    or abs(old_bf) == 1 and self.left.bf == 0
                ):
                    # The left subtree must have decreased in height
                    self.bf += 1
            # If value would be in right subtree
            elif val > self.value:
                # If there is no right subtree, the value doesn't exist
                if self.right is None:
                    raise RuntimeError("value is not present")

                old_bf = self.right.bf
                # Delete this value from the right subtree
                self.right = self.right.delete(val)

                if (
                    # If right subtree no longer exists
                    self.right is None
                    # or its balance factor changed to 0
                    or abs(old_bf) == 1 and self.right.bf == 0
                ):
                    # The right subtree must have decreased in height
                    self.bf -= 1
            # If value is in this node, and thus must be deleted
            else:
                # If one child exists, replace this node with that child
                if self.left is None:
                    return self.right
                elif self.right is None:
                    return self.left
                # Note that this also works in the case that no children exist

                # If we're still here, two children exist,
                # and we must get creative

                # Set this node's value to the previous (in-order) value
                successor_val = self.left.find_max()
                self.value = successor_val

                old_bf = self.left.bf
                # Delete the node with this previous value
                # (This will never be a node with two children)
                self.left = self.left.delete(successor_val)
                if (
                    # If left subtree no longer exists
                    self.left is None
                    # or its balance factor changed to 0
                    or abs(old_bf) == 1 and self.left.bf == 0
                ):
                    # The left subtree must have decreased in height
                    self.bf += 1

            # Make sure it stays balanced
            return self.balance()

        def balance(self) -> "BSTree.Node":
            """
            Balance the subtree, so that its balance factor stays
            between -1 and 1 inclusive.

            The balancing is done out-of-place. It is thus required to
            store the result back to the node being operated on.

            Returns
            -------
            BSTree.Node
                Root node of subtree after it is balanced.
            """
            if self.bf < -1:
                assert self.left is not None
                if self.left.bf <= 0:
                    # Left-left case
                    return self.rotate_right()
                else:
                    # Left-right case
                    self.left = self.left.rotate_left()
                    return self.rotate_right()
            elif self.bf > 1:
                assert self.right is not None
                if self.right.bf >= 0:
                    # Right-right case
                    return self.rotate_left()
                else:
                    # Right-left case
                    self.right = self.right.rotate_right()
                    return self.rotate_left()

            return self

        def rotate_left(self) -> "BSTree.Node":
            """
            Rotate the subtree to the left.

            The rotation is done out-of-place. It is thus required to
            store the result back to the node being operated on.

            Returns
            -------
            BSTree.Node
                Root node of subtree after it is rotated.
            """
            b = self.right
            if b is None:
                raise ValueError("cannot left-rotate node without right child")

            # Rotate the subtree
            self.right = b.left
            b.left = self

            # Update balance factors
            self.bf -= 1 + max(b.bf, 0)
            b.bf -= 1 - min(self.bf, 0)

            return b

        def rotate_right(self) -> "BSTree.Node":
            """
            Rotate the subtree to the right.

            The rotation is done out-of-place. It is thus required to
            store the result back to the node being operated on.

            Returns
            -------
            BSTree.Node
                Root node of subtree after it is rotated.
            """
            b = self.left
            if b is None:
                raise ValueError("cannot right-rotate node without left child")

            # Rotate the subtree
            self.left = b.right
            b.right = self

            # Update balance factors
            self.bf += 1 - min(b.bf, 0)
            b.bf += 1 + max(self.bf, 0)

            return b


    def __init__(self, iterable: Optional[Iterable[Any]] = None):
        """
        Create a self-balancing binary search tree.

        This is implemented as an AVL tree, where the heights of the two
        child subtrees differ by at most one at all times.

        Parameters
        ----------
        iterable : iterable, optional
            Iterable to populate the tree with.
        """
        self.root: Optional[BSTree.Node] = None

        if iterable is not None:
            for val in iterable:
                self.insert(val)

    def __len__(self) -> int:
        if self.root is None:
            return 0
        return len(self.root)

    def __iter__(self) -> Generator[Any, None, None]:
        if self.root is None:
            return

        for val in self.root:
            yield val

    def __reversed__(self) -> Generator[Any, None, None]:
        if self.root is None:
            return

        for val in reversed(self.root):
            yield val

    def __getitem__(self, pos: int) -> Any:
        # This handles both positive and negative indices in 4 lines!
        # Isn't Python great sometimes?
        for i, val in enumerate(reversed(self) if pos < 0 else self):
            if (-i - 1 if pos < 0 else i) == pos:
                return val

        raise IndexError("binary search tree index out of range")

    def __setitem__(self, pos: int, val: Any) -> None:
        self.delete(self[pos])
        self.insert(val)

    def __contains__(self, val: Any) -> bool:
        node: Optional[BSTree.Node] = self.root

        while node is not None:
            if val < node.value:
                node = node.left
            elif val > node.value:
                node = node.right
            else:
                return True
        return False

    # Algorithm from J.V. on StackOverflow
    # https://stackoverflow.com/a/54074933
    def __str__(self) -> str:
        if self.root is None:
            return ""

        def str_helper(t: BSTree.Node) -> tuple[list[str], int, int, int]:
            # If node has no children
            if t.left is None and t.right is None:
                line = str(t)
                width = len(line)
                height = 1
                middle = width // 2
                return [line], width, height, middle

            # If node has only right child
            if t.left is None:
                assert t.right is not None
                lines, n, p, x = str_helper(t.right)
                s = str(t)
                u = len(s)
                # First line has underscores to the right of the value
                first_line = s + (x * "_").ljust(n)
                # Second line has slanted line pointing to the right child
                second_line = "\\".rjust(u + x + 1).ljust(n + u)
                shifted_lines = [(u * " ") + line for line in lines]
                return (
                    [first_line, second_line] + shifted_lines,
                    n + u, p + 2, u // 2
                )

            # If node has only left child
            if t.right is None:
                assert t.left is not None
                lines, n, p, x = str_helper(t.left)
                s = str(t)
                u = len(s)
                # First line has underscores to the left of the value
                first_line = ((n - x - 1) * "_").rjust(n) + s
                # Second line has slanted line pointing to the left child
                second_line = "/".rjust(x + 1).ljust(n + u)
                shifted_lines = [line + (u * " ") for line in lines]
                return (
                    [first_line, second_line] + shifted_lines,
                    n + u, p + 2, n + (u // 2)
                )

            # If node has left and right child
            left, n, p, x = str_helper(t.left)
            right, m, q, y = str_helper(t.right)
            s = str(t)
            u = len(s)
            # First line has underscores to the left and right of the value
            first_line = ((n - x - 1) * "_").rjust(n) + s + (y * "_").ljust(m)
            # Second line has slanted lines pointing to the children
            second_line = (
                "/".rjust(x + 1).ljust(n)
                + (u * " ")
                + "\\".rjust(y + 1).ljust(m)
            )
            # Ensure that left and right string lines match in height
            if p < q:
                left += [n * " "] * (q - p)
            elif q < p:
                right += [m * " "] * (p - q)
            # Join left and right string lines
            lines = [first_line, second_line] + [
                a + (u * " ") + b for a, b in zip(left, right)
            ]
            return lines, n + m + u, max(p, q) + 2, n + u // 2

        lines, *_ = str_helper(self.root)
        return "\n".join(lines)

    def __repr__(self) -> str:
        values: list[Any] = [v for v in self]
        if values:
            return f"{self.__class__.__name__}({values!r})"
        else:
            return f"{self.__class__.__name__}()"

    def insert(self, val: Any) -> bool:
        """
        Insert a value into the tree.

        Parameters
        ----------
        val
            Value to insert.

        Returns
        -------
        bool
            True if the insert was successful.
        """
        if val is None:
            return False

        if self.root is None:
            self.root = BSTree.Node(val)
            return True

        try:
            self.root = self.root.insert(val)
        except:
            return False
        else:
            return True

    def delete(self, val: Any) -> bool:
        """
        Delete a value from the tree.

        Parameters
        ----------
        val
            Value to delete.

        Returns
        -------
        bool
            True if the delete was successful.
        """
        if val is None:
            return False

        if self.root is None:
            return False

        try:
            self.root = self.root.delete(val)
        except:
            return False
        else:
            return True

    def index(self, val: Any) -> int:
        """
        Find index of value.

        Parameters
        ----------
        val
            Value to find.

        Returns
        -------
        int
            Index of value.
        """
        for i, v in enumerate(self):
            if v == val:
                return i

        raise ValueError(f"{val!r} is not in binary search tree")

    def __bool__(self) -> bool:
        return self.root is not None
