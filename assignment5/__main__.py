# sys.path hack for custom module import
import sys
import os.path as path
sys.path.insert(0, path.join(path.dirname(path.abspath(__file__)), r".."))

from ast import literal_eval
from typing import Any, Iterable

from utils import BSTree


def main():
    def input_value(prompt: str = ""):
        while True:
            val_str = input(prompt)
            try:
                return literal_eval(val_str)
            except:
                print("Error parsing value. Please try again.")

    bstree = input_bstree()
    print("Binary search tree initialized.")
    print(bstree)
    print(repr(bstree))

    while True:
        print()

        print("1 - display tree")
        print("2 - count nodes")
        print("3 - search")
        print("4 - insert")
        print("5 - delete")
        print("6 - get item at position")
        print("7 - set item at position")
        print("8 - quit")

        try:
            choice = int(input("Enter function to test: "))
        except ValueError:
            print("Please enter a number.")
            continue
        print()

        match choice:
            case 1:  # display tree
                print(f"str(bstree) = \n{str(bstree)}")
                print(f"repr(bstree) = \n{repr(bstree)}")

            case 2:  # count nodes
                print(f"Length of binary search tree is {len(bstree)}.")

            case 3:  # search
                val = input_value("Enter value to search for: ")
                if val in bstree:
                    print(f"Value {val!r} found in tree.")
                else:
                    print(f"Value {val!r} not found in tree.")

            case 4:  # insert
                val = input_value("Enter value to insert: ")
                if bstree.insert(val):
                    print(f"Value {val!r} inserted into tree.")
                else:
                    print(f"Value {val!r} could not be inserted into tree.")

            case 5:  # delete
                val = input_value("Enter value to delete: ")
                if bstree.delete(val):
                    print(f"Value {val!r} deleted from tree.")
                else:
                    print(f"Value {val!r} could not be deleted from tree.")

            case 6:  # get item at position
                pos = input_value("Enter position of value: ")
                try:
                    val = bstree[pos]
                except Exception as e:
                    print(f"Threw {e.__class__.__name__} with message:\n{e}")
                else:
                    print(f"The value at index {pos} is {val!r}.")

            case 7:  # set item at position
                pos = input_value("Enter position of value: ")
                val = input_value("Enter new value: ")
                try:
                    bstree[pos] = val
                except Exception as e:
                    print(f"Threw {e.__class__.__name__} with message:\n{e}")
                else:
                    print(f"Index {pos} set to {val!r}.")

            case 8:  # quit
                break

            case _:
                print("Invalid choice.")


def input_bstree():
    # Enter iterable for BSTree constructor
    while True:
        iterable: Iterable[Any]
        try:
            iterable_str = input(
                "Iterable to initialize binary search tree "
                "(blank for nothing): "
            )
            if not iterable_str or iterable_str.isspace():
                iterable = []
            else:
                iterable = literal_eval(iterable_str)
        except:
            print("Error parsing iterable. Please try again.")
            continue

        # Check if iterable is actually iterable
        try:
            iter(iterable)
        except TypeError:
            print("Value is not iterable. Please try again.")
            continue
        else:
            break

    return BSTree(iterable)


if __name__ == "__main__":
    main()
