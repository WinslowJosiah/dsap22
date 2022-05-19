# sys.path hack for custom module import
import sys
import os.path as path

sys.path.insert(0, path.join(path.dirname(path.abspath(__file__)), r".."))

import gdown  # type: ignore
import math
import textwrap
import time
import wordfreq
from sortedcontainers import SortedKeyList  # type: ignore
from typing import Any, Callable, NamedTuple, Optional, Sequence

from utils import Trie

FILEDIR = path.dirname(path.abspath(__file__))

WORD_SEPARATOR = "  "

SCRABBLE_TILE_SCORES = {
    "a": 1, "e": 1, "i": 1, "l": 1, "n": 1,
    "o": 1, "r": 1, "s": 1, "t": 1, "u": 1,
    "d": 2, "g": 2,
    "b": 3, "c": 3, "m": 3, "p": 3,
    "f": 4, "h": 4, "v": 4, "w": 4, "y": 4,
    "k": 5,
    "j": 8, "x": 8,
    "q": 10, "z": 10,
}


class Entry(NamedTuple):
    definition: str
    score: int


def scrabble_score(word: str) -> int:
    return sum(SCRABBLE_TILE_SCORES.get(c.lower(), 0) for c in word)


def search_trie(
    trie: Trie,
    word: str,
    max_cost: Optional[int] = None,
    max_results: Optional[int] = None,
    sort_by: Optional[Callable[[str], Any]] = None
) -> dict[str, int]:
    """
    Search a trie for words most closely matching `word` according to
    Levenshtein distance.

    Parameters
    ----------
    trie : Trie
        Trie of words to search in.
    word : str
        Word to search for approximate matches to.
    max_cost : int, default `math.ceil(len(word) / 2)`
        Maximum Levenshtein distance to consider for matches.
    max_results : int, optional
        Maximum number of results to return.
    sort_by : Callable, optional
        Function to sort words by. This takes the word as a string and
        should return a value which can be used as a key for sorting.

    Returns
    -------
    dict of {str : int}
        Dict with words from the trie as keys and their Levenshtein
        distances from `word` as values, sorted in ascending order by
        Levenshtein distance (and, optionally, `sort_by`).
    """
    def search_trie_helper(node: Trie, prev_row: Sequence[int], node_word: str):
        nonlocal results, max_cost
        assert max_cost is not None

        # Build current row of matrix
        cost: int = prev_row[0] + 1
        min_cost: int = cost
        current_row: list[int] = [cost]

        for column in range(1, len(prev_row)):
            insert_cost = cost + 1
            delete_cost = prev_row[column] + 1
            replace_cost = prev_row[column - 1]
            if word[column - 1] != node_word[-1]:
                replace_cost += 1

            cost = min(insert_cost, delete_cost, replace_cost)
            current_row.append(cost)
            min_cost = min(cost, min_cost)

        # If this node is a word, and the cost is within range
        if node.is_word and cost <= max_cost:
            # Add this to the results
            results.add((node_word, cost))  # type: ignore

            # Cull the result list and max cost if necessary
            if max_results is not None:
                try:
                    results.pop(max_results)
                except:
                    pass
                else:
                    max_cost = results[-1][1]

        assert max_cost is not None
        # If the minimum possible cost is within range
        if min_cost <= max_cost:
            # Search one node deeper in the trie
            for c, new_node in node.edges.items():
                search_trie_helper(new_node, current_row, node_word + c)

    # Set up variables for search
    if max_cost is None:
        max_cost = math.ceil(len(word) / 2)

    current_row: Sequence[int] = range(len(word) + 1)
    if sort_by is None:
        def ordering(value: tuple[str, int]) -> Any:
            return value[1]
    else:
        def ordering(value: tuple[str, int]) -> Any:
            return (value[1], sort_by(value[0]))
    results: SortedKeyList = SortedKeyList(key=ordering)

    # Start searching from the root of the tree
    for c, node in trie.edges.items():
        search_trie_helper(node, current_row, c)

    return dict(results)


