#=
local_search:
- Julia version: 1.4.1
- Author: paul
- Date: 2020-06-09
=#
using Random: randperm

struct Neighbor
    index::UInt32
    distance::Float32
end
function compute_distance(
    point1::AbstractVector{<:Real},
    point2::AbstractVector{<:Real})
    return sqrt((point1[1] - point2[1])^2 + (point1[2] - point2[2])^2)
end

function choose_close_unused_vertex(
    neighbors::Vector{Neighbor},
    distances_to_point::Vector{<:Real},
    current_distance::Real,
    vertices_not_to_choose::Set{Int},
    entropy=0.8)

    available_points = setdiff(
        [neighbor.index for neighbor in neighbors if neighbor.distance <= current_distance],
        vertices_not_to_choose)

    if isempty(available_points)
#         println("No available points, searching for extra points")
        while true
            for (index, distance) in enumerate(distances_to_point)
                if (distance <= current_distance && index ∉ vertices_not_to_choose && rand() > entropy)
                    return index, distance
                end
            end
        end
#         println("Done searching for extra points")
    else
#         println("Current distance = $current_distance")
#         println("going though the neighbors to find a suitable one")
        while true
#             for neighbor in neighbors
#                 println(neighbor.distance)
#             end
            for neighbor in neighbors
#                 print("Available points: ")
#                 print(available_points)
#                 print("current distance = $current_distance; distance of neighbor = ")
#                 print(neighbor.distance)
#                 print("\n")
                if neighbor.distance > current_distance
                    break
                elseif neighbor.index ∉ vertices_not_to_choose && rand() > entropy
                    return neighbor.index, neighbor.distance
                end
            end
        end
#         println("done going though the neighbors")
    end
end

function swap_elements!(path::Vector, first_index::Int, second_index::Int)
    if first_index >= second_index
        error("First element $first_index is not smaller than the second element $second_index")
    end
#     println("swapping elements $first_index, and $second_index")
    path[:] = path[[1:(first_index-1); second_index:-1:first_index; (second_index+1):length(path)]]
end

function solve(
    point_coordinates::AbstractMatrix{<:Real};
    proportion_of_closest_neighbors=0.05,
    min_num_neighbors=20,
    max_num_neigbors=500,
    prop_long_path_exploration=0.8,
    prop_edges_to_sample_to_find_long_path=0.1,
    num_iter_per_exploration=30000,
    num_explorations=nothing)

    n = size(point_coordinates)[2]
#     println("building distance matrix")
    distance_matrix = zeros(Float32, n, n)
    Threads.@threads for i in 1:n
        @inbounds for j in i+1:n
            distance = compute_distance(point_coordinates[:,i], point_coordinates[:,j])
            distance_matrix[i,j] = distance
            distance_matrix[j,i] = distance
        end
    end
#     println("Done building distance matrix")

    num_neighbors_to_store = min(max_num_neigbors,
        max(min_num_neighbors, round(Int, proportion_of_closest_neighbors * n)))
    neighbors = Matrix{Neighbor}(undef, num_neighbors_to_store, n)
    @inbounds Threads.@threads for i in 1:n
        neighbors_of_i = Neighbor[]
        for (j, distance) in enumerate(distance_matrix[:,i])
            if i == j
                continue
            elseif isempty(neighbors_of_i) || (last(neighbors_of_i).distance < distance && length(neighbors_of_i) <= num_neighbors_to_store)
                push!(neighbors_of_i, Neighbor(j, distance))
            elseif distance < first(neighbors_of_i).distance
                pushfirst!(neighbors_of_i, Neighbor(j, distance))
            else
                @inbounds for (index, neighbor) in enumerate(neighbors_of_i)
                    if neighbor.distance > distance
                        insert!(neighbors_of_i, index, Neighbor(j, distance))
                        break
                    end
                end
            end
            if length(neighbors_of_i) > num_neighbors_to_store
                pop!(neighbors_of_i)
            end
        end
        neighbors[:,i] = neighbors_of_i
    end
#     println("Done building neighbors object")
#     println(neighbors[:,1])
    function compute_path_length(path)
        return sum([distance_matrix[path[i],path[i+1]] for i in 1:(n-1)]) +
            distance_matrix[last(path),first(path)]
    end

    function run_with_start_path(
        start_path=nothing,
        num_iter_per_exploration=num_iter_per_exploration)

#         println("running with start path")
        if start_path == nothing
            start_path = randperm(n)
        end
        best_path = copy(start_path)
        distance_path = compute_path_length(start_path)
#         println("distance of start path: $distance_path")
        distance_best_path = distance_path
        for it in 1:num_iter_per_exploration
#             println("running iteration $it")
            # restart with best path so far
            start_path = copy(best_path)
            distance_path = compute_path_length(best_path)
            # choose starting vertex
            if rand() < prop_long_path_exploration
                start, long_path_distance = 0, 0.0
                sample_indices = rand(1:n, round(Int, n * prop_edges_to_sample_to_find_long_path))
                @inbounds for j in sample_indices
                    distance = distance_matrix[start_path[j], start_path[j+1 > n ? 1 : j+1]]
                    if distance > long_path_distance
                        start = j
                        long_path_distance = distance
                    end
                end
            else
                start = rand(1:n)
            end
            # rearange path so start is the start of the cycle
            start_path = start_path[[start:length(start_path); 1:(start-1)]]
            _next = start_path[2]
            used_vertices = Set([_next])
            @inbounds for _ in 1:n
                close_to_next, distance = choose_close_unused_vertex(
                    neighbors[:,_next],
                    distance_matrix[:,_next],
                    distance_matrix[start_path[1], _next],
                    used_vertices)
                position_of_freed_up_element = findfirst(x -> x == close_to_next, start_path) - 1
                if close_to_next == start_path[1] || position_of_freed_up_element == 2
                    break
                end
#                 println("distance before = $distance_path")
#                 println("recomputed distance before = " * string(compute_path_length(start_path)))
#                 println("old path:")
#                 println(start_path)
                freed_up_element = start_path[position_of_freed_up_element]
                distance_path -= distance_matrix[start_path[1], _next]
#                 distance_path += distance
                distance_path += distance_matrix[_next, close_to_next]
                distance_path -= distance_matrix[freed_up_element, close_to_next]
                distance_path += distance_matrix[start_path[1], freed_up_element]
#                 println("distance after = $distance_path")
                swap_elements!(start_path, 2, position_of_freed_up_element)
#                 println("recomputed distance after = " * string(compute_path_length(start_path)))
#                 println("new path:")
#                 println(start_path)
                if distance_path < distance_best_path && compute_path_length(start_path) < distance_best_path
                    distance_best_path = compute_path_length(start_path)
                    best_path = copy(start_path)
                end
                push!(used_vertices, close_to_next)
                push!(used_vertices, freed_up_element)
                _next = freed_up_element
            end
        end
        return best_path, compute_path_length(best_path)
    end

    if num_explorations == nothing
        num_explorations = 4 * Threads.nthreads()
    end
    paths = Matrix{Int}(undef, n, num_explorations)
    distances = Vector{Float32}(undef, num_explorations)
    @inbounds Threads.@threads for i in 1:num_explorations
        paths[:,i], distances[i] = run_with_start_path()
    end
    best_path = paths[:, argmin(distances)]

    return best_path, compute_path_length(best_path)
end
