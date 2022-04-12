# sys.path hack for custom module import
import sys
import os.path as path
sys.path.insert(0, path.join(path.dirname(path.abspath(__file__)), r"..\.."))

import json
import random
import re
import textwrap
from collections import defaultdict
from imdb import Cinemagoer, IMDbError  # type: ignore
from imdb.helpers import makeTextNotes  # type: ignore
from typing import Any, Optional, Sequence, TypedDict
from utils import Queue

FILEDIR = path.dirname(path.abspath(__file__))

KEVIN_BACON_ID = "nm0000102"
MAX_ACTOR_SEARCH_RESULTS = 10
MAX_ACTOR_DIST_RESULTS = 30
MAX_BIO_LENGTH = 300
BFS_PROGRESS_FREQ = 1000


# Helper classes for type hints
class ConnectionInfo(TypedDict):
    dist: int
    preds: defaultdict[str, set[str]]


class PredecessorInfo(TypedDict):
    actor: str
    movies: set[str]


# Algorithm from Max Halford
# https://maxhalford.github.io/blog/weighted-sampling-without-replacement/
def weighted_sample_without_replacement(
    population: Sequence[Any],
    weights: Sequence[float],
    k: int = 1
) -> list[Any]:
    """
    Return a `k` sized list of elements chosen from the `population`
    without replacement.

    Parameters
    ----------
    population : iterable
        Sequence to sample from.
    weights : iterable
        Sequence of weights for each item in `population`.
    k : int, default 1
        Number of elements to sample.

    Returns
    -------
    list
        Sampled elements from `population`.
    """
    # If k is negative, bring it to 0
    k = max(k, 0)

    v = [random.random() ** (1 / w if w else float("inf")) for w in weights]
    order = sorted(range(len(population)), key=lambda i: v[i])
    return [population[i] for i in order[-k:]]


# Helper function to input an actor by name
def input_actor(prompt: str = "", default: str = KEVIN_BACON_ID) -> str:
    """
    Ask the user for the name of an actor, and return their IMDb actor
    ID.

    Parameters
    ----------
    prompt : str, optional
        Input prompt when asking for actor's name.
    default : str, default "nm0000102", meaning Kevin Bacon
        Actor ID to return if name input is blank.

    Returns
    -------
    str
        Actor ID which was selected.
    """
    # Cinemagoer will help us with searching for actors
    # (I could use it for filmography/costar data, and I would prefer it,)
    # (but it's too slow!)
    cg: Any = Cinemagoer()

    people: list[Any] = []
    # Ask user for search string until actor results are given
    while not people:
        input_str = input(prompt).strip()

        # If string is blank except for whitespace, return default
        if not input_str:
            return default

        # If string is IMDb ID, try getting that person directly
        m = re.fullmatch(r"(?:nm)?(\d+)", input_str)
        if m:
            try:
                person = cg.get_person(m.group(1))
            except IMDbError:
                print("I don't recognize this as the ID of an actor/actress.")
                print("Please try again.")
                continue
            else:
                print(f"Entered ID for {person['long imdb name']}.")
                return f"nm{person.getID()}"

        people = cg.search_person(input_str)

        # If actor search returned no results
        if not people:
            # Warn the user
            print("I don't recognize this as the name of an actor/actress.")
            print("Please try again.")

    # Truncate results to some maximum number
    people = people[:MAX_ACTOR_SEARCH_RESULTS]

    # If actor search returned results
    for i, person in enumerate(people):
        # Print actor's name with 1-based index
        print(f"{i + 1}:\t{person['long imdb name']}")

        # Display biography to disambiguate, if possible
        cg.update(person, ["biography"])
        bio = person.get("biography")
        if bio:
            # Get biography text, without author note...
            bio_text: str = makeTextNotes("%(text)s")(bio[0])
            # ...and shorten it to fit on-screen
            print(f"\t{textwrap.shorten(bio_text, MAX_BIO_LENGTH)}")

    # If only one person was returned, use them
    if len(people) == 1:
        print("Using the only result.")
        return f"nm{people[0].getID()}"

    # Ask for index in results
    while True:
        input_str = input(f"Enter number from 1 to {len(people)}: ")

        try:
            input_val = int(input_str)
        except ValueError:
            print("Please enter a number.")
            continue

        if input_val < 1 or input_val > len(people):
            print(f"Please enter a number from 1 to {len(people)}.")
            continue

        break

    # Remember: we asked for a 1-based index, and we need a 0-based index
    return f"nm{people[input_val - 1].getID()}"


