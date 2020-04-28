from typing import Dict, Tuple, Type
from math import sin, pi
from random import random, seed
from itertools import product
from enum import Enum

import cairo

WIDTH, HEIGHT = (256,) * 2
PIXEL_SCALE = 10

INITAL_PROBABILITY = 0.3

NUMBER_OF_ITERATIONS = 100
TRANSITION_STEPS = 15

DEAD_CELL_SIZE = 1.5
ALIVE_CELL_SIZE = 5


class CellState(Enum):
    ALIVE = 1
    DYING = 2
    DEAD = 3
    GROWING = 4


CellBlock = Dict[Tuple[int, int], CellState]


def get_cells(n: int, percent: float) -> CellBlock:
    return {
        (x, y): CellState.ALIVE if random() < percent else CellState.DEAD
        for x, y in product(range(1, n), repeat=2)
    }


def get_number_neighbours(x: int, y: int, cells: CellBlock) -> int:
    number_of_neighbours = 0
    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            if i == x and y == j:
                continue

            cell_state = cells.get((i, j), CellState.DEAD)
            if cell_state == CellState.DEAD:
                continue

            number_of_neighbours += 1
    return number_of_neighbours


def iterate_cell(state: CellState, number_of_neighbours: int) -> CellState:
    if state == CellState.ALIVE:
        if number_of_neighbours in {2, 3}:
            return CellState.ALIVE
        else:
            return CellState.DYING

    if number_of_neighbours == 3:
        return CellState.GROWING
    else:
        return CellState.DEAD


def iterate_cells(cells: CellBlock) -> CellBlock:
    output = {}
    for (x, y), state in cells.items():
        number_of_neighbours = get_number_neighbours(x, y, cells)
        output[x, y] = iterate_cell(state, number_of_neighbours)
    return output


def create_image(
    context: cairo.Context, cells: CellBlock, cell_sizes: Dict[CellBlock, float]
) -> None:
    context.rectangle(0, 0, WIDTH, HEIGHT)
    context.set_source_rgb(1, 1, 1)
    context.fill()

    context.set_source_rgb(0, 0, 0)
    for (x, y), cell_state in cells.items():
        context.arc(x * 16, y * 16, cell_sizes[cell_state], 0, 2 * pi)
        context.fill()


def map_state(cell_state: CellState) -> CellState:
    if cell_state == CellState.DYING:
        return CellState.DEAD

    if cell_state == CellState.GROWING:
        return CellState.ALIVE

    return cell_state


def main():
    surface = cairo.ImageSurface(
        cairo.FORMAT_RGB24, WIDTH * PIXEL_SCALE, HEIGHT * PIXEL_SCALE
    )
    context = cairo.Context(surface)
    context.scale(PIXEL_SCALE, PIXEL_SCALE)

    cell_size_diff = (ALIVE_CELL_SIZE - DEAD_CELL_SIZE) / TRANSITION_STEPS

    cell_sizes = {
        CellState.ALIVE: ALIVE_CELL_SIZE,
        CellState.DEAD: DEAD_CELL_SIZE,
        CellState.GROWING: None,
        CellState.DYING: None,
    }

    seed(2)
    cells = get_cells(16, INITAL_PROBABILITY)

    def _write_image(frame: int, reset: bool) -> None:
        nonlocal cells
        if reset:
            cells = {k: map_state(v) for k, v in cells.items()}
        create_image(context, cells, cell_sizes)
        surface.write_to_png(f"output/{frame:03}.png")
        print(frame)

    for i in range(
        1, TRANSITION_STEPS * NUMBER_OF_ITERATIONS, TRANSITION_STEPS
    ):
        _write_image(i, reset=True)
        cells = iterate_cells(cells)
        for step in range(1, TRANSITION_STEPS):
            cell_sizes[CellState.GROWING] = (
                DEAD_CELL_SIZE + step * cell_size_diff
            )
            cell_sizes[CellState.DYING] = (
                ALIVE_CELL_SIZE - step * cell_size_diff
            )
            _write_image(i + step, reset=False)
    else:
        _write_image(i + TRANSITION_STEPS, reset=True)


if __name__ == "__main__":
    main()
