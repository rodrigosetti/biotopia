#! /usr/bin/env python
# coding: utf-8

from copy import copy
from itertools import cycle, izip_longest, repeat, chain
from random import sample, randint, random

def neighbours(cell):
    "return the orthogonal neighbours"
    return set(((cell[0]-1, cell[1]),
                (cell[0], cell[1]-1),
                (cell[0], cell[1]+1),
                (cell[0]+1, cell[1])))

def sign(x):
    if x < 0:
        return -1
    elif x == 0:
        return 0
    else:
        return 1

class Creature(object):

    def __init__(self, position, cells, head, energy=0):
        """
        Create a new creature from structure. "cells" is a set of (x,y) tuples
        representing positions of the cells. "head" is a position, contained in
        "cells", that is the creature's head.
        """
        self.position = position
        self.cells = set(cells)
        self.head = head
        self.energy = energy
        self.age = 0

        self.analyze()

    def mirror_horizontal(self):
        self.cells = set((-c[0], c[1]) for c in self.cells)
        self.analyze()

    def mirror_vertical(self):
        self.cells = set((c[0], -c[1]) for c in self.cells)
        self.analyze()

    def rotate_right(self):
        self.cells = set((c[1], -c[0]) for c in self.cells)
        self.analyze()

    def rotate_left(self):
        self.cells = set((-c[1], c[0]) for c in self.cells)
        self.analyze()

    def mutate(self):
        """
        Perform one of the mutations:
        - add a new cell in a valid position (one neighbour empty space)
        - remove a movement cell (one neighbour cell)
        """
        if randint(0,1) == 0:
            return self.add_random_cell()
        else:
            return self.remove_random_cell() or self.add_random_cell()

    def add_random_cell(self):

        visited_empty_neighs = set()

        # look in every cell, in a random order
        for cell in sample(self.cells, len(self.cells)):

            # look all possible neighbours of this cell
            possible_neighs = neighbours(cell)

            # look all empty neighbours of this cell (takes out living cells)
            empty_neighs = possible_neighs.difference(self.cells)

            # look all non-visited empty neighbours of this cell
            # (takes out visited)
            empty_neighs = empty_neighs.difference(visited_empty_neighs)

            # look in every empty neighbour of every cell, in a random order
            for empty_neigh in sample(empty_neighs, len(empty_neighs)):

                # look all possible neighbour of this empty neighbour
                candidate_possible_neighs = neighbours(empty_neigh)

                # look all neighbours living cells of this empty neighbour
                candidate_cell_neighs = self.cells.intersection(candidate_possible_neighs)

                # if there is only one living cell neighbour, then add a new
                # cell there, analyze and return
                if len(candidate_cell_neighs) == 1:
                    self.cells.add(empty_neigh)
                    self.analyze()
                    return True

            # mark as visited
            visited_empty_neighs.update(empty_neighs)

        # couldn't add any cell (IMPOSSIBLE!)
        raise Exception("Unexpected mutation error: could not add cell")

    def remove_random_cell(self):

        # look in every cell, in a random order
        for cell in sample(self.cells, len(self.cells)):

            # cannot remove head
            if cell != self.head:
                # look all possible neighbours of this cell
                possible_neighs = neighbours(cell)

                # look all living cell neighbours of this cell
                cell_neighs = self.cells.intersection(possible_neighs)

                # if there is only one (movement), remove this cell, analyze and
                # return
                if len(cell_neighs) == 1:
                    self.cells.remove(cell)
                    self.analyze()
                    return True

        # couldn't remove any (single or no-cells case)
        return False

    def analyze(self):
        """
        Find out the movement and the mouths
        """
        to_visit = set([self.head])
        visited = set()
        self.mouths = set()

        vertical = horizontal = 0

        # while there are cells to visit
        while to_visit:

            # get the next cell
            cell = to_visit.pop()

            # this one is visited
            visited.add(cell)

            # get the cell neighbours positions
            possible_neighs = neighbours(cell)
            # get actual neighbours
            cell_neighs = self.cells.intersection(possible_neighs)

            # if this cell is connecting to more than one, the its closing a
            # cycle
            if len(visited.intersection(possible_neighs)) > 1:
                raise ValueError("Invalid structure: cycle found")

            # determine if this is a movement cell:
            elif len(cell_neighs) == 1:
                cell_neigh = next(iter(cell_neighs))
                if cell_neigh[0] == cell[0] - 1:
                    horizontal -= 1
                elif cell_neigh[0] == cell[0] + 1:
                    horizontal += 1
                elif cell_neigh[1] == cell[1] - 1:
                    vertical -= 1
                elif cell_neigh[1] == cell[1] + 1:
                    vertical += 1
                else:
                    raise Exception("Unexpected neighbour value")

            # add the unvisited neighbours to be visited
            to_visit.update(n for n in cell_neighs if n not in visited)

            # determine mouths, by checking the candidates which are not
            # already mouths, and are not living cells (i.e. are empty)
            for possible_mounth in (n for n in possible_neighs if n not in cell_neighs and n not in self.mouths):

                # checkout the neighbours of this mouth candidate
                possible_mounth_possible_neighs = neighbours(possible_mounth)

                # if the number of living cell of this possible mouth is more
                # than 2, the it's a real mounth
                if len(self.cells.intersection(possible_mounth_possible_neighs)) >= 3:
                    self.mouths.add(possible_mounth)

        # if the total visited cells is less than the actual cells, there are
        # some unreachable cells
        if len(visited) < len(self.cells):
            raise ValueError("Invalid structure: unconnected cells")

        # determine movement:
        self.movement = cycle(chain([(0, 0)],
                                    izip_longest(repeat(sign(horizontal), abs(horizontal)),
                                                 repeat(sign(vertical), abs(vertical)),
                                                 fillvalue = 0)))

        # normalize all for head to be at 0,0
        if self.head != (0,0):
            self.cells = set((c[0]-self.head[0], c[1]-self.head[1]) for c in
                             self.cells)

    def __repr__(self):
        return "<Creature %s, head=%s>" % (self.cells, self.head)