def main():
    def input_word(prompt: str = "") -> str:
        while True:
            # Remove non-alphabetic characters
            word = "".join(
                c.lower() for c in input(prompt)
                if c.isalpha()
            )
            # Return if word is non-empty
            if word:
                return word
            print("Please enter something.")


    # Download Collins Scrabble Words with definitions (2019)
    dict_path: str = path.join(FILEDIR, "csw19-definitions.txt")
    print("Downloading wordlist...")
    gdown.cached_download(  # type: ignore
        "https://drive.google.com/uc?id=1XIFdZukAcDRiDIOgR_rHpICrrgJbLBxV",
        dict_path, quiet=True
    )
    print("Done downloading.")

    # Create trie using words from CSW19
    print("Creating trie...")
    words: Trie = Trie()
    with open(dict_path) as f:
        f.readline()  # Header line
        f.readline()  # Blank line
        for line in f:
            word, definition = line.strip().split("\t")
            word = word.lower()

            words[word] = Entry(definition, scrabble_score(word))
    print("Trie created.")
    print(f"Length: {len(words)} words")
    print()


    def look_up_word():
        # Enter search term
        search_term = input_word("Enter word: ")
        print()
        print(f"You entered: {search_term}")

        definition_exists: bool = False
        # If search term is in the dictionary
        if search_term in words:
            entry: Entry = words[search_term]

            # Print the definition
            print()
            print(f"{search_term}  (score: {entry.score})")
            print(f"\t{entry.definition}")
            print()
            definition_exists = True

        # If we're still here, the word is not a part of the dictionary,
        # so we have to do a somewhat fancy approximate-string search

        # Start timing
        start_time_ns: int = time.perf_counter_ns()

        # Search for approximate matches (one call, that's all!)
        search_results: dict[str, int] = search_trie(
            words, search_term,
            max_results=100,
            sort_by=lambda k: (
                # Word frequency (descending)
                -wordfreq.word_frequency(k, "en"),
                # Absolute differences of each Unicode codepoint
                # (basically, how close it would be in a dictionary)
                [abs(ord(c) - ord(d)) for c, d in zip(k, search_term)]
            )
        )

        # Stop timing
        stop_time_ns: int = time.perf_counter_ns()

        # Calculate time elapsed and format as string
        time_diff_ns: int = stop_time_ns - start_time_ns
        time_diff_str: str
        if time_diff_ns < 1e3:
            time_diff_str = f"{time_diff_ns} ns"
        elif time_diff_ns < 1e6:
            time_diff_str = f"{time_diff_ns / 1e3:.3f} μs"
        elif time_diff_ns < 1e9:
            time_diff_str = f"{time_diff_ns / 1e6:.3f} ms"
        else:
            time_diff_str = f"{time_diff_ns / 1e9:.3f} s"

        if search_results:
            # Display results
            print(
                "But perhaps you meant..."
                if definition_exists else
                "Did you mean..."
            )
            print()

            # Delete search term from results if it exists
            if definition_exists:
                del search_results[search_term]

            # Wrap lines of search results using textwrap
            for line in textwrap.wrap(WORD_SEPARATOR.join(search_results)):
                print(line)
        else:
            # Let the user know that there were no results
            print(
                "I have no idea what else you could've meant by this."
                if definition_exists else
                "I have no idea what you could've meant by this."
            )

        print()
        print(f"Time elapsed: {time_diff_str}")


    def find_words_starting_with_prefix():
        # Enter search_term
        search_term = input_word("Enter prefix: ")

        # Search for words starting with search term
        search_results: list[str] = list(words.query(search_term))

        print()
        if search_results:
            # Display results
            for line in textwrap.wrap(WORD_SEPARATOR.join(search_results)):
                print(line)

            print()
            print(f"Number of results: {len(search_results)}")
        else:
            # Let the user know that there were no results
            print(f"There are no words that start with \"{search_term}\".")


    def add_word_to_dictionary():
        # Enter word
        word = input_word("Enter word: ")

        # If the word already exists in the dictionary
        if word in words:
            print(f"\"{word}\" is already in the dictionary.")

            # Ask the user whether they want to overwrite the definition
            while True:
                # Keep only the first Y or N, if it exists
                yes_or_no = "".join(
                    c.lower() for c in input("Overwrite? (Y/N) ")
                    if c.lower() in "yn"
                )[:1]
                if yes_or_no:
                    break
                print("Please enter Y or N.")

            if yes_or_no == "n":
                return

        print()
        # Enter definition
        while True:
            # Remove spaces from start and end
            definition = input("Enter definition: ").strip()
            # Break if definition is non-empty
            if definition:
                break
            print("Please enter a definition.")

        words[word] = Entry(definition, scrabble_score(word))
        print(f"Entry added for \"{word}\".")


    def remove_word_from_dictionary():
        # Enter word
        word = input_word("Enter word: ")
        try:
            del words[word]
        except KeyError:
            print(f"\"{word}\" is not in the dictionary.")
        else:
            print(f"\"{word}\" removed from dictionary.")


    # Main loop
    while True:
        print("1\tLook up word")
        print("2\tFind all words starting with...")
        print("3\tAdd word to dictionary")
        print("4\tRemove word from dictionary")
        print("5\tExit")
        print()

        input_str = input("Enter choice from 1 to 5: ")

        try:
            input_val = int(input_str)
        except ValueError:
            print("Please enter a number.")
            continue

        match input_val:
            case 1:
                look_up_word()
            case 2:
                find_words_starting_with_prefix()
            case 3:
                add_word_to_dictionary()
            case 4:
                remove_word_from_dictionary()
            case 5:
                break
            case _:
                print("Please enter a choice from 1 to 5.")
                continue

        print()


if __name__ == "__main__":
    main()
