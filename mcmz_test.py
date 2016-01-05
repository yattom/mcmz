import pytest
from mcmz import *


def test_shortest():
    maze = Maze(4, 4, 4)
    paths = PathNetwork(maze)
    ans = paths.shortest((0, 3, 1), (3, 3, 1))
    assert ans.dest == (3, 3, 1)
    assert ans.distance == 3
    assert ans.trace == [(0, 3, 1), (1, 3, 1), (2, 3, 1), (3, 3, 1)]


def test_shortest_obstacles_and_jump():
    '''
    Z
    ######
    #    #
    #  % # %=1 block tall
    #S##G#
    #  # #
    ###### X
    '''
    maze = Maze(4, 4, 4)
    maze.put(1, 2, 1, WALL)
    maze.put(2, 2, 1, WALL)
    maze.put(2, 2, 0, WALL)
    maze.put(2, 3, 2, WALL)
    paths = PathNetwork(maze)
    ans = paths.shortest((0, 3, 1), (3, 3, 1))
    assert ans.trace == [(0, 3, 1), (0, 3, 2), (1, 3, 2), (2, 2, 2), (3, 2, 2), (3, 3, 2), (3, 3, 1)]

def test_shortest_large():
    maze = Maze(10, 10, 10)
    paths = PathNetwork(maze)
    ans = paths.shortest((0, 9, 4), (9, 9, 4))
    assert ans.distance == 9


def test_falling_down():
    '''
    ######
    #S  N#
    #S  N# 
    ##  ##
    #   G#
    #   G#
    ###### X
    Y
    S -> G reachable
    S -> N unreachable
    '''
    maze = Maze(5, 5, 1)
    maze.put(0, 2, 0, WALL)
    maze.put(2, 2, 0, WALL)
    paths = PathNetwork(maze)
    ans = paths.shortest((0, 1, 0), (2, 4, 0))
    assert ans

    ans = paths.shortest((0, 1, 0), (2, 1, 0))
    assert not ans


# def test_shortest_huge():
#     maze = Maze(30, 10, 30)
#     paths = PathNetwork(maze)
#     ans = paths.shortest((0, 9, 4), (9, 9, 4))
#     assert ans.distance == 9