def default_descendant(position=(0,0), energy=0):
    """
    Return a random oriented default descendent
    """
    descendent = Creature(position, ((-1,1), (-1,0), (0,0), (1,0), (1,1)),
                          head=(0,0),
                          energy=energy)
    r = randint(1,4)

    if r == 1:
        descendent.rotate_right()
    elif r == 2:
        descendent.rotate_left()
    elif r == 3:
        descendent.mirror_vertical()

    return descendent

class MultiSet(object):

    def __init__(self, iterable = []):
        self.items = {}
        for value in iterable:
            self.add(value)

    def __contains__(self, value):
        return self.items.get(value, 0) > 0

    def __len__(self):
        return sum(self.items.itervalues())

    def add(self, value):
        self.items[value] = self.items.get(value, 0) + 1

    def remove(self, value):
        self.items[value] = self.items.get(value, 0) - 1
        if self.items[value] == 0:
            del self.items[value]

    def __iter__(self):
        for value, count in self.items.iteritems():
            for i in xrange(count):
                yield value

    def iter_unique(self):
        for value, count in self.items.iteritems():
            if count > 0:
                yield value

    def __repr__(self):
        return "<multiset %s>" % ','.join(iter(self))

ENERGY_LOSS = 1
ENERGY_GAIN = 20

class Zoo(object):

    def __init__(self, descendants, size,
                 offspring_energy,
                 start_food, start_keys,
                 wrap_vertical=False, wrap_horizontal=False,
                 mutation_probability = 0.2):
        self.creatures = set(descendants)
        self.size = size
        self.offspring_energy = offspring_energy
        self.wrap_horizontal = wrap_horizontal
        self.wrap_vertical = wrap_vertical
        self.mutation_probability = mutation_probability

        self.food = MultiSet()
        for i in xrange(start_food):
            while True:
                new_food = (randint(0,size[0]), randint(0,size[1]))
                if new_food not in self.food:
                    self.food.add(new_food)
                    break

        self.keys = MultiSet()
        for i in xrange(start_keys):
            while True:
                new_key = (randint(0,size[0]), randint(0,size[1]))
                if new_key not in self.keys and new_key not in self.food:
                    self.keys.add(new_key)
                    break

    def step(self):
        """
        Perform one step of the simulation.
        """
        survivors = set()

        for creature in self.creatures:
            creature.energy -= ENERGY_LOSS
            creature.age += 1

            for mouth in creature.mouths:
                # calculate absolute mouth position
                mouth_position = (mouth[0] + creature.position[0],
                                  mouth[1] + creature.position[1])

                if mouth_position in self.food:
                    # remove food particle from soup
                    self.food.remove(mouth_position)

                    # increment creature's energy
                    creature.energy += ENERGY_GAIN
                if mouth_position in self.keys:
                    # remove key particle from soup
                    self.keys.remove(mouth_position)

                    # create a copy of current creature with start energy
                    new_creature = Creature(mouth_position,
                                            copy(creature.cells),
                                            creature.head,
                                            energy = self.offspring_energy)

                    # mutate with probability
                    if random() < self.mutation_probability:
                        new_creature.mutate()

                    # turn to a random direction (left or right)
                    if randint(1,2) == 1:
                        new_creature.rotate_left()
                    else:
                        new_creature.rotate_right()
                    survivors.add(new_creature)


            # move
            try:
                movement = next(creature.movement)
                creature.position = (creature.position[0] + movement[0],
                                     creature.position[1] + movement[1])

                # colide or wrap horizontally
                if creature.position[0] < 0:
                    if self.wrap_horizontal:
                        creature.position = (creature.position[0] + self.size[0],
                                             creature.position[1])
                    else:
                        creature.position = (0, creature.position[1])
                        creature.mirror_horizontal()
                elif creature.position[0] > self.size[0]:
                    if self.wrap_horizontal:
                        creature.position = (creature.position[0] - self.size[0],
                                             creature.position[1])
                    else:
                        creature.position = (self.size[0], creature.position[1])
                        creature.mirror_horizontal()

                # colide or wrap vertically
                if creature.position[1] < 0:
                    if self.wrap_vertical:
                        creature.position = (creature.position[0],
                                             creature.position[1] + self.size[1])
                    else:
                        creature.position = (creature.position[0], 0)
                        creature.mirror_vertical()
                elif creature.position[1] > self.size[1]:
                    if self.wrap_vertical:
                        creature.position = (creature.position[0],
                                             creature.position[1] - self.size[1])
                    else:
                        creature.position = (creature.position[0], self.size[1])
                        creature.mirror_vertical()

            except StopIteration:
                pass

            # creature dies if is beyond the life expectancy, and the energy
            # level is less or equal than zero - for energy balance
            if creature.energy < 0:
                # dying creature, will not go to the next step, and will leave
                # a trace of food for each of its cells and head as key
                for cell in creature.cells:
                    if cell == creature.head:
                        self.keys.add((creature.position[0] + cell[0],
                                       creature.position[1] + cell[1]))
                    else:
                        self.food.add((creature.position[0] + cell[0],
                                       creature.position[1] + cell[1]))
            else:
                survivors.add(creature)

        self.creatures = survivors

