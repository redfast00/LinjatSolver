#!/usr/bin/env python3

import time
import argparse
import string

from parser import puzzles
from solver import solve_puzzle

from termcolor import colored
import colorama

colorama.init()


def print_puzzle(p):
    for line in p:
        print(line)


def print_solution(s):
    used = {None: (' ', 'white')}
    current = 0
    allowed_letters = string.ascii_letters
    allowed_colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    for line in s:
        for tile in line:
            if tile not in used:
                new_letter = allowed_letters[current % len(allowed_letters)]
                new_color = allowed_colors[current % len(allowed_colors)]
                used[tile] = (new_letter, new_color)
                current += 1
            letter, color = used[tile]
            print(colored(letter, color), end='')
        print('')


parser = argparse.ArgumentParser()
parser.add_argument('difficulty', choices=list(puzzles.keys()))
parser.add_argument('level', type=int)
args = parser.parse_args()

difficulty = args.difficulty
level = args.level - 1

if (level not in range(len(puzzles[difficulty]))) or (puzzles[difficulty][level]['puzzle'] is None):
    parser.error(f"Level {args.level} does not have a puzzle for difficulty {difficulty}")


begin = time.monotonic()
puzzle = puzzles[difficulty][level]['puzzle']
solution = solve_puzzle(puzzle)
end = time.monotonic()
print_puzzle(puzzle)
print(f'Solved puzzle {args.level} of the {args.difficulty} levels in {round(end - begin, 2)} seconds')
print_solution(solution)
