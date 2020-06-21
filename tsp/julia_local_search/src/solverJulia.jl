include("local_search.jl")
const DATA_FILE_NAME = joinpath(@__DIR__, ARGS[1])

const LINES = open(DATA_FILE_NAME) do f
    readlines(f)
end

const NODE_COUNT = parse(Int32, LINES[1])

const POINTS = let
    coordinates = zeros(Float32, 2, NODE_COUNT)
    @inbounds for i in 1:NODE_COUNT
        parts = split(LINES[i+1])
        # coordinates[:,i] = reshape(parse.(Int32, parts), (2, 1))
        coordinates[:,i] = parse.(Float32, parts)
    end
    coordinates
end
best_path, distance = solve(POINTS)

const SOLUTION = collect(1:NODE_COUNT)
const TOTAL_DISTANCE = let
    total_distance = 0.0
    @inbounds for column_index in 1:(size(POINTS)[2] - 1)
        total_distance += compute_distance(
        POINTS[:,SOLUTION[column_index]], POINTS[:,SOLUTION[column_index+1]])
    end
    total_distance += compute_distance(POINTS[:,last(SOLUTION)], POINTS[:,SOLUTION[1]])
end
print(distance)
print(" 0\n")
for i in best_path
    print(i)
    print(" ")
end

