from typing import List, Set, Tuple
from utils import Point
import numpy as np
import random
from collections import namedtuple

DistanceTo = namedtuple("DistanceTo", ["index", "distance"])


def choose_close_unused_vertex(ordered_distances: List[DistanceTo], current_distance: float,
                               entropy: float = 0.0, vertices_not_to_choose: Set[int] = set()
                               ) -> Tuple[int, float]:
    # if len(ordered_distances) > len(vertices_not_to_choose):
    while True:
        for point in ordered_distances:
            if point.distance > current_distance:
                break
            elif random.random() >= entropy and point.index not in vertices_not_to_choose:
                # print("point %i is available" % point.index)
                return point.index, point.distance
    # else:
    #     raise Exception("No more Points to")


def swap_elements(path: List[int], position_of_next: int, position_of_freed_up_element: int) -> List[int]:
    if position_of_next >= position_of_freed_up_element:
        raise Exception("First element %d is not smaller in position than second element %d"
                        % (position_of_next, position_of_freed_up_element))
    path = path[:position_of_next] + [path[position_of_freed_up_element]] \
        + list(reversed(path[position_of_next+1:position_of_freed_up_element])) \
        + [path[position_of_next]] + path[position_of_freed_up_element+1:]
    return path


def solve(points: List[Point]) -> Tuple[List[int], float, List[float]]:
    dim = len(points)
    distance_matrix = np.zeros((dim, dim))
    for i in range(dim):
        for j in range(i + 1, dim):
            d = np.sqrt((points[i].x - points[j].x)**2 + (points[i].y - points[j].y)**2)
            distance_matrix[i, j] = d
            distance_matrix[j, i] = d
    distance_dict = {}
    for i in range(dim):
        distances = [DistanceTo(index, distance) for index, distance in enumerate(distance_matrix[i]) if index != i]
        distance_dict[i] = sorted(distances, key=lambda tup: tup.distance)
    # for i in range(dim):
    #     print(distance_dict[i])
    # return
    path = list(range(dim))
    best_path = path.copy()
    distance_path = sum([distance_matrix[path[i], path[i+1]] for i in range(dim-1)]
                        + [distance_matrix[path[dim-1], path[0]]])
    distance_best_path = distance_path
    best_distances = [distance_best_path]
    counter = 0
    # while counter < 1000000:
    while counter < 10000:
        # if counter != 0 and counter % 1000 == 0:
        #     print("counter = %i" % counter)
        best_distances.append(distance_best_path)
        counter += 1
        # restart with best path so far
        path = best_path.copy()
        distance_path = distance_best_path
        # choose starting vertex
        start = np.random.randint(dim)
        # print("dim = %d, start = %d" % (dim, start))
        # rearrange path so start is the start of the cycle
        path = path[start:] + path[:start]
        # print("length of path = %d" % len(path))
        position_of_next = 1
        _next = path[position_of_next]
        used_vertices = set()
        used_vertices.add(_next)
        for _ in range(100000):
            # print(distance_dict[_next])
            # print("---------------------------------")
            close_to_next, distance = choose_close_unused_vertex(
                distance_dict[_next],
                current_distance=distance_matrix[path[0], _next],
                entropy=0.8,
                vertices_not_to_choose=used_vertices
            )
            # print("_next = %i, close_to_next = %i" % (_next, close_to_next))
            position_of_freed_up_element = path.index(close_to_next) - 1
            if close_to_next == path[0] or position_of_freed_up_element == position_of_next:
                break
            # TODO distance computation somehow broken
            distance_path -= distance_matrix[path[0], _next]
            distance_path += distance_matrix[_next, close_to_next]
            freed_up_element = path[position_of_freed_up_element]
            distance_path -= distance_matrix[path[position_of_freed_up_element], close_to_next]
            distance_path += distance_matrix[path[0], path[position_of_freed_up_element]]
            path = swap_elements(path, position_of_next, position_of_freed_up_element)
            if distance_path < distance_best_path:
                distance_best_path = distance_path
                # print("New best distance found: %.2f" % distance_best_path)
                best_path = path.copy()
                counter = 0
            used_vertices.add(close_to_next)
            used_vertices.add(freed_up_element)
            _next = freed_up_element
            # position_of_next = position_of_freed_up_element
        # TODO introduce second stage where long vertices are eliminated?

    return best_path, distance_best_path, best_distances





