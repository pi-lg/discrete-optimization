from typing import List, Set, Tuple
from utils import Point
import numpy as np
import random
from collections import namedtuple
from llist import dllist
import multiprocessing as mp
import sys
# TODO: remove below dependencies after testing
import os
import pickle

DistanceTo = namedtuple("DistanceTo", ["index", "distance"])


def choose_close_unused_vertex(ordered_distances: List[DistanceTo], distances_to_point: np.array,
                               current_distance: float, entropy: float = 0.0, vertices_not_to_choose: Set[int] = set()
                               ) -> Tuple[int, float]:
    available_points = set(
        [point.index for point in ordered_distances if point.distance <= current_distance]
    ).difference(vertices_not_to_choose)
    if not available_points:
        index_of_closest, distance_of_closest = (-1, current_distance)
        for index, distance in enumerate(distances_to_point):
            if distance <= distance_of_closest and index not in vertices_not_to_choose:
                index_of_closest = index
                distance_of_closest = distance
        return index_of_closest, distance_of_closest
    else:
        while True:
            for point in ordered_distances:
                if point.distance > current_distance:
                    break
                elif random.random() >= entropy and point.index not in vertices_not_to_choose:
                    return point.index, point.distance


def swap_elements(path: List[int], position_of_next: int, position_of_freed_up_element: int) -> List[int]:
    if position_of_next >= position_of_freed_up_element:
        raise Exception("First element %d is not smaller in position than second element %d"
                        % (position_of_next, position_of_freed_up_element))
    path = path[:position_of_next] + [path[position_of_freed_up_element]] \
        + list(reversed(path[position_of_next+1:position_of_freed_up_element])) \
        + [path[position_of_next]] + path[position_of_freed_up_element+1:]
    return path


def compute_distance(i: Point, j: Point):
    return np.sqrt((i.x - j.x)**2 + (i.y - j.y)**2)


def compute_distances_to_point(start: int, dim: int, points: List[Point]) -> np.array:
    distances = np.zeros(dim - (start + 1))
    for later_point in range(start + 1, dim):
        distances[later_point - (start + 1)] = compute_distance(points[start], points[later_point])
    return distances


def get_distance(i: int, j: int, distances: List[np.array]) -> float:
    sorted_indices = sorted([i, j])
    return distances[sorted_indices[0]][sorted_indices[1] - (sorted_indices[0] + 1)]


def get_distances_to_point(index: int, distances: List[np.array]) -> np.array:
    array = np.array([get_distance(index, j, distances) for j in range(index)] + [0.0])
    if index == len(distances):
        return array
    else:
        return np.concatenate((array, distances[index]))


def run_with_random_start(distances, neighbors, prop_long_path_exploration,
                          prop_of_edges_to_sample_to_find_long_path, num_iterations_per_exploration, start_path=None):
    dim = len(distances) + 1
    if not start_path:
        start_path = list(np.random.permutation(dim))
    best_path = start_path.copy()
    distance_path = sum([get_distance(start_path[i], start_path[i + 1], distances) for i in range(dim - 1)]
                        + [get_distance(start_path[dim - 1], start_path[0], distances)])
    distance_best_path = distance_path

    for i in range(num_iterations_per_exploration):
        # restart with best path so far
        start_path = best_path.copy()
        distance_path = distance_best_path
        # choose starting vertex
        if random.random() < prop_long_path_exploration:
            start, long_path_distance = (0, 0.0)
            sample_indices = random.choices(range(dim), k=round(dim * prop_of_edges_to_sample_to_find_long_path))
            for j in sample_indices:
                distance = get_distance(start_path[j], start_path[j + 1 if j + 1 < dim else 0], distances)
                if distance > long_path_distance:
                    start = j
                    long_path_distance = distance
        else:
            start = np.random.randint(dim)
        # rearrange path so start is the start of the cycle
        start_path = start_path[start:] + start_path[:start]
        position_of_next = 1
        _next = start_path[position_of_next]
        used_vertices = set()
        used_vertices.add(_next)
        for _ in range(dim):
            close_to_next, distance = choose_close_unused_vertex(
                neighbors[_next],
                distances_to_point=get_distances_to_point(_next, distances),
                current_distance=get_distance(start_path[0], _next, distances),
                entropy=0.8,
                vertices_not_to_choose=used_vertices
            )
            position_of_freed_up_element = start_path.index(close_to_next) - 1
            if close_to_next == start_path[0] or position_of_freed_up_element == position_of_next:
                break
            distance_path -= get_distance(start_path[0], _next, distances)
            distance_path += get_distance(_next, close_to_next, distances)
            freed_up_element = start_path[position_of_freed_up_element]
            distance_path -= get_distance(start_path[position_of_freed_up_element], close_to_next, distances)
            distance_path += get_distance(start_path[0], start_path[position_of_freed_up_element], distances)
            start_path = swap_elements(start_path, position_of_next, position_of_freed_up_element)
            if distance_path < distance_best_path:
                distance_best_path = distance_path
                best_path = start_path.copy()
                improvement_counter = 0
            used_vertices.add(close_to_next)
            used_vertices.add(freed_up_element)
            _next = freed_up_element

    return best_path, distance_best_path


