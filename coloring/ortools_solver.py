import numpy as np
from typing import List, Tuple, Union
from ortools.sat.python import cp_model
import time


class VarArrayAndObjectiveSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables) -> None:
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0
        self.start = time.time()
        self.start_interval = time.time()

    def on_solution_callback(self) -> None:
        t1 = time.time()
        time_used = t1 - self.start
        interval_used = t1 - self.start_interval
        self.start_interval = t1
        # print("Interval using %.4f, Accu using %.4f, Solution %i" % (interval_used, time_used, self.__solution_count),
        #       end=", ")
        # print("objective value (colors used) = %i" % self.ObjectiveValue())
        self.__solution_count += 1

    def solution_count(self) -> int:
        return self.__solution_count


def solve(edges: List[tuple], num_vertices: int, max_minutes: int = 10) -> Tuple[int, int, List[int]]:
    model = cp_model.CpModel()
    # build graph
    graph_list = [set() for i in range(num_vertices)]
    for edge in edges:
        i, j = edge
        graph_list[i].add(j)
        graph_list[j].add(i)
    # print(graph_list[0])
    # for i in range(num_vertices):
    #     print("%i has neighbors: %s" % (i, ' '.join(map(str, list(graph_list[i])))))
    # Set decision variables
    colors = [-1] * num_vertices
    for i in range(num_vertices):
        colors[i] = model.NewIntVar(0, num_vertices, 'color_of_%i' % i)
    # Set constraints
    for i in range(num_vertices):
        for j in graph_list[i]:
            model.Add(colors[i] != colors[j])
            # print("the color of %i cannot be the same as the color of %i." % (i, j))
    obj_max_color = model.NewIntVar(0, num_vertices, 'num_colors')
    model.AddMaxEquality(obj_max_color, colors)
    model.Minimize(obj_max_color)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60 * max_minutes
    solution_printer = VarArrayAndObjectiveSolutionPrinter(colors)
    status = solver.SolveWithSolutionCallback(model, solution_printer)
    # print('---------------')
    # print('Status         : %s' % solver.StatusName(status))
    # print('#sol found     : %i' % solution_printer.solution_count())
    # print('Branches       : %i' % solver.NumBranches())
    # print('Wall time      : %f seconds' % solver.WallTime())

    num_colors = solver.ObjectiveValue() + 1
    solution = [-1] * num_vertices
    for idx, color_i in enumerate(colors):
        solution[idx] = solver.Value(color_i)
    is_optimal = -1
    if status == cp_model.OPTIMAL:
        is_optimal = 1
    elif status == cp_model.FEASIBLE:
        is_optimal = 0

    return int(num_colors), is_optimal, solution


