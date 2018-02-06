import sys
import platform
import time
from collections import OrderedDict
import heapq

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

    def __init__(self, tiles, parent=None, path=None):
        self.tiles = tiles
        self.parent = parent
        self.path = path
        self.depth = (parent.depth + 1) if parent else 0
        self.cost = 1

    def expand(self):
        children = []
        blank = self.tiles.index(0)
        col = blank % board_size
        row = int(blank / board_size)

        for dir in ["Up", "Down", "Left", "Right"]:
            # pdir = self.parent.path if self.parent else None
            # if pdir == "Up" and dir == "Down":
            #     continue
            # elif pdir == "Down" and dir == "Up":
            #     continue
            # elif pdir == "Left" and dir == "Right":
            #     continue
            # elif pdir == "Right" and dir == "Left":
            #     continue

            pos = test_dir(dir, blank, row, col)
            if pos != -1:
                tiles = list(self.tiles)
                new_tiles = tiles
                new_tiles[pos], new_tiles[blank] = new_tiles[blank], new_tiles[pos]
                children.append(Node(tuple(new_tiles), self, dir))
        return children


class AstNode:
    global goal_state

    def __init__(self, tiles, parent=None, path=None, cost=1):
        self.tiles = tiles
        self.parent = parent
        self.path = path
        self.depth = (parent.depth + 1) if parent else 0
        self.cost = cost
        self.heuristic = 0

    def __str__(self):
        return "{} : {}".format(self.tiles, self.heuristic)

    def __lt__(self, other):
        return self.heuristic < other.heuristic

    def __eq__(self, other):
        return self.tiles == other

    def __cmp__(self, other):
        return self < other

    def __hash__(self):
        return hash(self.tiles)

    def expand(self):
        children = []
        blank = self.tiles.index(0)
        col = blank % board_size
        row = int(blank / board_size)

        for dir in ["Up", "Down", "Left", "Right"]:
            pos = test_dir(dir, blank, row, col)
            if pos != -1:
                tiles = list(self.tiles)
                new_tiles = tiles
                new_tiles[pos], new_tiles[blank] = new_tiles[blank], new_tiles[pos]
                children.append(AstNode(tuple(new_tiles), self, dir))
        return children

    def calculate_ast_heuristic(self):
        self.heuristic = self.count_misplaced_tiles() + self.manhattan_distance()

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

    def count_misplaced_tiles(self):
        count = 0
        for i, x in enumerate(self.tiles):
            if x != goal_state[i]:
                count += 1
        return count


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
        explored.add(state.tiles)

        if state.tiles == goal_state:
            nodesExpanded = len(explored)
            return state

        children = state.expand()
        children.reverse()
        for child in children:
            if child not in frontier and child.tiles not in explored:
                counter += 1
                frontier[counter] = child
                maxDepth = child.depth


def ast(state):
    global nodesExpanded
    global maxDepth
    global goal_state
    state = AstNode(state)
    state.calculate_ast_heuristic()
    frontier = [state]
    explored = set()

    while frontier:
        state = heapq.heappop(frontier)
        nodesExpanded = len(explored)
        explored.add(state.tiles)

        if state.tiles == goal_state:
            return state

        if len(explored) % 1000 == 0:
            print(len(explored))

        # if len(explored) > 10:
        #     return state

        for child in state.expand():
            if child not in frontier and child.tiles not in explored:
                nodesExpanded += 1
                frontier.append(child)
                maxDepth = child.depth
            elif child in frontier:
                frontier.remove(child)
                child.heuristic -= 1
                frontier.append(child)

    return state


solution = None

# Track how long the program takes to execute
start_time = time.clock()
if sys.argv[1] == "bfs":
    solution = bfs(initial_state)
elif sys.argv[1] == "dfs":
    solution = dfs(initial_state)
elif sys.argv[1] == "ast":
    solution = ast(initial_state)

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
