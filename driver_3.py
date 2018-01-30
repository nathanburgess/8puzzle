import sys
import platform
from collections import deque


class Tree:
    def __init__(self, input):
        node = Board(input)
        self.expandNode(node)
        self.root = node
        print(node)

    def expandNode(self, board):
        print(board)
        board.set(2, 9)

class Board:
    def __init__(self, input):
        self.tiles = []
        for i in input:
            self.tiles.append(int(i))
        self.children = []

    def __str__(self):
        return self.tiles.__str__()

    def __getitem__(self, item):
        return self.tiles[item]

    def __setitem__(self, key, value):
        self.tiles[key] = value

    def set(self, index, value):
        self.tiles[index] = value


if platform.system() == "Windows":
    import psutil
else:
    import resource

mode = sys.argv[1]
board = Board(sys.argv[2].split(","))

print()
# print(board)
t = Tree(board)
# print(t)

pathToGoal = ["Up", "Left", "Left"]
pathCost = 0
nodesExpanded = 0
depth = 0
maxDepth = 0
runTime = 0
maxRam = 0

if platform.system() == "Windows":
    maxRam = psutil.Process().memory_info().rss
else:
    maxRam = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

print("\n\npath_to_goal:", pathToGoal)
print("cost_of_path:", pathCost)
print("nodes_expanded:", nodesExpanded)
print("search_depth:", depth)
print("max_search_depth:", maxDepth)
print("running_time:", runTime)
print("max_ram_usage:", maxRam * 0.000001)
