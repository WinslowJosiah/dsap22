# sys.path hack for custom module import
import sys
import os.path as path
sys.path.insert(0, path.join(path.dirname(path.abspath(__file__)), r"..\.."))

import gzip
import json
import re
import requests
from configparser import ConfigParser
from datetime import date
from imdb import Cinemagoer, IMDbError  # type: ignore
from typing import Any, Literal, Optional, TypedDict, get_args, overload

FILEDIR = path.dirname(path.abspath(__file__))

IMDB_DATA_URL = r"https://datasets.imdbws.com/{0}.tsv.gz"
ALL_MOVIE_CATEGORIES = {
    "movie", "short", "video", "tvMovie", "tvShort", "tvSpecial",
    "tvSeries", "tvMiniSeries", "tvPilot", "tvEpisode", "videoGame",
}

CONFIG_PATH = path.join(FILEDIR, "imdb.ini")
CONFIG_DEFAULT = {
    "Categories": {
        "movie_categories": "movie, short",
        "actor_categories": "actor, actress, self",
    },
    "MissingInfo": {
        "movies_to_revisit": "",
        "actors_to_revisit": "",
    },
    "Options": {
        "redownload_if_older": "yes",
    },
}
# Sanity check for movie categories
assert all(
    c.strip() in ALL_MOVIE_CATEGORIES
    for c in CONFIG_DEFAULT["Categories"]["movie_categories"].split(",")
)


# Helper classes for type hints
class MovieInfo(TypedDict):
    name: str
    cast: set[str]


class ActorInfo(TypedDict):
    name: str
    filmography: set[str]


IMDbDataset = Literal["title.basics", "name.basics", "title.principals"]
# These constants depend on the IMDbDataset type hint
MOVIE_INFO, ACTOR_INFO, ROLE_INFO = get_args(IMDbDataset)


# JSON serializer class to handle cast and filmography sets
class SetEncoder(json.JSONEncoder):
    @overload
    def default(self, o: set[Any]) -> list[Any]:
        ...

    @overload
    def default(self, o: Any) -> Any:
        ...

    def default(self, o: set[Any] | Any) -> list[Any] | Any:
        # Turn sets into lists
        if isinstance(o, set):
            return list(o)
        return super().default(o)


def cg_movie_category(title: Any) -> str:
    """
    Get the proper IMDb movie category for a Cinemagoer Movie object.

    Parameters
    ----------
    title : imdb.Movie.Movie
        Cinemagoer Movie object.

    Returns
    -------
    str
        IMDb movie category for `title`.
    """
    # I need to convert Cinemagoer's "kind" information
    # to a proper movie category

    match title["kind"]:
        case "movie":
            # This is the most complicated case, because
            # movies, shorts, and TV specials are lumped together
            cg: Any = Cinemagoer()

            # If tv-special is in the keywords, it's a TV special
            cg.update(title, "keywords")
            if "tv-special" in title.get("keywords", []):
                return "tvSpecial"

            # If short is in the genres, it's a short
            if "Short" in title.get("genres", []):
                return "short"

            # Otherwise, it's a movie
            return "movie"
        case "video movie":
            return "video"
        case "tv movie":
            return "tvMovie"
        case "tv short":
            return "tvShort"
        case "tv series":
            return "tvSeries"
        case "tv mini series":
            return "tvMiniSeries"
        case "tv pilot":
            return "tvPilot"
        case "episode":
            return "tvEpisode"
        case "video game":
            return "videoGame"
        case kind:
            raise ValueError(f"Unexpected value of Cinemagoer kind: {kind}")


def download_dataset(name: IMDbDataset):
    """
    Download an IMDb dataset and save it as a .tsv file.

    Parameters
    ----------
    name : str
        Name of the dataset.
    """
    dataset_file = path.join(FILEDIR, f"{name}.tsv")
    # File must be decompressed from .tsv.gz to .tsv
    r = requests.get(IMDB_DATA_URL.format(name))
    with open(dataset_file, "wb") as f_out:
        f_out.write(gzip.decompress(r.content))


