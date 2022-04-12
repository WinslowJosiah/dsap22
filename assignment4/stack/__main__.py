# sys.path hack for custom module import
import sys
import os.path as path
sys.path.insert(0, path.join(path.dirname(path.abspath(__file__)), r"..\.."))

import math
import operator
import os
from typing import Any

from utils import Stack


# Small function to call the appropriate clear-screen function
def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")


def main():
    def duplicate(x: Any) -> tuple[Any, Any]:
        return x, x

    def pop(x: Any) -> tuple[()]:
        return tuple()

    def swap(x: Any, y: Any) -> tuple[Any, Any]:
        return y, x

    # Width of each row of operations in menu
    OPS_WIDTH = 6
    # Legal operations
    OPERATIONS = {
        "+": (operator.add, 2),
        "-": (operator.sub, 2),
        "*": (operator.mul, 2),
        "/": (operator.floordiv, 2),
        "%": (operator.mod, 2),
        "^": (operator.pow, 2),
        "~": (operator.neg, 1),
        "!": (math.factorial, 1),
        "sqrt": (math.isqrt, 1),
        "dup": (duplicate, 1),
        "pop": (pop, 1),
        "swap": (swap, 2),
    }

    stack = Stack()

    # This testing suite will run forever
    while True:
        clear_screen()

        if len(stack) == 0:
            print("Stack is empty.")
        else:
            # I print the stack with the "top" at the bottom,
            # because IMHO it makes the order clearer
            for val in reversed(stack):
                print(val)
        print()

        print("Valid operations:")
        for i, op in enumerate(OPERATIONS):
            end_char = "\t"
            if i + 1 == len(OPERATIONS) or (i + 1) % OPS_WIDTH == 0:
                end_char = "\n"
            print(op, end=end_char)

        # Input an int or operator (from a choice of several)
        input_val = None
        while True:
            input_str = input("Enter number or operation: ")
            # Select correct operation if available
            if input_str in OPERATIONS:
                input_val = OPERATIONS[input_str]
                break

            # Otherwise, try converting to an int
            try:
                input_val = int(input_str)
                break
            except ValueError:
                print("Please input a number or operation.")

        # If input is an int
        if isinstance(input_val, int):
            # Push that int
            stack.push(input_val)
        # If input is an operation
        else:
            # Try doing that operation
            try:
                stack.do_operation(*input_val)
            except Exception as e:
                print(f"Threw {e.__class__.__name__} with message:\n{e}")
                print()
                _ = input("Press any key to continue...")


if __name__ == "__main__":
    main()
