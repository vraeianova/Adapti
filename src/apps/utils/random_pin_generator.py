import random


# Generate 5 random numbers between 1 to 9


def random_pin_generator():
    randomlist = random.sample(range(1, 9), 5)
    randomlist = "".join(map(str, randomlist))
    return randomlist
