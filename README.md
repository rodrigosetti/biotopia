# Biotopia

Biotopia is a simple Artificial Life Simulator inspired in a program of the
same name created by Anthony Liekens.

It works by letting creatures live in a simulated environment, where they must
compete for food and reproduction. Because of that competition we can observe a
statistics tendency of complexity increase in those creature's morphology.

## Command line arguments

    usage: biotopia.py [-h] [--width WIDTH] [--height HEIGHT]
                       [--ancestors-energy ENERGY] [--offspring-energy ENERGY]
                       [--energy-loss ENERGY] [--energy-gain ENERGY]
                       [--start-food AMOUNT] [--start-keys AMOUNT]
                       [--start-population AMOUNT]
                       [--mutation-probability PROPORTION] [--chart-update CYCLES]
                       [--wrap-vertically] [--wrap-horizontally]

    Biotopia - The Artificial Life Simulator

    optional arguments:
      -h, --help            show this help message and exit
      --width WIDTH, -wd WIDTH
                            the simulation environment width
      --height HEIGHT, -ht HEIGHT
                            the simulation environment height
      --ancestors-energy ENERGY, -a ENERGY
                            the amount of energy the ancestors starts with
      --offspring-energy ENERGY, -o ENERGY
                            at each reproduction, the amount of energy the
                            offspring starts with
      --energy-loss ENERGY, -l ENERGY
                            the quantity of energy lost at each creature's cycle
      --energy-gain ENERGY, -g ENERGY
                            the quantity of energy gain at each food eat
      --start-food AMOUNT, -f AMOUNT
                            the amount of food the simulation's environment starts
                            with
      --start-keys AMOUNT, -k AMOUNT
                            the amount of key particles the simulation's
                            environment starts with
      --start-population AMOUNT, -p AMOUNT
                            The number of ancestors the simulation starts with
      --mutation-probability PROPORTION, -m PROPORTION
                            The chance of random mutation at each reproduction
      --chart-update CYCLES, -c CYCLES
                            Update the population/keys chart period
      --wrap-vertically, -wv
                            Whether or not to wrap the environment vertically
      --wrap-horizontally, -wh
                            Whether or not to wrap the environment horizontally

## In simulation commands

  * Click over the environment: zoom area.
  * `space`: toggle pause simulation.
  * `r`: restart simulation.
  * `d`: toggle debug mode (show nearest creature energy and age, and some of
    the best creatures).
  * `h`: toggle horizontal wrapping.
  * `v`: toggle vertical wrapping.

## Main concepts

Creatures, in this simulator, are simple beings with a multi-cellular
structure.  The very arrangement of its cells determines both its movement
throughout the world, as well as it's capacity of eating and reproduce.

To live, each creature looses energy, therefore, they must eat to keep up
energy amount bigger than zero. If it ever reaches zero, the creature dies and
its transformed into food for other creatures to consume.

Reproduction is assexual by means of self-replication, and have a change of
random mutation (which means a single change in its structure). Creatures do
not interact directly with each other.

## The environment

There are two resources in the environment, represented as particles (pixels
dots) scattered all over the place. These are:

  * food - dark green pixels. They provide energy to the creature.
  * key particles - dark yellow pixels. They are the only source of reproduction.

Each creature is born with a limited amount of energy, and at each simulation
cycle, this energy is decreased by an amount (default is 1). When the
creature's energy reaches zero, it dies.

In order to rise its energy level, the creature must walk over the space and
"eat" the food particles (dark green). Upon eating, the food particle
disappears from the environment, and it's added a certain amount of energy
(default 10) to the creature.

When death occurs (energy reaches zero) the creature stops operating and its
structure is transformed in food particles and one key particle, which can be
consumed by other creatures.

The key particle (dark yellow pixels), when eat, replicates the creature -
creating an identical offspring, with change of random mutation - in place. The
new offspring will have a standard energy to start its life, and will have a
random rotation of -90 or +90 degrees. This is the only way a creature might
reproduce (by eating key particles).

Both food particles and key particles are created in the environment only when
a creature dies (except, of course, at the start of simulation).

The simulation can have two behaviours regarding the limits of the world:

  * wrapping - in this case, a creature, when reaching the border, will
    reappear in the other end an continue moving. When both vertical and
    horizontal wrapping are enabled, the world will have a torus topology.
  * collision - in this case, a creature, when reaching the border, will mirror
    horizontally (if reaching the width limit) or vertically (if reaching the
    heigth limit), therefore, changing its movement.

## Creatures
### Structure

Creature behaviour is governed by its structure. A creature structure can be
represented by a set of connected dots (called cells, green pixels). One of
this cells is a special one, and its called "head cell", colored yellow.

The head cell functions exactly as the other cells, so, it does not matter
which cell is the head. The only difference is that, upon death, all regular
cells are transformed into food particles, whist the head cell is transformed
into a key particle.

The creature structure must obey certain rules, they are:

  * All cells must be connected to the head.
  * There must not be cycles (i.e. starting from the head, and following
    neighbours, one cannot reach the same cell again).

By neighbours we mean only orthogonal, not diagonals.

With that rules in mind, let show some concrete valid and invalid examples (in
this examples, empty space is represented as `.`, and cells are represented as
`o`).

These are all valid examples:

    ..... ..... .....
    .o.o. .oo.. .o...
    .ooo. .o.o. .ooo.
    ..... .ooo. .o...
    ..... ..... .....

