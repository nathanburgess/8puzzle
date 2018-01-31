import sys
import platform
import copy

BOARD_SIZE = 0
TILE_SET = set()


class Tree:
    def __init__(self, values):
        self.root = Node(self, values)
        self.root.expand()
        self.root.expand()

    def __str__(self):
        return self.root.__str__()


class Node:
    def __init__(self, parent, values):
        self.parent = parent
        self.values = values
        self.set_blank()

    def __str__(self):
        val = []
        for i, x in enumerate(self.values):
            if i % 3 == 0:
                val.append("\n")
            val.append("{} ".format(x))
        return "".join(val)

    def set_blank(self):
        """Find the location of the blank for this board"""
        self.blank = []
        for x, ix in enumerate(self.values):
            if ix == 0:
                self.blank = x

    def __eq__(self, other):
        return self.values == other.values

    def __hash__(self):
        return hash(repr(self))

    def expand(self):
        values = self.values

        # Get indices for neighbors
        upIdx = self.blank - BOARD_SIZE
        rightIdx = self.blank + 1
        downIdx = self.blank + BOARD_SIZE
        leftIdx = self.blank - 1
        up = right = down = left = 0

        # Determine available moves
        if self.blank % BOARD_SIZE != 0:
            left = values[leftIdx]
        if (self.blank - BOARD_SIZE + 1) % BOARD_SIZE != 0:
            right = values[rightIdx]
        if self.blank >= BOARD_SIZE:
            up = values[upIdx]
        if self.blank < BOARD_SIZE * BOARD_SIZE - BOARD_SIZE:
            down = values[downIdx]

        # print(self.values)
        print(hash(repr(self)))

        # newValues = copy.deepcopy(values)
        # newValues[self.blank] = up
        # newValues[upIdx] = 0
        #
        # node = Node(self, newValues)
        # if node.values in TILE_SET:
        #     print("Node was already explored")
        # else:
        #     print("Node has not been explored")
        #     TILE_SET.add(node)
        #     print(node)

        print("up: {}, right: {}, down: {}, left: {}".format(up, right, down,
                                                             left))


if platform.system() == "Windows":
    import psutil
else:
    import resource

mode = sys.argv[1]
start = sys.argv[2].split(",")
start = list(map(int, start))
goal = [0, 1, 2, 3, 4, 5, 6, 7, 8]

print()
size = 10
length = len(start)
while size > 1:
    size -= 1
    if length == size:
        continue
    if length % size == 0:
        BOARD_SIZE = size
        break

t = Tree(start)
print(t)


pathToGoal = []
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

print("\n---------------\npath_to_goal:", pathToGoal)
print("cost_of_path:", pathCost)
print("nodes_expanded:", nodesExpanded)
print("search_depth:", depth)
print("max_search_depth:", maxDepth)
print("running_time:", runTime)
print("max_ram_usage:", maxRam * 0.000001)
