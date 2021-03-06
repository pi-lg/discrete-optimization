#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from collections import namedtuple
from utils import Point
from local_search_solver import solve
import os
from subprocess import Popen, PIPE
from multiprocessing import cpu_count


def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # Writes the inputData to a temporary file

    julia_dir = 'julia_local_search/src/'
    tmp_file_name = 'tmp.data'
    tmp_file = open(julia_dir + tmp_file_name, 'w')
    tmp_file.write(input_data)
    tmp_file.close()

    # Runs the command: java Solver -file=tmp.data
    os.environ["JULIA_NUM_THREADS"] = str(cpu_count())
    process = Popen(['julia', 'julia_local_search/src/solverJulia.jl'
                     , tmp_file_name
                    ], stdout=PIPE, universal_newlines=True)
    (stdout, stderr) = process.communicate()

    # removes the temporary file
    os.remove(julia_dir + tmp_file_name)

    return stdout.strip()

    # parse the input
    lines = input_data.split('\n')

    nodeCount = int(lines[0])

    points = []
    for i in range(1, nodeCount+1):
        line = lines[i]
        parts = line.split()
        points.append(Point(float(parts[0]), float(parts[1])))
    if len(points) < 30000:
        best_path, distance = solve(points)
        solution = best_path
    else:
        solution = range(0, nodeCount)
    # build a trivial solution
    # visit the nodes in the order they appear in the file

    # calculate the length of the tour
    obj = length(points[solution[-1]], points[solution[0]])
    for index in range(0, nodeCount-1):
        obj += length(points[solution[index]], points[solution[index+1]])

    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

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
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)')

