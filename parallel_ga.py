import random

# Basic GA search space for traffic timing
POPULATION_SIZE = 10
MUTATION_RATE = 0.1


def create_random_solution():
    return [random.randint(10, 60), random.randint(10, 60), random.randint(0, 1)]


def crossover(parent1, parent2):
    return [parent1[0], parent2[1], parent2[2]]


def mutate(solution):
    if random.random() < MUTATION_RATE:
        gene = random.randint(0, 2)
        if gene == 0:
            solution[0] = random.randint(10, 60)
        elif gene == 1:
            solution[1] = random.randint(10, 60)
        else:
            solution[2] = 1 if solution[2] == 0 else 0
    return solution
