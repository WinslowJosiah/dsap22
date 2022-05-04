# sys.path hack for custom module import
import sys
import os.path as path

sys.path.insert(0, path.join(path.dirname(path.abspath(__file__)), r".."))

from utils import HashMap


def get_letter_freq(phrase: str) -> HashMap:
    """
    Count the letters in `phrase`. The counts are returned as key-value
    pairs in a HashMap.

    Parameters
    ----------
    phrase : str
        Phrase to count the letters of.

    Returns
    -------
    HashMap
        Hash map with the letters as keys and their counts as values.
    """
    result = HashMap()
    for c in phrase.lower():
        if not c.isalpha():
            continue
        result[c] = result.get(c, 0) + 1
    return result


def get_freq_difference(h1: HashMap, h2: HashMap) -> HashMap:
    """
    Subtract the values for each key in `h2` from the values for each
    key in `h1`, keeping only positive counts.

    The values of `h1` and `h2` are assumed to be numeric.

    Parameters
    ----------
    h1 : HashMap
        Hash map to be subtracted from.
    h2 : HashMap
        Hash map to subtract.

    Returns
    -------
    HashMap
        Hash map with values of `h2` subtracted from values of `h1`,
        keeping only positive counts.
    """
    result = h1.copy()
    for k, v in h2.items():
        if k not in result:
            continue

        diff: int | float = result[k] - v
        if diff <= 0:
            del result[k]
        else:
            result[k] = diff

    return result


def main():
    source_phrase = input("Enter source phrase: ")
    source_map = get_letter_freq(source_phrase)
    print(source_map)

    target_phrase = input("Enter target phrase: ")
    target_map = get_letter_freq(target_phrase)
    print(target_map)

    if source_map == target_map:
        print("These phrases are anagrams!")
    else:
        print("These phrases are not anagrams.")
        print()

        source_diff = get_freq_difference(source_map, target_map)
        if source_diff:
            print("The source phrase has...")
        for k, v in source_diff.items():
            plural = "" if v == 1 else "'s"
            print(f"\t{v} extra {k}{plural}")

        target_diff = get_freq_difference(target_map, source_map)
        if target_diff:
            print("The target phrase has...")
        for k, v in target_diff.items():
            plural = "" if v == 1 else "'s"
            print(f"\t{v} extra {k}{plural}")


if __name__ == "__main__":
    main()