On the other hand, the following examples are invalid, because the contain
cycles:

    ..... ..... .....
    .o.o. .ooo. .ooo.
    .ooo. .o.o. .o.o.
    .oo.. .ooo. .ooo.
    ..... ..... .....

At each reproduction (i.e. key particle eating) the offspring will be an exact
copy of its parent, with a change of random mutation. A mutation is either
adding or removing a single cell in a way that does not yield an invalid
structure.

### Movement

Creatures move in the environment depending on its structure. The movement
depends solely on what is called "flagellum". These are cells that have only on
neighbour.

For example, the following structure has three flagellum, one faced upwards,
one faced left, and the other faced right:

    .....
    ..o..
    .ooo.
    .....

Each flagellum adds to a direction coefficient. In this example, the two
horizontal flagellum (left and right) rule out each other, thereby resulting in
a horizontal coefficient of zero. The upward flagellum adds a unbalanced
vertical coefficient (in this case, -1).

So, by summing up the flagellum directions, we came out with horizontal and
vertical coefficients. To sum up, we must consider that upward flagellum adds
-1 to the vertical coefficient, downwards flagellum adds 1 to the vertical
coefficient; left flagellum adds -1 to the horizontal coefficient, and right
flagellum adds 1 to horizontal coefficient.

The following examples have (0,-2), (1,-1), and (1, 0) of (horizontal,
vertical) coefficients respectively:

    ..... ..... .....
    .o.o. .oo.. .o...
    .ooo. .o.o. .ooo.
    ..... .ooo. .o...
    ..... ..... .....

At each cycle, a creature may walk only one pixel in each direction. The actual
move is draw from a creature's internal cyclic movement, that have the
following rule:

  * A creature always stands still one cycle (i.e. walk (0,0))
  * Then, at each i-th cycle, the creature will have a movement equals to
    `(sign(H) if i < |H| else 0, sign(V) if i < |V| else 0)`, for i from 1 to
    `max(|H|, |V|)`; Where `H` is the horizontal coefficient; `V` is the
    vertical coefficient; `sign(x)` is -1 if `x < 0`, 0 if `x = 0`, or 1
    otherwise; and `|x|` is the absolute value of `x`.

For example, for a horizontal x vertical coefficient of (-1,2), a creature will
have the following movement cycle:

  * (0, 0)
  * (-1, 1)
  * (0, 1)

For coefficients equal to (1,1), we'll have the following cycle:

  * (0, 0)
  * (1, 1)

Likewise, for coefficients equal to (1,-1), we'll have the following cycle:

  * (0, 0)
  * (1,-1)

For coefficients equal to (0,10), we'll have the following cycle:

  * (0, 0)
  * (0, 1)
  * (0, 1)
  * (0, 1)
  * (0, 1)
  * (0, 1)
  * (0, 1)
  * (0, 1)
  * (0, 1)
  * (0, 1)
  * (0, 1)

Note that, the bigger the coefficient, faster will be the movement of the
creature in that dimension, because it will less often stand still. Also, for a
creature to have perfect diagonal movement, it will have to have equal absolute
values of the horizontal and vertical coefficients. Finally, creatures that
have the coefficients equal to (0,0) will never move (that's a bad thing,
because it wont eat and reproduce - leading quickly to death).

### Eating

The structure of the creature also determines where are its "mouths". A
creature might have zero or more mouths. Mouth is a place in an neighbour empty
space where the creature can consume both food and key particles.

For a mouth to exist, the empty space should have at least three cell
neighbours (orthogonal neighbours might have at most four cell neighbours). It
doesn't matter if the cell is a regular (green) or head (yellow) type.

For example, in the following structures, we denote with an `*` the place where
a mouth exists:

    ..... ..... ..... .......
    .o*o. .oo.. .o... .o*o*o.
    .ooo. .o*o. .ooo. .ooooo.
    ..... .ooo. .o... ..o*o..
    ..... ..... ..... .......

A creature with zero mouths (third example in the previous row) will obviously
die pretty soon because it cannot eat food, and, because it cannot eat key
particles, will never reproduce. On the other hand, creatures with more mouths
than the average will have selective advantage because they'll more easily be
able to eat and reproduce.

## Evolution

The starting ancestral are creatures with the following structure:

    .....
    .o.o.
    .ooo.
    .....

They have one mouth and moving coefficients (0,-2), therefore, they move
vertically down. All the rotations of the ancestral also exists, so the
movements are variate, but all of them orthogonal.

Just to make things clear, the following creatures are all equivalent (i.e. the
same) (rotations and mirrors of the same structure):

    ...... ...... ..... ..... ..... ..... ...... ......
    .o.oo. .oo.o. .oo.. ..oo. ..o.. ...o. ..ooo. .ooo..
    .ooo.. ..ooo. .o... ...o. ..oo. ..oo. .oo.o. .o.oo.
    ...... ...... .oo.. ..oo. ...o. ..o.. ...... ......
    ...... ...... ..o.. ..o.. ..oo. ..oo. ...... ......
    ...... ...... ..... ..... ..... ..... ...... ......

The environment is started with some of them, and some amount of free food and
key particles scattered around the world.

Pretty soon, we observe that the descendants will show a tendency to increse
complexity of its structure by incorporating more mouths and better movements
strategies (i.e. faster and diagonals).