def main():
    config: ConfigParser = ConfigParser()

    config_file_exists: bool = False
    print("Finding config file...")
    # If config file was found
    if path.isfile(CONFIG_PATH):
        # Attempt to read config file
        print("Config file found. Reading...")
        config_file_exists = True
        config.read(CONFIG_PATH)
    # If config file was not found
    else:
        # Create with default settings
        print("Config file does not exist. "
            "Creating with default settings...")

    # Populate config with default info for each section if missing
    if "Categories" not in config:
        print("Creating missing [Categories] section...")
        config["Categories"] = CONFIG_DEFAULT["Categories"]
    if "MissingInfo" not in config:
        print("Creating missing [MissingInfo] section...")
        config["MissingInfo"] = CONFIG_DEFAULT["MissingInfo"]
    if "Options" not in config:
        print("Creating missing [Options] section...")
        config["Options"] = CONFIG_DEFAULT["Options"]

    # Write file with default info if file doesn't exist
    if not config_file_exists:
        with open(CONFIG_PATH, "w") as f:
            config.write(f)

    # Use info from config to set up accepted categories
    categories = config["Categories"]
    categories_default = CONFIG_DEFAULT["Categories"]
    movie_categories: set[str] = {
        c.strip()
        for c in categories.get(
            "movie_categories",
            fallback=categories_default["movie_categories"]
        ).split(",")
    }
    actor_categories: set[str] = {
        c.strip()
        for c in categories.get(
            "actor_categories",
            fallback=categories_default["actor_categories"]
        ).split(",")
    }
    # Sanity check for movie categories
    for category in movie_categories:
        if category not in ALL_MOVIE_CATEGORIES:
            print(f"WARNING: {category} is not a valid movie category")

    # Check if we need to redownload the .tsv data files
    options = config["Options"]
    options_default = CONFIG_DEFAULT["Options"]
    should_redownload: bool = False
    redownload_reason: Optional[str] = None
    skipped_redownload_if_older: bool = False
    for dataset in [MOVIE_INFO, ACTOR_INFO, ROLE_INFO]:
        dataset_path: str = path.join(FILEDIR, f"{dataset}.tsv")

        # If file doesn't exist, we must redownload
        if not path.isfile(dataset_path):
            should_redownload = True
            redownload_reason = f"{dataset}.tsv doesn't exist"
            break

        # If file is older than today, we may need to redownload
        if date.fromtimestamp(path.getmtime(dataset_path)) < date.today():
            # Don't redownload if we've specified we don't want to
            if not options.getboolean(
                "redownload_if_older",
                fallback=options_default["redownload_if_older"]
            ):
                skipped_redownload_if_older = True
                break

            should_redownload = True
            redownload_reason = f"{dataset}.tsv older than today"
            break

    # Redownload the files if we need to
    if should_redownload:
        print("The relevant IMDb datasets should be redownloaded.")
        print(f"Reason: {redownload_reason}")

        for dataset in [MOVIE_INFO, ACTOR_INFO, ROLE_INFO]:
            print(f"Redownloading {dataset}.tsv...")
            download_dataset(dataset)

        print("Done redownloading datasets.")
    # Skip redownloading if we don't need to and don't want to
    elif skipped_redownload_if_older:
        print("Skipped redownload of old IMDb datasets.")

    movies: dict[str, MovieInfo] = {}
    actors: dict[str, ActorInfo] = {}

    # Load movies with names
    print("Processing movies...")
    with open(path.join(FILEDIR, f"{MOVIE_INFO}.tsv"), encoding="utf-8") as f:
        f.readline()  # Skip header
        for line in f:
            row = line.split("\t")

            if row[1] not in movie_categories:
                continue

            movies[row[0]] = {
                "name": row[2],
                "cast": set(),
            }

    # Load actors with names
    print("Processing actors...")
    with open(path.join(FILEDIR, f"{ACTOR_INFO}.tsv"), encoding="utf-8") as f:
        f.readline()  # Skip header
        for line in f:
            row = line.split("\t")

            jobs = row[4].split(",")
            if not any(job in actor_categories for job in jobs):
                continue

            actors[row[0]] = {
                "name": row[1],
                "filmography": set(),
            }

    # Load roles with movies and actors
    print("Processing connections...")
    with open(path.join(FILEDIR, f"{ROLE_INFO}.tsv"), encoding="utf-8") as f:
        f.readline()  # Skip header
        for line in f:
            row = line.split("\t")

            movie = row[0]
            if movie not in movies:
                continue
            actor = row[2]
            if actor not in actors:
                continue

            if row[3] not in actor_categories:
                continue

            movies[movie]["cast"].add(actor)
            actors[actor]["filmography"].add(movie)

    # Load auxillary movies and actors, if any
    missing_info = config["MissingInfo"]
    missing_info_default = CONFIG_DEFAULT["MissingInfo"]
    movies_to_revisit: set[str] = {
        v.strip()
        for v in missing_info.get(
            "movies_to_revisit",
            fallback=missing_info_default["movies_to_revisit"]
        ).split(",")
    }
    actors_to_revisit: set[str] = {
        v.strip()
        for v in missing_info.get(
            "actors_to_revisit",
            fallback=missing_info_default["actors_to_revisit"]
        ).split(",")
    }
    cg: Any = Cinemagoer()

    # Revisit auxillary movies, if any
    if movies_to_revisit:
        print("Revisiting some movies...")
    for movie in movies_to_revisit:
        # Check if movie ID is valid
        m = re.fullmatch(r"(?:tt)?(\d+)", movie)
        if not m:
            continue

        # Use movie ID to search for info
        movie_id: str = m.group(1)
        try:
            title = cg.get_movie(movie_id)
            cg.update(title, "full credits")
        except IMDbError:
            print(f"Error getting data for movie with ID tt{movie_id}.")
            continue

        # Create movie entry if not in list
        movie_id_full: str = f"tt{title.getID()}"
        if movie_id_full not in movies:
            # Filter movie based on movie_categories
            if cg_movie_category(title) not in movie_categories:
                print(f"WARNING: Movie with ID {movie_id_full} "
                    "not of accepted category")
                continue

            movies[movie_id_full] = {
                "name": title["title"],
                "cast": set(),
            }

        # Update movie info
        for person in title.get("cast", []):
            actor_id_full: str = f"nm{person.getID()}"
            if actor_id_full not in actors:
                # TODO: filter person based on actor_categories

                actors[actor_id_full] = {
                    "name": person["name"],
                    "filmography": set()
                }

            movies[movie_id_full]["cast"].add(actor_id_full)
            actors[actor_id_full]["filmography"].add(movie_id_full)

    # Revisit auxillary actors, if any
    if actors_to_revisit:
        print("Revisiting some actors...")
    for actor in actors_to_revisit:
        # Check if actor ID is valid
        m = re.fullmatch(r"(?:nm)?(\d+)", actor)
        if not m:
            continue

        # Use actor ID to search for info
        actor_id: str = m.group(1)
        try:
            person = cg.get_person(actor_id)
        except IMDbError:
            print(f"Error getting data for actor with ID nm{actor_id}.")
            continue

        # Create actor entry if not in list
        actor_id_full: str = f"nm{person.getID()}"
        if actor_id_full not in actors:
            # No need to filter based on actor categories,
            # because we'll be looping through them directly
            actors[actor_id_full] = {
                "name": person["name"],
                "filmography": set()
            }

        # Update actor info
        for category in actor_categories:
            for title in person["filmography"].get(category, []):
                movie_id_full: str = f"tt{title.getID()}"
                if movie_id_full not in movies:
                    # Filter movie based on movie categories
                    if cg_movie_category(title) not in movie_categories:
                        continue

                    movies[movie_id_full] = {
                        "name": title["title"],
                        "cast": set(),
                    }

                actors[actor_id_full]["filmography"].add(movie_id_full)
                movies[movie_id_full]["cast"].add(actor_id_full)

    # Remove movies and actors without connections
    print("Removing movies without cast list...")
    for movie in [k for k, v in movies.items() if not v["cast"]]:
        del movies[movie]
    print("Removing actors without filmography...")
    for actor in [k for k, v in actors.items() if not v["filmography"]]:
        del actors[actor]

    print(f"Compiled info for {len(actors)} actors and {len(movies)} movies.")

    # Write processed .json files (this takes a while)
    print("Writing movies.json...")
    with open(path.join(FILEDIR, "movies.json"), "w", encoding="utf-8") as f:
        json.dump(movies, f, cls=SetEncoder)
    print("Writing actors.json...")
    with open(path.join(FILEDIR, "actors.json"), "w", encoding="utf-8") as f:
        json.dump(actors, f, cls=SetEncoder)

    print("Done.")


if __name__ == "__main__":
    main()
