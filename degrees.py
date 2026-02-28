import csv
import sys

from util import Node, StackFrontier, QueueFrontier
from dataclasses import dataclass
from typing import Tuple, FrozenSet
from collections import deque

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}

# Define a simple (movie_id, actor_id) pair
@dataclass(frozen=True)
class MovieActor:
    movie_id: int
    actor_id: int


# Define the main object that will go inside a Python set
@dataclass(frozen=True)
class Node:
    depth: int
    obj: MovieActor
    list_of_objects: Tuple[MovieActor, ...]   # immutable instead of list
    set_of_actor_ids: FrozenSet[int]          # immutable instead of set

def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")



    # maintain a set for each depth
    # each object in the set will have the current (movie, actor) pair
    # the consolidated set of movie, actor beginning from root. so depth 0 will have 1 item, depth 1 will have 2 items etc
    # list of actor ids from source. if the new actor id is target we reached a solution and return the consolidated set
    # if the new actor id exists in the list of actor ids then we reached a cyclic solution . we need to try the next item in the
    # level. if we exaust all items in the level and they are open we move on to next depth
    # advantages of breath first here is any solution reached is optimum

    # create a depth 0 set of nodes from the neighbors of person returned

    # replace set with deque because the q is used only one time


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.
    If no possible path, returns None.
    """
    source_id = person_id_for_name(source)
    target_id = person_id_for_name(target)

    # BFS queue
    queue = deque()

    # Initial node
    node_source = Node(
        depth=0,
        obj=None,
        list_of_objects=[],
        set_of_actor_ids=frozenset({source_id})
    )
    queue.append(node_source)

    while queue:
        current_node = queue.popleft()
        current_depth = current_node.depth
        current_actor_id = list(current_node.set_of_actor_ids)[-1]  # last actor in path

        for neighbor in neighbors_for_person(current_actor_id):
            movie_id, person_id = neighbor

            # Avoid cycles
            if person_id in current_node.set_of_actor_ids:
                continue

            # Build new node
            new_node = Node(
                depth=current_depth + 1,
                obj=neighbor,
                list_of_objects=current_node.list_of_objects + [neighbor],
                set_of_actor_ids=current_node.set_of_actor_ids.union({person_id})
            )

            # If we reached target, return path
            if person_id == target_id:
                return new_node.list_of_objects

            queue.append(new_node)

    # No path found
    return None


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors



if __name__ == "__main__":
    main()
