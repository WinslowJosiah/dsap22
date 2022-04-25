# sys.path hack for custom module import
import sys
import os.path as path
sys.path.insert(0, path.join(path.dirname(path.abspath(__file__)), r".."))

from ast import literal_eval
from typing import Any, Iterable

from utils import SLList


def main():
    def input_value(prompt: str = ""):
        while True:
            val_str = input(prompt)
            try:
                return literal_eval(val_str)
            except:
                print("Error parsing value. Please try again.")

    sllist = input_sllist()
    print("Single linked list initialized.")
    print(sllist)
    print(repr(sllist))

    while True:
        print()

        print("1 - display list")
        print("2 - count nodes")
        print("3 - search")
        print("4 - insert at beginning")
        print("5 - insert at end")
        print("6 - insert at position")
        print("7 - delete first node")
        print("8 - delete last node")
        print("9 - delete at position")
        print("10 - get item at position")
        print("11 - set item at position")
        print("12 - reverse list")
        print("13 - sort by exchanging data")
        print("14 - sort by exchanging links")
        print("15 - insert cycle")
        print("16 - detect cycle")
        print("17 - remove cycle")
        print("18 - quit")

        try:
            choice = int(input("Enter function to test: "))
        except ValueError:
            print("Please enter a number.")
            continue
        print()

        match choice:
            case 1: # display list
                print(f"str(sllist) = {str(sllist)}")
                print(f"repr(sllist) = {repr(sllist)}")

            case 2: # count nodes
                print(f"Length of list is {len(sllist)}.")

            case 3: # search
                val = input_value("Enter value to search for: ")
                try:
                    index = sllist.index(val)
                except Exception as e:
                    print(f"Threw {e.__class__.__name__} with message:\n{e}")
                else:
                    print(f"Value {val!r} found at index {index}.")

            case 4: # insert at beginning
                val = input_value("Enter value to insert: ")
                sllist.prepend(val)
                print(f"Value {val!r} inserted at beginning.")

            case 5: # insert at end
                val = input_value("Enter value to insert: ")
                sllist.append(val)
                print(f"Value {val!r} inserted at end.")

            case 6: # insert at position
                pos = input_value("Enter position to insert at: ")
                val = input_value("Enter value to insert: ")
                try:
                    sllist.insert(pos, val)
                except Exception as e:
                    print(f"Threw {e.__class__.__name__} with message:\n{e}")
                else:
                    print(f"Value {val!r} inserted at position {pos}.")

            case 7: # delete first node
                try:
                    val = sllist.pop_front()
                except Exception as e:
                    print(f"Threw {e.__class__.__name__} with message:\n{e}")
                else:
                    print(f"Value {val!r} deleted from beginning.")

            case 8: # delete last node
                try:
                    val = sllist.pop_back()
                except Exception as e:
                    print(f"Threw {e.__class__.__name__} with message:\n{e}")
                else:
                    print(f"Value {val!r} deleted from end.")

            case 9: # delete at position
                pos = input_value(
                    "Enter position to delete from (None for end): "
                )
                try:
                    val = sllist.pop(pos)
                except Exception as e:
                    print(f"Threw {e.__class__.__name__} with message:\n{e}")
                else:
                    if pos is None:
                        print(f"Value {val!r} deleted from end.")
                    else:
                        print(f"Value {val!r} deleted from position {pos}.")

            case 10: # get item at position
                pos = input_value("Enter position of value: ")
                try:
                    val = sllist[pos]
                except Exception as e:
                    print(f"Threw {e.__class__.__name__} with message:\n{e}")
                else:
                    print(f"The value at index {pos} is {val!r}.")

            case 11: # set item at position
                pos = input_value("Enter position of value: ")
                val = input_value("Enter new value: ")
                try:
                    sllist[pos] = val
                except Exception as e:
                    print(f"Threw {e.__class__.__name__} with message:\n{e}")
                else:
                    print(f"Index {pos} set to {val!r}.")

            case 12: # reverse list
                try:
                    sllist.reverse()
                except Exception as e:
                    print(f"Threw {e.__class__.__name__} with message:\n{e}")
                else:
                    print(f"List has been reversed.")

            case 13: # sort by exchanging data
                try:
                    sllist.sort_values()
                except Exception as e:
                    print(f"Threw {e.__class__.__name__} with message:\n{e}")
                else:
                    print(f"List has been sorted by data.")

            case 14: # sort by exchanging links
                try:
                    sllist.sort_items()
                except Exception as e:
                    print(f"Threw {e.__class__.__name__} with message:\n{e}")
                else:
                    print(f"List has been sorted by links.")

            case 15: # insert cycle
                mu = input_value("Enter starting index of cycle: ")
                try:
                    sllist.insert_cycle(mu)
                except Exception as e:
                    print(f"Threw {e.__class__.__name__} with message:\n{e}")
                else:
                    print(
                        f"Cycle has been inserted starting at position {mu}."
                    )

            case 16: # detect cycle
                lam, mu = sllist.find_cycle()
                if lam == 0:
                    print(f"No cycle found.")
                else:
                    print(
                        f"{lam}-length cycle found starting at position {mu}."
                    )
                print(f"Length of list is {lam + mu}.")

            case 17: # remove cycle
                sllist.remove_cycle()
                print(f"Cycle has been removed.")

            case 18: # quit
                break

            case _:
                print("Invalid choice.")


def input_sllist():
    # Enter iterable for SLList constructor
    while True:
        iterable: Iterable[Any]
        try:
            iterable_str = input(
                "Iterable to initialize linked list (blank for nothing): "
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

    # Enter mu-value for SLList constructor
    while True:
        try:
            mu_str = input("Starting index of cycle (blank for no cycle): ")
            if not mu_str or mu_str.isspace():
                mu = None
            else:
                mu = literal_eval(mu_str)
        except:
            print("Error parsing value. Please try again.")
            continue
        else:
            break

    return SLList(iterable, mu)


if __name__ == "__main__":
    main()
