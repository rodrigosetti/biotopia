#! /usr/bin/env python
# coding: utf-8

"""
Biotopia is a simple Artificial Life Simulator inspired in a program of the
same name created by Anthony Liekens.

It works by letting creatures live in a simulated environment, where they must
compete for food and reproduction. Because of that competition we can observe a
statistical tendency of complexity increase in the population's morphology.

Please see accompanied README.
"""

__author__ = "Rodrigo Setti"
__all__ = ["Creature", "Zoo", "ancestor"]

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
    "Return -1 if x < 0; 0 if x == 0; and 1 otherwise"
    if x < 0:
        return -1
    elif x == 0:
        return 0
    else:
        return 1

def distance(a, b):
    "Calculates the squared distance of two bi-dimensional points"
    return (a[0]-b[0])**2 + (a[1]-b[1])**2

class Creature(object):
    """
    A Creature object holds the creature's structure, which is composed of a
    set of (x,y) of its cells, relative to its head (which is (0,0)).
    Also, some state information such as energy, age, and position.
    """

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
        Find out the movement and the mouths from the structure. Must be called
        each time the structure changes.
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

def ancestor(position=(0,0), energy=0):
    """
    Return a random oriented default root ancestor.
    """
    creature = Creature(position, ((-1,1), (-1,0), (0,0), (1,0), (1,1)),
                          head=(0,0),
                          energy=energy)

    # perform a random rotation
    r = randint(1,4)
    if r == 1:
        creature.rotate_right()
    elif r == 2:
        creature.rotate_left()
    elif r == 3:
        creature.mirror_vertical()

    # let creature with a random movement cycle
    for x in xrange(randint(0,2)):
        next(creature.movement)

    return creature

class MultiSet(object):
    """
    Implements a multi-set. Each element can appear more than once, therefore,
    add operations and remove operations must be called the same amount for each
    element in order for it not be contained in set.
    """

    def __init__(self, iterable = []):
        self.items = {}
        for value in iterable:
            self.add(value)

    def __contains__(self, value):
        return self.items.get(value, 0) > 0

    def __len__(self):
        return sum(self.items.itervalues())

    def add(self, value):
        "adds this value to the set, incrementing the value's count"
        self.items[value] = self.items.get(value, 0) + 1

    def remove(self, value):
        "remove this value from the set, decrementing the value's count"
        self.items[value] = self.items.get(value, 0) - 1
        if self.items[value] == 0:
            del self.items[value]

    def __iter__(self):
        for value, count in self.items.iteritems():
            for i in xrange(count):
                yield value

    def iter_unique(self):
        """
        iterate over the unique values of the set, not repeating if the same
        value occurs more than once in the set.
        """
        for value, count in self.items.iteritems():
            if count > 0:
                yield value

    def __repr__(self):
        return "<multiset %s>" % ','.join(iter(self))

