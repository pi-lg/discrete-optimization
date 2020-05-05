from typing import List, Set
from random import choice


class Vertex:
    def __init__(self, index: int, edges: set = None):
        self.index = index
        if not edges:
            edges = set()
        self.edges = edges
        self.color = None
        self.impossible_colors = set()

    def add_link(self, vertex: 'Vertex'):
        self.edges.add(vertex)

    def paint(self, _color: int):
        if self.color:
            raise Exception("Cannot assign color {} to Vertex {} as it already has color {}".format(
                _color, self.index, self.color))
        elif _color in self.impossible_colors:
            raise Exception("Color {} is not valid for Vertex {}.".format(_color, self.index))
        else:
            self.color = _color
            for edge in self.edges:
                edge.remove_from_possible_colors(_color)

    def remove_from_possible_colors(self, _color: int):
        self.impossible_colors.add(_color)


class Graph:
    set_of_used_colors: Set[int] = set()
    uncolored_vertices: List[Vertex] = []

    def __init__(self, edges: list, num_vertices: int, num_edges: int):
        self.vertices = {i: Vertex(i) for i in range(num_vertices)}
        for edge in edges:
            i, j = edge
            self.vertices[i].add_link(self.vertices[j])
            self.vertices[j].add_link(self.vertices[i])

    def color_next_vertex(self):
        self.uncolored_vertices.sort(key=lambda v: (len(v.impossible_colors), len(v.edges)))
        vertex_to_color = self.uncolored_vertices.pop()
        possible_colors = self.set_of_used_colors.difference(vertex_to_color.impossible_colors)
        if possible_colors:
            if len(possible_colors) == 1:
                vertex_to_color.paint(possible_colors.pop())
            else:
                # TODO: how about choosing the value that least limits the choices you can make for the next (couple of)
                # - vertex (-ices) that would come next
                vertex_to_color.paint(choice(list(possible_colors)))  # a choice was made!!!!
                # TODO: we have made a choice, should we put the current state on the stack so we can go back later?
        else:
            max_color = max(self.set_of_used_colors) if self.set_of_used_colors else -1
            new_color = max_color + 1
            vertex_to_color.paint(new_color)
            self.set_of_used_colors.add(new_color)

    def color(self):
        self.uncolored_vertices = list(self.vertices.values())
        while self.uncolored_vertices:
            self.color_next_vertex()





