import sys
import random
import datetime
from functools import reduce

class Struct(object):
    def __init__(self, **kwargs):
        for k in kwargs:
            self.__setattr__(k, kwargs[k])

EMPTY = 0
OUTSIDE = -1
WALL = 1

def dump(msg):
    sys.stdout.write(str(msg) + "\n")
    sys.stdout.flush()

class Maze(object):
    def __init__(self, width=0, height=0, depth=0):
        self.width = width
        self.height = height
        self.depth = depth
        self.blocks = {}
        for x in range(width):
            for y in range(height):
                for z in range(depth):
                    self.blocks[(x, y, z)] = EMPTY

    def get(self, x, y, z):
        assert -1 <= x < self.width + 1
        assert -1 <= y < self.height + 1
        assert -1 <= z < self.depth + 1
        if (x, y, z) not in self.blocks:
            return OUTSIDE
        return self.blocks[(x, y, z)]

    def put(self, x, y, z, b):
        assert -1 <= x < self.width + 1
        assert -1 <= y < self.height + 1
        assert -1 <= z < self.depth + 1
        self.blocks[(x, y, z)] = b

    def all(self):
        return self.blocks.keys()

    def copy(self):
        copy = Maze(self.width, self.height, self.depth)
        copy.blocks = self.blocks.copy()
        return copy

def draw_map(maze, start, goal):
    '''
    >>> m = Maze(4, 2, 3)
    >>> m.put(0, 1, 0, WALL)
    >>> m.put(2, 0, 1, WALL)
    >>> print(draw_map(m, (0, 0, 0), (3, 2, 1)).strip())
    Y=0
    ######
    #    # Z=2
    #  # # Z=1
    #S   # Z=0
    ######
    Y=1
    ######
    #   G# Z=2
    #    # Z=1
    ##   # Z=0
    ######
    >>>

    '''
    def max3(a, b):
        return (max(a[0], b[0]), max(a[1], b[1]), max(a[2], b[2]))
    buffer = ''
    w, h, d = reduce(lambda a, b: max3(a, b), maze.all(), (0, 0, 0))
    for y in range(h + 1):
        buffer += "Y={0}\n".format(y)
        buffer += "#" * (w + 3)
        buffer += "\n"
        for z in range(d, -1, -1):
            l = '#'
            for x in range(w + 1):
                if start == (x, y, z):
                    l += "S"
                elif goal == (x, y, z):
                    l += "G"
                elif maze.get(x, y, z) == WALL:
                    l += "#"
                else:
                    l += " "
            else:
                l += "#"
            buffer += "{0} Z={1}\n".format(l, z)
        buffer += "#" * (w + 3)
        buffer += "\n"
    return buffer



class PathNetwork(object):
    def __init__(self, maze):
        vacancies = set()
        for (x, y, z) in maze.all():
            if (maze.get(x, y, z) is EMPTY and
                maze.get(x, y - 1, z) is EMPTY):
                vacancies.add((x, y, z))

        paths = set()
        for (x, y, z) in vacancies:
            def addif(x2, y2, z2):
                if (x2, y2, z2) in vacancies:
                    paths.add(((x, y, z), (x2, y2, z2)))
            # walk
            if maze.get(x, y + 1, z) is not EMPTY:
                addif(x - 1, y    , z    )
                addif(x + 1, y    , z    )
                addif(x    , y    , z - 1)
                addif(x    , y    , z + 1)

                # jump up
                if maze.get(x, y - 2, z) is EMPTY:
                    if maze.get(x - 1, y, z) is not EMPTY:
                        addif(x - 1, y - 1, z)
                    if maze.get(x + 1, y, z) is not EMPTY:
                        addif(x + 1, y - 1, z)
                    if maze.get(x, y, z - 1) is not EMPTY:
                        addif(x, y - 1, z - 1)
                    if maze.get(x, y, z + 1) is not EMPTY:
                        addif(x, y - 1, z + 1)

            # fall
            addif(x    , y + 1, z    )

        self.vacancies = vacancies
        self.paths = paths


    def shortest(self, start, goal):
        assert start in self.vacancies
        assert goal in self.vacancies

        # pos, len, trail
        to_check = [Struct(dest=start, distance=0, trace=[start])]
        checked = {}
        while to_check:
            s = to_check.pop(0)
            sp, sl, st = s.dest, s.distance, s.trace
            for p1, p2 in [path for path in self.paths if path[0] == sp]:
                assert p1 == sp
                new = Struct(dest=p2, distance=sl + 1, trace=st + [p2])
                if p2 in checked:
                    if checked[p2].distance <= new.distance:
                        continue
                checked[p2] = new
                to_check.append(new)

        assert to_check == []
        if goal in checked:
            return checked[goal]
        else:
            return None


