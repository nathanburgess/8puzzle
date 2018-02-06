import sys
import platform
import time
from collections import OrderedDict
import heapq
import queue

# Set up some "global" variables
goal_state = (0, 1, 2, 3, 4, 5, 6, 7, 8)
board_size = 0
nodesExpanded = 0
maxDepth = 0


def test_dir(dir, pos, row, col):
    if dir == "Up" and row > 0:
        return pos - board_size
    elif dir == "Down" and row < board_size - 1:
        return pos + board_size
    elif dir == "Left" and col > 0:
        return pos - 1
    elif dir == "Right" and col < board_size - 1:
        return pos + 1
    return -1


class Node:
    global goal_state
    global board_size

    def __init__(self, tiles, parent=None, path="None"):
        self.tiles = tiles
        self.parent = parent
        self.path = path
        self.depth = (parent.depth + 1) if parent else 0
        self.cost = 1
        self.heuristic = 0

    def __hash__(self):
        return hash(self.tiles)

    def __eq__(self, other):
        return self.tiles == other.tiles

    def __lt__(self, other):
        return self.heuristic < other.heuristic

    def expand(self, reverse=False):
        children = []
        blank = self.tiles.index(0)
        col = blank % board_size
        row = int(blank / board_size)

        for dir in ["Up", "Down", "Left", "Right"]:
            pos = test_dir(dir, blank, row, col)
            if pos != -1:
                tiles = list(self.tiles)
                tiles[pos], tiles[blank] = tiles[blank], tiles[pos]
                children.append(Node(tuple(tiles), self, dir))

        if reverse:
            children.reverse()
        return children

    def calculate_heuristic(self):
        self.heuristic = self.manhattan_distance() + self.depth

    def manhattan_distance(self):
        distance = 0
        goal_positions = []
        for i, item in enumerate(self.tiles):
            x = i % board_size
            y = int(i / board_size)
            goal_positions.append((x, y))

        for i, x in enumerate(self.tiles):
            if x == 0:
                continue
            x1 = i % board_size
            y1 = int(i / board_size)
            x2 = goal_positions[x][0]
            y2 = goal_positions[x][1]
            distance += abs(x1 - x2) + abs(y1 - y2)
        return distance


if platform.system() == "Windows":
    import psutil
else:
    import resource

# Get the algorithm from the input arguments
algorithm = sys.argv[1]
# Get the initial state
input_tiles = sys.argv[2].split(",")
initial_state = tuple(map(int, input_tiles))
print()

# Determine the n x n size of the puzzle based on the input
size = 10
length = len(input_tiles)
while size > 1:
    size -= 1
    if length == size:
        continue
    if length % size == 0:
        board_size = size
        break


def bfs(state):
    global nodesExpanded
    global maxDepth
    counter = 0
    frontier = OrderedDict()
    explored = set()

    frontier[counter] = Node(state)

    while frontier:
        state = frontier.pop(next(iter(frontier)))
        explored.add(state.tiles)

        if state.tiles == goal_state:
            nodesExpanded = len(explored)
            return state

        if len(explored) % 1000 == 0:
            print(len(explored))

        for child in state.expand():
            if child not in frontier and child.tiles not in explored:
                counter += 1
                frontier[counter] = child
                maxDepth = child.depth


def dfs(state):
    global nodesExpanded
    global maxDepth

    counter = 0
    frontier = OrderedDict()
    explored = set()

    frontier[counter] = Node(state)

    while frontier:
        state = frontier.pop(next(reversed(frontier)))
        explored.add(state)

        if state.tiles == goal_state:
            nodesExpanded = len(explored)
            return state

        if len(explored) % 1000 == 0:
            print(len(explored))

        for child in state.expand(True):
            if child not in frontier and child not in explored:
                counter += 1
                frontier[counter] = child
                maxDepth = child.depth


