import sys
import platform
import queue
import time
from collections import deque

BOARD_SIZE = 0
BOARDS = []
goal = (0, 1, 2, 3, 4, 5, 6, 7, 8)

# class Tree:
#     def __init__(self, values):
#         self.root = Node(self, values)
#         self.root.calculate_children()
#
#     def __str__(self):
#         return self.root.__str__()
#
#     def bfs(self):
#         print("")
#
#
# class Node:
#     def __init__(self, parent, values):
#         self.parent = parent
#         self.values = tuple(values)
#         self.children = []
#         self.set_blank()
#
#     def __str__(self):
#         """Print out this board as a n x n square"""
#         val = []
#         for i, x in enumerate(self.values):
#             if i % 3 == 0:
#                 val.append("\n")
#             val.append("{} ".format(x))
#         return "".join(val)
#
#     def set_blank(self):
#         """Find the location of the blank space on this board"""
#         self.blank = []
#         for x, ix in enumerate(self.values):
#             if ix == 0:
#                 self.blank = x
#
#     def calculate_children(self):
#         """Calculate the children for this node"""
#         values = self.values
#
#         # Get indices for neighbors
#         uid = self.blank - BOARD_SIZE
#         rid = self.blank + 1
#         did = self.blank + BOARD_SIZE
#         lid = self.blank - 1
#
#         # Calculate the new board when a left move happens
#         if self.blank % BOARD_SIZE != 0:
#             new_values = list(values)
#             left = values[lid]
#             new_values[self.blank] = left
#             new_values[lid] = 0
#             self.add_child(new_values)
#
#         # Calculate the new board when a right move happens
#         if (self.blank - BOARD_SIZE + 1) % BOARD_SIZE != 0:
#             new_values = list(values)
#             right = values[rid]
#             new_values[self.blank] = right
#             new_values[rid] = 0
#             self.add_child(new_values)
#
#         # Calculate the new board when an up move happens
#         if self.blank >= BOARD_SIZE:
#             new_values = list(values)
#             up = values[uid]
#             new_values[self.blank] = up
#             new_values[uid] = 0
#             self.add_child(new_values)
#
#         # Calculate the new board when a down move happens
#         if self.blank < BOARD_SIZE * BOARD_SIZE - BOARD_SIZE:
#             new_values = list(values)
#             down = values[did]
#             new_values[self.blank] = down
#             new_values[did] = 0
#             self.add_child(new_values)
#
#         self.expand_children()
#
#         # print("Node: {} {}\nSelf: {} {}".format(node.__hash__(), node, self.__hash__(), self))
#         # print("up: {}, right: {}, down: {}, left: {}".format(up, right, down, left))
#
#     def add_child(self, values):
#         node = Node(self, values)
#         if node.values not in TILE_SET:
#             # print("Added values {} to TILE_SET ({})".format(node.values, len(TILE_SET)))
#             TILE_SET.add(node.values)
#             self.children.append(node)
#
#     def expand_children(self):
#         for node in self.children:
#             if node.values == goal:
#                 continue
#             node.calculate_children()


# RAM calculations are system dependant, import the proper package
if platform.system() == "Windows":
    import psutil
else:
    import resource

# Get the algorithm from the input arguments
algorithm = sys.argv[1]
# Get the puzzle to solve from the input arguments and save it as a tuple of ints
start = sys.argv[2].split(",")
start = tuple(map(int, start))

print()

# Determine the n x n size of the puzzle based on the input
size = 10
length = len(start)
while size > 1:
    size -= 1
    if length == size:
        continue
    if length % size == 0:
        BOARD_SIZE = size
        break


class Board:
    goal = (0, 1, 2, 3, 4, 5, 6, 7, 8)

    def __init__(self, tiles):
        self.tiles = tiles
        self.blank = 0
        self.set_blank()

    def __str__(self):
        """Print out this board as a n x n square"""
        val = []
        for i, x in enumerate(self.tiles):
            if i % 3 == 0:
                val.append("\n")
            val.append("{} ".format(x))
        return "".join(val)

    def goal_check(self):
        return goal == self.tiles

    def set_blank(self):
        """Find the location of the blank space on this board"""
        self.blank = []
        for x, ix in enumerate(self.tiles):
            if ix == 0:
                self.blank = x

    def move_tile(self, index):
        tiles = list(self.tiles)
        tiles[self.blank] = tiles[index]
        tiles[index] = 0
        new_board = Board(tuple(tiles))
        return new_board


class State:
    def __init__(self, board, path=[]):
        self.board = board
        self.path = path

    def goal_check(self):
        return self.board.goal_check()

    def create_paths(self):
        return [self.make_path(dir) for dir in ["up", "right", "down", "left"]]

    def make_path(self, dir):
        blank = self.board.blank
        col = self.board.blank % BOARD_SIZE
        row = int(self.board.blank / BOARD_SIZE)
        size = BOARD_SIZE - 1
        if dir == "up" and row > 0:
            blank -= size + 1
        if dir == "right" and col < size:
            blank += 1
        if dir == "down" and row < size:
            blank += size + 1
        if dir == "left" and col > 0:
            blank -= 1
        board = self.board.move_tile(blank)
        self.path.append(dir)
        return State(board, self.path)


pathCost = 0
nodesExpanded = 0
depth = 0
maxDepth = 0
maxRam = 0


def solve_bfs(initial_state):
    explored = set()
    frontier = deque()
    frontier.append(initial_state)
    global nodesExpanded

    while len(frontier) > 0:
        state = frontier.pop()
        explored.add(state.board.tiles)

        if state.goal_check():
            return state

        for node in state.create_paths():
            if node not in frontier and node.board.tiles not in explored:
                frontier.append(node)
                nodesExpanded += 1


start_time = time.time()

board = Board(start)
state = State(board)
solution = solve_bfs(state)
print(solution)
print(solution.board)
pathToGoal = solution.path

runTime = time.time() - start_time

#
# Print out the statistics for this puzzle
#

if platform.system() == "Windows":
    maxRam = psutil.Process().memory_info().rss
else:
    maxRam = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

print("\n---------------\npath_to_goal:", pathToGoal)
print("cost_of_path:", pathCost)
print("nodes_expanded:", nodesExpanded)
print("search_depth:", depth)
print("max_search_depth:", maxDepth)
print("running_time:", runTime)
print("max_ram_usage:", maxRam * 0.000001)
