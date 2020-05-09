#!/usr/bin/python
# -*- coding: utf-8 -*-
from own_solver import Graph
from ortools_solver import solve

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))

    if node_count < 100:
        # solving with ortools
        number_of_colors, is_optimal, colors = solve(edges, node_count)
    else:
        # solving with own algorithm
        graph = Graph(edges, node_count, edge_count)
        graph.color()
        number_of_colors = max(graph.set_of_used_colors)
        is_optimal = 0
        colors = [graph.vertices[i].color for i in range(node_count)]

    # print("number of nodes: {}, number of edges: {}".format(node_count, edge_count))
    # print("number of colors used was: {}".format(max(graph.set_of_used_colors)))
    output_data = str(number_of_colors) + ' ' + str(is_optimal) + '\n'
    output_data += ' '.join([str(color) for color in colors])



    # # build a trivial solution
    # # every node has its own color
    # solution = range(0, node_count)
    #
    # # prepare the solution in the specified output format
    # output_data = str(node_count) + ' ' + str(0) + '\n'
    # output_data += ' '.join(map(str, solution))

    return output_data


import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')