def limit(l, generator):
    if l <= 0:
        return
    c = 0
    for e in generator:
        if l <= c:
            return
        yield e
        c += 1


def build_random_maze(size, entry_points, density):
    maze = Maze(size, size, size)
    for i in range(int(size * size * size * density)):
        x, y, z = [random.randint(0, 9) for _ in [0, 0, 0]]
        maze.put(x, y, z, WALL)
    clear_entry_points(maze, entry_points)
    return maze


def clear_entry_points(maze, entry_points):
    for e in entry_points:
        maze.put(e[0], e[1], e[2], EMPTY)
        maze.put(e[0], e[1] - 1, e[2], EMPTY)
        if e[1] + 1 < maze.height:
            maze.put(e[0], e[1] + 1, e[2], WALL)


def build_candidates(size, start, goal, density, timeout=100):
    started_at = datetime.datetime.now()
    while True:
        maze = build_random_maze(size, [start, goal], density)
        paths = PathNetwork(maze)
        ans = paths.shortest(start, goal)
        if ans:
            yield ans.distance, maze
        if (datetime.datetime.now() - started_at).seconds > timeout:
            raise RuntimeError('timeout')


def mutate(maze):
    for i in range(6):
        maze.put(random.randint(0, maze.width - 1),
                 random.randint(0, maze.height - 1),
                 random.randint(0, maze.depth - 1),
                 random.choice([WALL, EMPTY]))
    return maze


def cross(m1, m2):
    m = Maze(m1.width, m1.height, m1.depth)
    axis = random.choice(['x', 'y', 'z'])
    cut = random.randint(1, 8)
    for x, y, z in m.all():
        if ((axis == 'x' and x < cut) or
            (axis == 'y' and y < cut) or
            (axis == 'z' and z < cut)):
            m.put(x, y, z, m1.get(x, y, z))
    for x, y, z in m.all():
        if ((axis == 'x' and x >= cut) or
            (axis == 'y' and y >= cut) or
            (axis == 'z' and z >= cut)):
            m.put(x, y, z, m2.get(x, y, z))
    return m



def build_next_generation(bests, population, start, goal):
    nexts = bests[:]
    while len(nexts) < population:
        if random.random() < 0.5:
            c = random.choice(bests)[1]
            m = mutate(c.copy())
        else:
            c1 = random.choice(bests)[1]
            c2 = random.choice(bests)[1]
            m = cross(c1, c2)

        clear_entry_points(m, [start, goal])
        paths = PathNetwork(m)
        ans = paths.shortest(start, goal)
        if ans:
            nexts.append((ans.distance, m))
    return nexts


STABLE_THRESHOLD = 100
INITIAL_DENSITY = 0.2
INITIAL_POPULATION = 10
CANDIDATE_POPULATION = 50
MAZE_SIZE = 10

def initial_candidates(start, goal, count):
    candidates = limit(count * 3, build_candidates(MAZE_SIZE, start, goal, INITIAL_DENSITY))
    return sorted(candidates, key = lambda c: -c[0])[:count]


def most_complex_maze():
    start = (0, 9, 0)
    goal = (9, 6, 9)
    bests = initial_candidates(start, goal, INITIAL_POPULATION)
    top = (0, 0)
    while True:
        candidates = sorted(build_next_generation(bests, CANDIDATE_POPULATION, start, goal), key = lambda c: -c[0])
        bests = candidates[:10]
        if top[0] < bests[0][0]:
            top = (bests[0][0], 0)
        else:
            top = (top[0], top[1] + 1)
            if top[1] > STABLE_THRESHOLD:
                break
        dump([b[0] for b in bests])
    dump(draw_map(bests[0][1], start, goal))


if __name__=='__main__':
    most_complex_maze()
