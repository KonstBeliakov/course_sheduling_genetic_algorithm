import random
from copy import deepcopy
from pandas._libs.tslibs import timestamps


# Encoding schedule with list of pairs of exam and timeinterval for it
def initial_population(population_size: int, exam_ids: list):
    population = []
    timestamps = 1 + len(exam_ids) // 2 # At the beginning there will be 5 exams on average at the same time
    for i in range(population_size):
        item = [[exam, random.randrange(timestamps)] for exam in exam_ids]

        population.append(item)

    # for i in range(population_size):
    #     random.shuffle(exam_ids)
    #     population.append([[i, exam] for i, exam in enumerate(exam_ids)])
    return population


def genome_to_schedule(genome: list):
    time_to_exam = {}
    for exam, time in genome:
        if time not in time_to_exam:
            time_to_exam[time] = set()
        time_to_exam[time].add(exam)
    return time_to_exam


def fitness_function(genome: list):
    # We will give -1000 point for each pair of exams that cant be held at the same time
    global banned_list
    time_to_exam = genome_to_schedule(genome)
    fittness = 0
    for time in time_to_exam:
        for exam1 in time_to_exam[time]:
            if exam1 in banned_list:
                for exam2 in time_to_exam[time]:
                    if exam2 in banned_list[exam1]:
                        fittness -= 1000

    # Let's get -1 point for each timeinterval that we have
    fittness -= max(time_to_exam)

    return fittness


def selection(population: list[list[int]], fitnesses: list[int], k: int = 3) -> list[int]:
    """Select one parent using tournament selection."""
    indices = random.sample(range(len(population)), k)
    best_idx = max(indices, key=lambda i: fitnesses[i])
    return population[best_idx][:]


def recombination(parent1: list, parent2: list, recombination_rate: float):
    if random.random() > recombination_rate:
        return deepcopy(parent1), deepcopy(parent2)
    child1, child2 = [], []
    for gene1, gene2 in zip(parent1, parent2):
        if random.randrange(2):
            child1.append(gene1.copy())
            child2.append(gene2.copy())
        else:
            child1.append(gene2.copy())
            child2.append(gene1.copy())
    return child1, child2


def mutation(individual: list, mutation_rate: float):
    for gene in individual:
        if random.random() < mutation_rate:
            if gene[1] == 0:
                gene[1] = 1
            else:
                gene[1] += 1 if random.randrange(2) else -1


def print_schedule(genome: list[tuple[int, int]]):
    time_to_exam = genome_to_schedule(genome)
    for time in sorted(time_to_exam):
        print(f'{time}:', ' '.join(map(str, time_to_exam[time])))


filename = 'problems/hec-s-92.stu'

stu = []
exam_to_students = {}
banned_list = {} # which exams could not be held at the same time
exam_ids = set()

with open(filename, 'r') as f:
    for student, line in enumerate(f.readlines()):
        exams = {int(i) for i in line.split()}
        stu.append(exams)
        for exam in exams:
            exam_ids.add(exam)
            if exam not in banned_list:
                banned_list[exam] = set()
            for exam2 in exams:
                if exam != exam2:
                    banned_list[exam].add(exam2)

            if exam not in exam_to_students:
                exam_to_students[exam] = set()
            exam_to_students[exam].add(student)
exam_ids = list(exam_ids)

# print(stu[:10])
# for i in sorted(exam_to_students):
#     print(i, exam_to_students[i])



def genetic_algorithm(pop_size: int = 100,
                      max_generations: int = 500,
                      crossover_prob: float = 0.8,
                      mutation_rate_begin: float = 0.7,
                      mutation_rate_end: float = 0.05,
                      tournament_k: int = 3,
                      verbose: bool = True):
    """
    Run the genetic algorithm and return:
    - best individual found,
    - its fitness,
    - generation index when the optimum was first reached (or None if not reached).
    """
    # 1) Initialise population
    global exam_ids
    population = initial_population(pop_size, exam_ids)

    best_individual = None
    best_fitness = float("-inf")
    success_generation = None  # will stay None if we never hit the optimum

    for gen in range(max_generations):
        # 2) Evaluate fitness
        fitnesses = [fitness_function(ind) for ind in population]

        # 3) Update global best
        idx = max(range(len(population)), key=lambda i: fitnesses[i])
        if best_fitness < fitnesses[idx]:
            best_individual = population[idx]
            best_fitness = fitnesses[idx]

        if verbose and gen % 10 == 0:
            print(f"Generation {gen:3d}: best fitness = {best_fitness}")

        # 4) Check for perfect solution
        if best_fitness == 0:
            success_generation = gen
            if verbose:
                print(f"Solution found at generation {gen}!")
            break

        # 5) Create new population
        new_population: list[list[int]] = []

        current_mutation_rate = (mutation_rate_end * (max_generations - gen) + mutation_rate_begin * gen) / max_generations

        while len(new_population) < pop_size:
          p1 = selection(population, fitnesses, tournament_k)
          p2 = selection(population, fitnesses, tournament_k)
          c1, c2 = recombination(p1, p2, crossover_prob)
          mutation(c1, current_mutation_rate)
          mutation(c2, current_mutation_rate)
          new_population.append(c1)
          new_population.append(c2)

        population = new_population

    return best_individual, best_fitness, success_generation

# After you implement all TODOs:
best, best_f, gen_succ = genetic_algorithm()
print("Best fitness:", best_f)
print("Success generation:", gen_succ)
print_schedule(best)
