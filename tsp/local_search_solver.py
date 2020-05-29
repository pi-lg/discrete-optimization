from typing import List, Set, Tuple
from utils import Point
import numpy as np
import random
from collections import namedtuple
from llist import dllist
import multiprocessing as mp
import sys

DistanceTo = namedtuple("DistanceTo", ["index", "distance"])


def choose_close_unused_vertex(ordered_distances: List[DistanceTo], distances_to_point: np.array,
                               current_distance: float, entropy: float = 0.0, vertices_not_to_choose: Set[int] = set()
                               ) -> Tuple[int, float]:
    # if len(ordered_distances) > len(vertices_not_to_choose):
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
                    # print("point %i is available" % point.index)
                    return point.index, point.distance
    # else:
    #     raise Exception("No more Points to")


# TODO: Adjust swapping once path is a dllist
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


def compute_distances(start: int, dim: int, points: List[Point]) -> np.array:
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


def solve(points: List[Point], prop_of_closest_neighbors_to_store: float = 0.05, min_num_neighbors: int = 20,
          max_num_neighbors: int = 100, prop_long_path_exploration: float = 0.2,
          prop_of_edges_to_sample_to_find_long_path: float = 0.05) -> Tuple[List[int], float, List[float]]:
    dim = len(points)
    print("number of points is: %i" % dim)
    sys.stdout.flush()
    pool = mp.Pool(mp.cpu_count())
    distances = [pool.apply(compute_distances, args=(start, dim, points)) for start in range(dim - 1)]
    pool.close()
    # distance_matrix = np.zeros((dim, dim))
    # for i in range(dim):
    #     for j in range(i + 1, dim):
    #         d = compute_distance(points[i], points[j])
    #         distance_matrix[i, j] = d
    #         distance_matrix[j, i] = d
    # print("Distance MATRIX computed.")
    # sys.stdout.flush()

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
        neighbors[i] = n
    print("neighbors computed.")
    sys.stdout.flush()

    path = list(range(dim))
    best_path = path.copy()
    distance_path = sum([get_distance(path[i], path[i+1], distances) for i in range(dim-1)]
                        + [get_distance(path[dim-1], path[0], distances)])
    distance_best_path = distance_path
    best_distances = [distance_best_path]
    improvement_counter = 0
    counter = 0

    # while improvement_counter < 1000000:
    while improvement_counter < 1000:
        counter += 1
        # if improvement_counter != 0 and improvement_counter % 1000 == 0:
        #     print("improvement_counter = %i" % improvement_counter)
        if counter % 1000 == 0:
            best_distances.append(distance_best_path)
        improvement_counter += 1
        # restart with best path so far
        path = best_path.copy()
        distance_path = distance_best_path
        # choose starting vertex
        if random.random() < prop_long_path_exploration:
            start, long_path_distance = (0, 0.0)
            # sample_indices = sorted(
            #     random.choices(range(dim), k=round(dim * prop_of_edges_to_sample_to_find_long_path)))
            # for i in sample_indices:
            for i in range(dim):
                if random.random() < prop_of_edges_to_sample_to_find_long_path:
                    distance = get_distance(path[i], path[i + 1 if i < (dim - 1) else 0], distances)
                    if distance > long_path_distance:
                        start = i
                        long_path_distance = distance
        else:
            start = np.random.randint(dim)
        # print("dim = %d, start = %d" % (dim, start))
        # rearrange path so start is the start of the cycle
        # TODO: Make path dllist and adjust rotation
        path = path[start:] + path[:start]
        # print("length of path = %d" % len(path))
        position_of_next = 1
        _next = path[position_of_next]
        used_vertices = set()
        used_vertices.add(_next)
        for _ in range(100000):
            # print(closest_points[_next])
            # print("---------------------------------")
            close_to_next, distance = choose_close_unused_vertex(
                neighbors[_next],
                distances_to_point=get_distances_to_point(_next, distances),
                current_distance=get_distance(path[0], _next, distances),
                entropy=0.8,
                vertices_not_to_choose=used_vertices
            )
            # print("_next = %i, close_to_next = %i" % (_next, close_to_next))
            position_of_freed_up_element = path.index(close_to_next) - 1
            if close_to_next == path[0] or position_of_freed_up_element == position_of_next:
                break
            distance_path -= get_distance(path[0], _next, distances)
            distance_path += get_distance(_next, close_to_next, distances)
            freed_up_element = path[position_of_freed_up_element]
            distance_path -= get_distance(path[position_of_freed_up_element], close_to_next, distances)
            distance_path += get_distance(path[0], path[position_of_freed_up_element], distances)
            path = swap_elements(path, position_of_next, position_of_freed_up_element)
            if distance_path < distance_best_path:
                distance_best_path = distance_path
                # print("New best distance found: %.2f" % distance_best_path)
                best_path = path.copy()
                if counter % 100 == 0:
                    print("New best path distance: %.2f" % distance_best_path)
                    sys.stdout.flush()
                improvement_counter = 0
            used_vertices.add(close_to_next)
            used_vertices.add(freed_up_element)
            _next = freed_up_element
            # position_of_next = position_of_freed_up_element
        # TODO introduce second stage where long vertices are eliminated?

    return best_path, distance_best_path, best_distances