class Zoo(object):
    """
    Holds a complete simulation with a set of creatures, foods and key
    particles.
    """

    def __init__(self, descendants, size,
                 offspring_energy,
                 start_food, start_keys,
                 energy_loss=1, energy_gain=10,
                 wrap_vertical=False, wrap_horizontal=False,
                 mutation_probability = 0.2):
        self.creatures = set(descendants)
        self.size = size
        self.offspring_energy = offspring_energy
        self.energy_loss = energy_loss
        self.energy_gain = energy_gain
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
            creature.energy -= self.energy_loss
            creature.age += 1

            for mouth in creature.mouths:
                # calculate absolute mouth position
                mouth_position = (mouth[0] + creature.position[0],
                                  mouth[1] + creature.position[1])

                if mouth_position in self.food:
                    # remove food particle from soup
                    self.food.remove(mouth_position)

                    # increment creature's energy
                    creature.energy += self.energy_gain
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
    from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, QUIT, K_SPACE, K_r, K_d, KEYDOWN
    import argparse

    # parse arguments, possibly replacing default values
    parser = argparse.ArgumentParser(description="Biotopia - The Artificial Life Simulator")
    parser.add_argument('--width', '-wd', default=800, type=int, metavar='WIDTH',
                        dest='width', help='the simulation environment width')
    parser.add_argument('--height', '-ht', default=600, type=int, metavar='HEIGHT',
                        dest='height', help='the simulation environment height')
    parser.add_argument('--ancestors-energy', '-a', default=2000, type=int, metavar='ENERGY',
                        dest='ancestors_energy', help='the amount of energy the ancestors starts with')
    parser.add_argument('--offspring-energy', '-o', default=1000, type=int, metavar='ENERGY',
                        dest='offspring_energy', help='at each reproduction, the amount of energy the offspring starts with')
    parser.add_argument('--energy-loss', '-l', default=1, type=int, metavar='ENERGY',
                        dest='energy_loss', help="the quantity of energy lost at each creature's cycle")
    parser.add_argument('--energy-gain', '-g', default=10, type=int, metavar='ENERGY',
                        dest='energy_gain', help="the quantity of energy gain at each food eat")
    parser.add_argument('--start-food', '-f', default=50000, type=int, metavar='AMOUNT',
                        dest='start_food', help="the amount of food the simulation's environment starts with")
    parser.add_argument('--start-keys', '-k', default=250, type=int, metavar='AMOUNT',
                        dest='start_keys', help="the amount of key particles the simulation's environment starts with")
    parser.add_argument('--start-population', '-p', default=250, type=int, metavar='AMOUNT',
                        dest='start_population', help="The number of ancestors the simulation starts with")
    parser.add_argument('--mutation-probability', '-m', default=0.2, type=float, metavar='PROPORTION',
                        dest='mutation_probability', help="The chance of random mutation at each reproduction")
    parser.add_argument('--chart-update', '-c', default=10, type=int, metavar='CYCLES',
                        dest='chart_update', help="Update the population/keys chart period")
    parser.add_argument('--wrap-vertically', '-wv', default=False, action='store_true',
                        dest='wrap_vertically', help="Whether or not to wrap the environment vertically")
    parser.add_argument('--wrap-horizontally', '-wh', default=False, action='store_true',
                        dest='wrap_horizontally', help="Whether or not to wrap the environment horizontally")
    args = parser.parse_args()

    #: the maximum amount of population or keys
    POP_MAX = args.start_keys + args.start_population
    width = args.width
    height = args.height
    chart_update = args.chart_update

    # the width and height of the population/keys chart, located right under
    # the creature's environment. Statistics text will be displayed at the
    # right of the chart.
    chart_height = 100
    chart_width = width - 200

    # convenient function to start a new simulation
    def start_new_simulation():
        return Zoo([ancestor(position = (randint(0,width), randint(0, height)),
                             energy = args.ancestors_energy) for i in
                    xrange(args.start_population)],
                   size = (width, height),
                   offspring_energy = args.offspring_energy,
                   start_food = args.start_food,
                   start_keys = args.start_keys,
                   energy_loss = args.energy_loss,
                   energy_gain = args.energy_gain,
                   wrap_horizontal = args.wrap_horizontally,
                   wrap_vertical = args.wrap_vertically,
                   mutation_probability = args.mutation_probability)

    # initialize simulation
    zoo = start_new_simulation()

    # initialize pygame stuff
    pygame.init()
    fps_clock = pygame.time.Clock()
    window = pygame.display.set_mode((width, height + chart_height))
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
    stats_font = pygame.font.SysFont("monospace", 12)

    # flags and control variables
    zooming = False
    debugging = False
    paused = False
    nearest = None
    cycle_count = 0

    # main loop
    while True:
        # clear zoo screen
        pygame.draw.rect(window, background_color, ((0,0),(width,height+1)))

        # print each food particle
        for food in zoo.food.iter_unique():
            if 0 <= food[0] <= width and 0 <= food[1] <= height:
                window.set_at(food, food_color)

        # print each key particle
        for key in zoo.keys.iter_unique():
            window.set_at(key, key_color)

        # print each creature
        for creature in zoo.creatures:

            if debugging and creature is nearest:
                color = (255,255,255)
            elif creature.age <= 0:
                color = new_born_color
            elif creature.energy <= 0:
                color = die_color
            else:
                color = cell_color

            # print each creature cell
            for cell in creature.cells:
                cell_position = (creature.position[0] + cell[0],
                                 creature.position[1] + cell[1])
                if 0 <= cell_position[0] <= width and 0 <= cell_position[1] <= height:
                    window.set_at(cell_position, color)

            # print mouths and head only if not dieing or not new born
            if creature.energy > 0 and creature.age > 0:
                # print each creature mouth
                for mouth in creature.mouths:
                    mouth_position = (creature.position[0] + mouth[0],
                                   creature.position[1] + mouth[1])
                    if 0 <= mouth_position[0] <= width and 0 <= mouth_position[1] <= height:
                        window.set_at(mouth_position,
                                      eating_color if mouth_position in zoo.food else mouth_color)

                # print creature's head
                window.set_at((creature.position[0] + creature.head[0],
                               creature.position[1] + creature.head[1]),
                              head_color)

        # do some math
        total_creatures = len(zoo.creatures)
        total_keys = len(zoo.keys)

        # draw zoom, if active
        if zooming:
            sample_point = (min(max(mouse_pos[0] - width/32, 0), width - width/16),
                            min(max(mouse_pos[1] - height/32, 0), height - height/16))
            blit_point = (min(max(mouse_pos[0] - width/8, 0), width - width/4),
                          min(max(mouse_pos[1] - height/8, 0), height - height/4))
            zoom_surface = pygame.transform.scale(
                                window.subsurface((sample_point,
                                                   (width/16, height/16))),
                                (width/4, height/4))

            window.blit(zoom_surface, blit_point)
            pygame.draw.rect(window, zoom_border_color,
                             (blit_point, (width/4, height/4)), 1)

        # print the nearest creature's information, if debugging:
        if debugging and total_creatures > 0:
            # find out nearest creature energy and age
            nearest = min(zoo.creatures, key=lambda c: distance(c.position, mouse_pos))
            energy_text = stats_font.render("e: %d" % nearest.energy, False, text_color)
            age_text =    stats_font.render("a: %d" % nearest.age, False, text_color)
            status_width = max(energy_text.get_width(), age_text.get_width())
            status_height = font_size + age_text.get_height()

            # print information alongside the creature
            blit_pos = (nearest.position[0] + 10 if nearest.position[0] + 10 + status_width < width else nearest.position[0] - 10 - status_width,
                        nearest.position[1] + 10 if nearest.position[1] + 10 + status_height < height else nearest.position[1] - 10 - status_height)
            window.blit(energy_text, blit_pos)
            window.blit(age_text, (blit_pos[0], blit_pos[1] + font_size))

        # update screen and fps
        pygame.display.update()
        fps_clock.tick(60)

        # do stuff if not paused
        if not paused:
            # draw chart:
            if cycle_count % chart_update == 0:
                # first, move chart left
                chart = window.subsurface(((1,height+1),
                                           (chart_width-1, chart_height-1))).copy()
                window.blit(chart, (0, height+1))

                # then, print chart pixels
                pygame.draw.line(window, key_color,
                                 (chart_width-1, height),
                                 (chart_width-1,
                                  height + (total_keys * chart_height /  POP_MAX)))
                pygame.draw.line(window, head_color,
                                 (chart_width-1, height + chart_height),
                                 (chart_width-1,
                                  height+chart_height - (total_creatures * chart_height /  POP_MAX)))
                window.set_at((chart_width-1, height + chart_height/2),
                              background_color)

            # print some statistics: average age, average mouths, average energy
            if total_creatures > 0:
                min_age = min(c.age for c in zoo.creatures)
                max_age = max(c.age for c in zoo.creatures)
                average_age = sum(c.age for c in zoo.creatures) / float(total_creatures)

                creature_mouths = [len(c.mouths) for c in zoo.creatures]
                min_mouths = min(creature_mouths)
                max_mouths = max(creature_mouths)
                average_mouths = sum(creature_mouths) / float(total_creatures)

                min_energy = min(c.energy for c in zoo.creatures)
                max_energy = min(c.energy for c in zoo.creatures)
                average_energy = sum(c.energy for c in zoo.creatures) / float(total_creatures)
            else:
                average_age = max_age = min_age = 0
                average_mouths = max_mouths = min_mouths = 0
                average_energy = max_energy = min_energy = 0

            text_age = stats_font.render("age: %04d %04.2f %04d" % (min_age, average_age, max_age),
                                         False, text_color, background_color)
            text_mouths = stats_font.render("mouths: %04d %04.2f %04d" % (min_mouths, average_mouths, max_mouths),
                                            False, text_color, background_color)
            text_energy = stats_font.render("energy: %04d %04.2f %04d" % (min_energy, average_energy, max_energy),
                                            False, text_color, background_color)
            text_pop    = stats_font.render("pop/keys: %04d/%04d" % (total_creatures, total_keys),
                                            False, text_color, background_color)
            text_cycle  = stats_font.render("cycle: %08d" % cycle_count,
                                            False, text_color, background_color)

            pygame.draw.rect(window, background_color, ((chart_width+1, height+1),
                                                        (width - chart_width,
                                                         chart_height)))
            window.blit(text_age,    (chart_width+10, height + 5))
            window.blit(text_mouths, (chart_width+10, height + 1*font_size + 5))
            window.blit(text_energy, (chart_width+10, height + 2*font_size + 5))
            window.blit(text_pop,    (chart_width+10, height + 3*font_size + 5))
            window.blit(text_cycle,  (chart_width+10, height + 4*font_size + 5))

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
                # toggle pausing
                paused = not paused
            elif event.type == KEYDOWN and event.key == K_d:
                # toggle debugging
                debugging = not debugging
            elif event.type == KEYDOWN and event.key == K_r:
                # start new simulation!
                window.fill(background_color)
                zoo = start_new_simulation()
                cycle_count = 0

        # get mouse position
        mouse_pos = pygame.mouse.get_pos()