def ast(state, depth=0):
    global nodesExpanded
    global maxDepth
    global goal_state
    state = Node(state)
    state.calculate_heuristic()
    frontier = []
    explored = set()

    heapq.heappush(frontier, state)

    while frontier:
        heapq.heapify(frontier)
        state = heapq.heappop(frontier)
        explored.add(state)

        if depth and state.depth > depth:
            return None

        if state.tiles == goal_state:
            nodesExpanded = len(explored)
            return state

        if len(explored) % 1000 == 0:
            print(len(explored))

        for child in state.expand():
            child.calculate_heuristic()
            if child not in frontier and child not in explored:
                heapq.heappush(frontier, child)
                maxDepth = child.depth
            elif child in frontier:
                dirs = {"Up": 0, "Down": 1, "Left": 2, "Right": 3}
                old_child = frontier[frontier.index(child)]
                print("{0.path:5} {0.tiles}".format(child))
                print("{0.path:5} {0.tiles}".format(old_child))
                print()
                if dirs[old_child.path] > dirs[child.path]:
                    frontier.remove(child)
                    child.heuristic -= 1
                    heapq.heappush(frontier, child)


def idast(state, max_depth=0):
    depth = 1
    result = Node(state)

    while depth != max_depth:
        result = ast(state, depth)
        if result:
            return result
        depth += 1


solution = None

# Track how long the program takes to execute
start_time = time.clock()
if sys.argv[1] == "bfs":
    solution = bfs(initial_state)
elif sys.argv[1] == "dfs":
    solution = dfs(initial_state)
elif sys.argv[1] == "ast":
    solution = ast(initial_state)
elif sys.argv[1] == "idast":
    depth = 50
    if len(sys.argv) > 3:
        depth = sys.argv[3]
    solution = idast(initial_state, depth)

if not solution:
    print("It would appear that no solution exists for the puzzle", initial_state)
    exit()

temp = solution
pathToGoal = [temp.path]
pathCost = 1
while temp.depth > 1:
    temp = temp.parent
    pathToGoal.append(temp.path)
    pathCost += 1

nodesExpanded -= 1

#
# Print out the statistics for this puzzle
#
if platform.system() == "Windows":
    maxRam = psutil.Process().memory_info().rss
else:
    maxRam = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

output = open("output.txt", "w")
output.write("path_to_goal: {}\n".format(pathToGoal[::-1]))
output.write("cost_of_path: {}\n".format(pathCost))
output.write("nodes_expanded: {}\n".format(nodesExpanded))
output.write("search_depth: {}\n".format(solution.depth))
output.write("max_search_depth: {}\n".format(maxDepth))
output.write("running_time: {}\n".format(time.clock() - start_time))
output.write("max_ram_usage: {}".format(maxRam * 0.000001))

print("path_to_goal: {}".format(pathToGoal[::-1]))
print("cost_of_path: {}".format(pathCost))
print("nodes_expanded: {}".format(nodesExpanded))
print("search_depth: {}".format(solution.depth))
print("max_search_depth: {}".format(maxDepth))
print("running_time: {}".format(time.clock() - start_time))
print("max_ram_usage: {}".format(maxRam * 0.000001))

# bfs 6,1,8,4,0,2,7,3,5
#
# path_to_goal: ['Down', 'Right', ... , 'Up', 'Up']
# cost_of_path: 20
# nodes_expanded: 54094
# search_depth: 20
# max_search_depth: 21
#
#
#
# dfs 6,1,8,4,0,2,7,3,5
#
# path_to_goal: ['Up', 'Left', 'Down', ... , 'Up', 'Left', 'Up', 'Left']
# cost_of_path: 46142
# nodes_expanded: 51015
# search_depth: 46142
# max_search_depth: 46142
#
#
#
# ast 6,1,8,4,0,2,7,3,5
#
# path_to_goal: ['Down', 'Right', 'Up', 'Up', 'Left', 'Down', 'Right', 'Down', 'Left', 'Up', 'Left', 'Up', 'Right', 'Right', 'Down', 'Down', 'Left', 'Left', 'Up', 'Up']
# cost_of_path: 20
# nodes_expanded: 696
# search_depth: 20
# max_search_depth: 20