# TODO: Code version which computes distances on the fly using List[Point] object when number of points is big
def solve(points: List[Point], prop_of_closest_neighbors_to_store: float = 0.05, min_num_neighbors: int = 20,
          max_num_neighbors: int = 500, prop_long_path_exploration: float = 0.8,
          prop_of_edges_to_sample_to_find_long_path: float = 0.1, num_iterations_per_exploration: int = 20000,
          num_explorations=None
          ) -> Tuple[List[int], float, List[float]]:
    dim = len(points)
    # print("number of points is: %i" % dim)
    # print("coordinates of first point: x = %i, y = %i" % (points[0].x, points[0].y))
    # sys.stdout.flush()
    # file_name_distances_object = '_'.join(["distances", fn, ".Pickle"])
    # if os.path.isfile(file_name_distances_object):
    #     with open(file_name_distances_object, 'rb') as f:
    #         distances = pickle.load(f)
    # else:
    pool = mp.Pool(mp.cpu_count())
    distances = [pool.apply(compute_distances_to_point, args=(start, dim, points)) for start in range(dim - 1)]
    pool.close()
        # with open(file_name_distances_object, 'wb') as f:
        #     pickle.dump(distances, f)

    num_neighbors_to_store = min(max_num_neighbors,
                                 max(min_num_neighbors, round(prop_of_closest_neighbors_to_store * dim)))
    neighbors = [None for i in range(dim)]
    for i in range(dim):
        n = dllist()
        for index, distance in enumerate(get_distances_to_point(i, distances)):
            if index == i:
                continue
            elif n.size == 0:
                n.append(DistanceTo(index, distance))
            elif n.last.value.distance > distance:
                node = n.first
                while node.value.distance <= distance:
                    node = node.next
                n.insert(DistanceTo(index, distance), node)
                if n.size > num_neighbors_to_store:
                    n.popright()
        neighbors[i] = list(n)
    # print("neighbors computed.")
    # sys.stdout.flush()

    # path = list(range(dim))
    args = (
        distances,
        neighbors,
        prop_long_path_exploration,
        prop_of_edges_to_sample_to_find_long_path,
        num_iterations_per_exploration
    )

    # print("Starting the exploration.")
    # sys.stdout.flush()
    pool = mp.Pool(mp.cpu_count())
    results = []

    def populate_results(result):
        results.append(result)

    if not num_explorations:
        num_explorations = 4 * mp.cpu_count()
    for i in range(num_explorations):
        r = pool.apply_async(run_with_random_start, args, callback=populate_results)
    pool.close()
    pool.join()
    best_distance, best_path = (float('inf'), None)
    for result in results:
        if result[1] < best_distance:
            best_distance = result[1]
            best_path = result[0]
    # print("Exploration is done. Best path distance found = %.2f" % best_distance)
    # sys.stdout.flush()
    best_path, best_distance = run_with_random_start(distances, neighbors, prop_long_path_exploration,
                                                     prop_of_edges_to_sample_to_find_long_path, 5000, best_path)

    return best_path, best_distance