if __name__  == "__main__":
    import sys
    import pygame
    from pygame.locals import *

    WIDTH = 800
    HEIGHT = 600

    CHART_HEIGHT = 100
    CHART_WIDTH = 600

    DESCENDANTS_ENERGY = 2000
    OFFSPRING_ENERGY = 1000

    START_FOOD = 50000
    START_KEYS = 250
    START_POPULATION = 250

    #: the maximum amount of population or keys
    POP_MAX = START_KEYS + START_POPULATION

    # initialize simulation
    zoo = Zoo([default_descendant(position = (randint(0,WIDTH), randint(0, HEIGHT)),
                                  energy = DESCENDANTS_ENERGY) for i in
               xrange(START_POPULATION)],
              size = (WIDTH, HEIGHT),
              offspring_energy = OFFSPRING_ENERGY,
              start_food = START_FOOD,
              start_keys = START_KEYS)

    # initialize pygame stuff
    pygame.init()
    fps_clock = pygame.time.Clock()
    window = pygame.display.set_mode((WIDTH, HEIGHT + CHART_HEIGHT))
    pygame.display.set_caption("Biotopia - Artificial Life Simulator")

    # colors
    cell_color = pygame.Color(0,255,50)
    head_color = pygame.Color(255,255,0)
    mouth_color = pygame.Color(0,0,70)
    die_color = pygame.Color(255,0,0)
    eating_color = pygame.Color(255,255,255)
    new_born_color = pygame.Color(255,255,255)
    food_color = pygame.Color(0,70,0)
    key_color = pygame.Color(70,70,0)
    background_color = pygame.Color(0,0,0)
    zoom_border_color = pygame.Color(100,100,100)
    text_color = pygame.Color(150,150,150)

    # fonts
    font_size = 20
    stats_font = pygame.font.Font(None, 20)

    # flags and control variables
    zooming = False
    paused = False
    cycle_count = 0

    # main loop
    while True:
        # clear zoo screen
        pygame.draw.rect(window, background_color, ((0,0),(WIDTH,HEIGHT+1)))

        # print each food particle
        for food in zoo.food.iter_unique():
            window.set_at(food, food_color)

        # print each key particle
        for key in zoo.keys.iter_unique():
            window.set_at(key, key_color)

        # print each creature
        for creature in zoo.creatures:

            if creature.age <= 0:
                color = new_born_color
            elif creature.energy <= 0:
                color = die_color
            else:
                color = cell_color

            # print each creature cell
            for cell in creature.cells:
                cell_position = (creature.position[0] + cell[0],
                                 creature.position[1] + cell[1])
                if 0 <= cell_position[0] <= WIDTH and 0 <= cell_position[1] <= HEIGHT:
                    window.set_at(cell_position, color)

            # print mouths and head only if not dieing or not new born
            if creature.energy > 0 and creature.age > 0:
                # print each creature mouth
                for mouth in creature.mouths:
                    mouth_position = (creature.position[0] + mouth[0],
                                   creature.position[1] + mouth[1])
                    if 0 <= mouth_position[0] <= WIDTH and 0 <= mouth_position[1] <= HEIGHT:
                        window.set_at(mouth_position,
                                      eating_color if mouth_position in zoo.food else mouth_color)

                # print creature's head
                window.set_at((creature.position[0] + creature.head[0],
                               creature.position[1] + creature.head[1]),
                              head_color)

        # draw zoom, if active
        if zooming:
            sample_point = (min(max(mouse_pos[0] - WIDTH/32, 0), WIDTH - WIDTH/16),
                            min(max(mouse_pos[1] - HEIGHT/32, 0), HEIGHT - HEIGHT/16))
            blit_point = (min(max(mouse_pos[0] - WIDTH/8, 0), WIDTH - WIDTH/4),
                          min(max(mouse_pos[1] - HEIGHT/8, 0), HEIGHT - HEIGHT/4))
            zoom_surface = pygame.transform.scale(
                                window.subsurface((sample_point,
                                                   (WIDTH/16, HEIGHT/16))),
                                (WIDTH/4, HEIGHT/4))

            window.blit(zoom_surface, blit_point)
            pygame.draw.rect(window, zoom_border_color,
                             (blit_point, (WIDTH/4, HEIGHT/4)), 1)

        # update screen and fps
        pygame.display.update()
        fps_clock.tick(60)

        # do stuff if not paused
        if not paused:

            # draw chart:
            # first, move chart left
            chart = window.subsurface(((1,HEIGHT+1),
                                       (CHART_WIDTH-1, CHART_HEIGHT-1))).copy()
            window.blit(chart, (0, HEIGHT+1))

            # do some math
            total_creatures = len(zoo.creatures)
            total_keys = len(zoo.keys)

            # then, print chart pixels
            pygame.draw.line(window, key_color,
                             (CHART_WIDTH-1, HEIGHT),
                             (CHART_WIDTH-1,
                              HEIGHT + (total_keys * CHART_HEIGHT /  POP_MAX)))
            pygame.draw.line(window, head_color,
                             (CHART_WIDTH-1, HEIGHT + CHART_HEIGHT),
                             (CHART_WIDTH-1,
                              HEIGHT+CHART_HEIGHT - (total_creatures * CHART_HEIGHT /  POP_MAX)))
            window.set_at((CHART_WIDTH-1, HEIGHT + CHART_HEIGHT/2),
                          background_color)

            # print some statistics: average age, average mouths, average energy
            if total_creatures > 0:
                average_age = sum(c.age for c in zoo.creatures) / float(total_creatures)
                average_mouths = sum(len(c.mouths) for c in zoo.creatures) / float(total_creatures)
                average_energy = sum(c.energy for c in zoo.creatures) / float(total_creatures)
            else:
                average_age = 0
                average_mouths = 0
                average_energy = 0

            text_age = stats_font.render("avr age: %.2f" % average_age,
                                         False, text_color, background_color)
            text_mouths = stats_font.render("avr mouths: %.2f" % average_mouths,
                                            False, text_color, background_color)
            text_energy = stats_font.render("avr energy: %.2f" % average_energy,
                                            False, text_color, background_color)
            text_pop    = stats_font.render("pop/keys: %d/%d" % (total_creatures, total_keys),
                                            False, text_color, background_color)
            text_cycle  = stats_font.render("cycle: %d" % cycle_count,
                                            False, text_color, background_color)

            pygame.draw.rect(window, background_color, ((CHART_WIDTH+1, HEIGHT+1),
                                                        (WIDTH - CHART_WIDTH,
                                                         CHART_HEIGHT)))
            window.blit(text_age,    (CHART_WIDTH+10, HEIGHT + 5))
            window.blit(text_mouths, (CHART_WIDTH+10, HEIGHT + 1*font_size + 5))
            window.blit(text_energy, (CHART_WIDTH+10, HEIGHT + 2*font_size + 5))
            window.blit(text_pop,    (CHART_WIDTH+10, HEIGHT + 3*font_size + 5))
            window.blit(text_cycle,  (CHART_WIDTH+10, HEIGHT + 4*font_size + 5))

            # update simulation
            zoo.step()

            # increment cycle_count
            cycle_count += 1

        # handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                zooming = True
            elif event.type == MOUSEBUTTONUP:
                zooming = False
            elif event.type == KEYDOWN and event.key == K_SPACE:
                paused = not paused

        # get mouse position
        mouse_pos = pygame.mouse.get_pos()