def main():
    # Load actor/movie data from custom JSON files
    # Actor names + title names + associations courtesy of IMDb
    # (http://www.imdb.com).
    # Used with permission.
    print("Loading actors...")
    with open(path.join(FILEDIR, "actors.json"), encoding="utf-8") as f:
        all_actors: dict[str, dict[str, Any]] = json.load(f)
    print("Loading movies...")
    with open(path.join(FILEDIR, "movies.json"), encoding="utf-8") as f:
        all_movies: dict[str, dict[str, Any]] = json.load(f)
    print("Done loading.")


    def bacon_bfs(
        dest_actor: Optional[str] = None,
        src_actor: str = KEVIN_BACON_ID,
        dists_only: bool = False,
        max_dist: Optional[int] = None,
        debug: bool = False
    ) -> dict[str, ConnectionInfo]:
        """
        Search for path(s) outward from `src_actor` using a
        breadth-first search.

        Parameters
        ----------
        dest_actor : str, optional
            Actor ID of final actor in desired path(s).
        src_actor : str, default "nm0000102", meaning Kevin Bacon
            Actor ID of initial actor in desired path(s).
        dists_only : bool
            If true, only the distances to `src_actor` are stored.
        max_dist : int, optional
            Maximum distance from `src_actor` to search for.
        debug : bool
            If true, outputs debug information while searching.

        Returns
        -------
        dict of {str : ConnectionInfo}
            Mapping from actor ID to relevant info about the shortest
            path(s) to that actor from `src_actor`.
        """
        queue = Queue()
        edges: dict[str, ConnectionInfo] = {}

        debug_iters: int = 0

        done_searching: bool = False
        # Start searching from the source actor
        queue.enqueue(src_actor)
        edges[src_actor] = {
            "dist": 0,
            "preds": defaultdict(set)
        }
        while queue:
            if debug:
                if debug_iters == 0:
                    print(f"Left: {len(queue)}", end=" \r")

                debug_iters = (debug_iters + 1) % BFS_PROGRESS_FREQ

            actor = queue.dequeue()

            # Don't search this actor if they're not in our database
            if actor not in all_actors:
                continue

            # Search all movies from this actor
            movies = all_actors[actor]["filmography"]
            for movie in movies:
                # Don't search this movie if it's not in our database
                if movie not in all_movies:
                    continue

                # Add all costars to our actor queue
                cast = all_movies[movie]["cast"]
                for costar in cast:
                    # Don't search this costar if they're not in our database
                    if costar not in all_actors:
                        continue

                    # If this costar hasn't been found
                    if costar not in edges:
                        # Enqueue them
                        queue.enqueue(costar)
                        # Add them to our connections
                        edges[costar] = {
                            "dist": edges[actor]["dist"] + 1,
                            "preds": defaultdict(set)
                        }

                    # If we care about finding paths,
                    # and actor is part of short path from src_actor to costar
                    if not dists_only and (
                        edges[actor]["dist"] < edges[costar]["dist"]
                    ):
                        # Add this connection (and this movie)
                        edges[costar]["preds"][actor].add(movie)

                    # If we've found a path to dest_actor
                    if max_dist is None and (
                        dest_actor is not None and costar == dest_actor
                    ):
                        # Keep searching up to the dist of the previous actor
                        max_dist = edges[actor]["dist"]

                    # If we've reached a maximum distance
                    if (
                        max_dist is not None
                        and edges[costar]["dist"] > max_dist
                    ):
                        # Quit early
                        done_searching = True
                        queue.clear()
                        break

                if done_searching:
                    break

        # If done searching, and we want full paths
        if done_searching and dest_actor is not None:
            # Find all connections from the destination actor to all
            # previously found actors
            dest_actor_dist = edges[dest_actor]["dist"]
            for movie in all_actors[dest_actor]["filmography"]:
                for costar in all_movies[movie]["cast"]:
                    if costar not in all_actors:
                        continue

                    if costar not in edges:
                        continue

                    # Add this connection if it also forms a shortest path
                    if not dists_only and (
                        edges[costar]["dist"] < dest_actor_dist
                    ):
                        edges[dest_actor]["preds"][costar].add(movie)

        if debug:
            print("Done searching.")

        return edges


    def get_all_paths(
        edges: dict[str, ConnectionInfo],
        dest: str
    ) -> list[list[PredecessorInfo]]:
        """
        Recursively gather all paths from the source actor used to
        generate `edges` to another actor.

        Parameters
        ----------
        edges : dict of {str : ConnectionInfo}
            Edges generated with `bacon_bfs`.
        dest : str
            Actor ID to find all paths to.

        See Also
        --------
        bacon_bfs : Generate the `edges` using a breadth-first search.
        """
        paths: list[list[PredecessorInfo]] = []

        # If actor is not in edges, there is no path
        if dest not in edges:
            return paths

        # If actor has distance 0, the only path is the empty path
        if edges[dest]["dist"] == 0:
            paths.append([])
            return paths

        for pred, movies in edges[dest]["preds"].items():
            current_pred: PredecessorInfo = {
                "actor": pred,
                "movies": movies
            }

            # Ironically, this uses a DFS to find all the paths,
            # which we generated using a BFS
            for p in get_all_paths(edges, pred):
                paths.append([current_pred] + p)

        return paths


    def find_link_from_a_to_b():
        while True:
            dest = input_actor(prompt="Enter starting actor "
                "(blank for Kevin Bacon): ")
            print()

            if dest in all_actors:
                break

            print("The requested actor is not in the database.")
            print("Please try again.")
            print()

        while True:
            src = input_actor(prompt="Enter ending actor "
                "(blank for Kevin Bacon): ")
            print()

            if src in all_actors:
                break

            print("The source actor is not in the database.")
            print("Please try again.")
            print()

        dest_name = all_actors[dest]["name"]
        src_name = all_actors[src]["name"]

        bacon_edges = bacon_bfs(dest, src)

        try:
            bacon_edge: ConnectionInfo = bacon_edges[dest]
        except KeyError:
            # If path doesn't exist, tell the user
            print()
            print(f"{dest_name} has a {src_name} number of infinity.")
            print()
            print("Either the database isn't complete enough to find a link,")
            print("or the link doesn't exist.")
            print("Please try again.")
            print()
        else:
            # If path exists, find and display it
            all_paths = get_all_paths(bacon_edges, dest)
            displaying_paths: bool = True

            while displaying_paths:
                print()
                print(f"{dest_name} has a {src_name} number of "
                    f"{bacon_edge['dist']}.")
                print()

                # Prepare to output a random path
                example_path = random.choice(all_paths)
                output_lines: list[tuple[str, str]] = []
                for i, edge in enumerate(example_path):
                    who = dest_name if i == 0 else "who"

                    person = edge["actor"]
                    title = random.choice(list(edge["movies"]))

                    movie = all_movies[title]["name"]
                    actor = all_actors[person]["name"]
                    punct = "." if i == len(example_path) - 1 else ","

                    output_lines.append((
                        # Human readable sentence
                        f"{who} was in {movie} with {actor}{punct}",
                        # Movie/actor IDs
                        f"{title} -> {person}"
                    ))

                # Output each line in two neat columns separated by a tab
                max_output_len = max(len(line[0]) for line in output_lines)
                for line in output_lines:
                    print(f"{{0:{max_output_len}}}\t{{1}}".format(*line))
                print()

                # Count the number of shortest paths in total
                total_paths = len(all_paths)
                total_paths_with_movies = sum(
                    len(edge["movies"]) - 1 for p in all_paths for edge in p
                ) + total_paths
                print(f"The total number of shortest-paths is {total_paths} "
                    f"({total_paths_with_movies} including different movies).")
                print()

                # Ask the user to display another shortest path
                while True:
                    input_char = input(
                        "Display another shortest-path? (Y/N) "
                    )
                    if input_char:
                        input_char = input_char[0].lower()

                    match input_char:
                        case "y":
                            break
                        case "n":
                            displaying_paths = False
                            break
                        case _:
                            print("Enter Y or N.")
                            continue

            print()


    def find_all_links_from_a():
        while True:
            src = input_actor(prompt="Enter actor "
                "(blank for Kevin Bacon): ")
            print()

            if src in all_actors:
                break

            print("The actor is not in the database.")
            print("Please try again.")
            print()

        bacon_edges = bacon_bfs(
            src_actor=src,
            dists_only=True, debug=True
        )

        # Count all actors with certain numbers, and get their average
        bacon_ranks: defaultdict[int, int] = defaultdict(int)
        bacon_sum: float = 0
        for _, info in bacon_edges.items():
            bacon_ranks[info["dist"]] += 1
            bacon_sum += info["dist"]

        excluded_actors: int = len([
            a for a in all_actors if a not in bacon_edges
        ])

        # Print results
        print("#\tActors")
        for rank, num in sorted(bacon_ranks.items()):
            print(f"{rank}\t{num}")
        print(f"Inf\t{excluded_actors}")
        print()

        print(f"Average: {bacon_sum / len(bacon_edges)}")
        print()


    def find_all_links_n_away_from_a():
        while True:
            src = input_actor(prompt="Enter actor "
                "(blank for Kevin Bacon): ")
            print()

            if src in all_actors:
                break

            print("The actor is not in the database.")
            print("Please try again.")
            print()

        src_name = all_actors[src]["name"]

        dist: Optional[int]
        while True:
            input_str = input("Enter positive number "
                "(blank for infinity): ").strip()

            if not input_str:
                dist = None
                break

            try:
                dist = int(input_str)
            except ValueError:
                print("Please enter a number.")
                continue
            else:
                if dist < 0:
                    print("Please enter a positive number.")
                    continue
                print()
                break

        bacon_edges = bacon_bfs(
            src_actor=src,
            dists_only=True, max_dist=dist,
            debug=True
        )

        actors_at_dist: list[str]
        if dist is None:
            actors_at_dist = [
                a for a in all_actors
                if a not in bacon_edges
            ]
        else:
            actors_at_dist = [
                a for a, info in bacon_edges.items()
                if info["dist"] == dist
            ]

        print((f"There are {len(actors_at_dist)} actors "
            if len(actors_at_dist) != 1
            else "There is 1 actor "
            ) + f"with a {src_name} number of "
            + ("infinity." if dist is None else f"{dist}."))

        # If there are no actors to print, return
        if not actors_at_dist:
            return

        # If there are too many actors to print, warn the user
        if len(actors_at_dist) > MAX_ACTOR_DIST_RESULTS:
            print("There are too many to list, so here's a random sample of "
                f"{MAX_ACTOR_DIST_RESULTS} of them.")

        # Print random sample of actors, weighted by number of films they're in
        print()
        for actor in weighted_sample_without_replacement(
            actors_at_dist,
            k=MAX_ACTOR_DIST_RESULTS,
            weights=[len(all_actors[a]["filmography"]) for a in actors_at_dist]
        ):
            print(f"{all_actors[actor]['name']} [{actor}]")
        print()


    # Main loop
    while True:
        print("1\tWhat is the link between actor A and actor B?")
        print('2\tHow good of a "center" is actor A?')
        print("3\tWho are all the people with an actor A number of N?")
        print("4\tExit")
        print()

        input_str = input("Enter choice from 1 to 4: ")

        try:
            input_val = int(input_str)
        except ValueError:
            print("Please enter a number.")
            continue

        match input_val:
            case 1:
                find_link_from_a_to_b()
            case 2:
                find_all_links_from_a()
            case 3:
                find_all_links_n_away_from_a()
            case 4:
                break
            case _:
                print("Please enter a choice from 1 to 4.")
                continue


if __name__ == "__main__":
    main()
