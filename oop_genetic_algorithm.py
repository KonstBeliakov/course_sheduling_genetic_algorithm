import random
from copy import deepcopy

random.seed(39)
MUTATE_DOWN_PROBABILITY = 0.5
POP_SIZE = 20
MAX_GENERATIONS = 500
MUTATION_RATE_BEGIN = 0.1
MUTATION_RATE_END = 0.01
CROSSOWER_PROB = 0.2  # 0.8 for elitism
TOURNAMENT_K = 3


class Genome:
    def __init__(self, exam_time: list[int]):
        self.time = exam_time

    def mutate(self, mutation_rate: float, banned_list: dict):
        """Smart mutation that checks for hard conditions for the schedule"""
        for exam_id in range(len(self.time)):
            if random.random() < mutation_rate:
                current_time = self.time[exam_id]

                new_time = current_time + (1 if random.random() > MUTATE_DOWN_PROBABILITY else -1)
                new_time = max(0, new_time)

                conflicts = False
                for other_exam in range(len(self.time)):
                    if other_exam != exam_id and self.time[other_exam] == new_time:
                        if other_exam in banned_list.get(exam_id, set()):
                            conflicts = True
                            break

                if not conflicts:
                    self.time[exam_id] = new_time

    def schedule(self) -> list[set[int]]:
        # print(self.time)
        # print(max(self.time))
        max_time = max(self.time)
        time_to_exam = [set() for _ in range(max_time + 1)]
        for exam_id, exam_time in enumerate(self.time):
            time_to_exam[exam_time].add(exam_id)
        return time_to_exam

    def fitness(self, banned_list: list[set[int]]) -> int:
        # We will give -1000 point for each pair of exams that cant be held at the same time
        time_to_exam = self.schedule()
        fittness = 0
        for time in range(len(time_to_exam)):
            for exam1 in time_to_exam[time]:
                if exam1 in banned_list:
                    for exam2 in time_to_exam[time]:
                        if exam2 in banned_list[exam1]:
                            fittness -= 1000

        # Getting -2 points for each empty timeinterval
        # for i in range(len(time_to_exam)):
        #     if not time_to_exam[i]:
        #         fittness -= 2

        # Let's get -1 point for each timeinterval that we have
        fittness -= len(time_to_exam)

        return fittness

    def remove_empty_spots(self):
        schedule = self.schedule()
        new_schedule = [i for i in schedule if i]
        max_time = max([max(i) for i in new_schedule])
        new_genome = [0 for _ in range(max_time + 1)]
        for time in range(len(new_schedule)):
            for e in new_schedule[time]:
                new_genome[e] = time
        self.time = new_genome


def random_genome(exam_number: int) -> Genome:
    genome = list(range(exam_number))
    random.shuffle(genome)
    return Genome(genome)

def recombination(parent1: Genome, parent2: Genome, recombination_rate: float) -> tuple[Genome, Genome]:
    if random.random() > recombination_rate:
        return deepcopy(parent1), deepcopy(parent2)
    child1, child2 = [], []
    for time1, time2 in zip(parent1.time, parent2.time):
        if random.randrange(2):
            child1.append(time1)
            child2.append(time2)
        else:
            child1.append(time2)
            child2.append(time1)
    return Genome(child1), Genome(child2)

def selection(population: list[Genome], fitnesses: list[int], k: int = 3) -> Genome:
    """Select one parent using tournament selection."""
    indices = random.sample(range(len(population)), k)
    best_idx = max(indices, key=lambda i: fitnesses[i])
    return deepcopy(population[best_idx])


def print_schedule(genome: Genome):
    time_to_exam = genome.schedule()
    for time in range(len(time_to_exam)):
        print(f'{time}:', ' '.join([str(i) for i in time_to_exam[time]]))


filename = 'problems/car-f-92.stu'  # 'problems/hec-s-92.stu'

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


def genetic_algorithm(pop_size: int = POP_SIZE,
                      max_generations: int = MAX_GENERATIONS,
                      crossover_prob: float = CROSSOWER_PROB,
                      mutation_rate_begin: float = MUTATION_RATE_BEGIN,
                      mutation_rate_end: float = MUTATION_RATE_END,
                      tournament_k: int = TOURNAMENT_K,
                      verbose: bool = True):
    """
    Run the genetic algorithm and return:
    - best individual found,
    - its fitness,
    - generation index when the optimum was first reached (or None if not reached).
    """
    # 1) Initialise population
    global exam_ids
    population: list[Genome] = [random_genome(len(exam_ids)) for _ in range(pop_size)]

    best_individual = None
    best_fitness = float("-inf")
    success_generation = None  # will stay None if we never hit the optimum

    for gen in range(max_generations):
        # 2) Evaluate fitness
        for genome in population:
            genome.remove_empty_spots()
        fitnesses = [ind.fitness(banned_list) for ind in population]

        # 3) Update global best
        idx = max(range(len(population)), key=lambda i: fitnesses[i])
        if best_fitness < fitnesses[idx]:
            best_individual = population[idx]
            best_fitness = fitnesses[idx]

        if verbose and gen % 10 == 0:
            print(f"Generation {gen:3d}: best fitness = {best_fitness}")
            if gen % 50 == 0:
                print(f"{fitnesses[idx]}")
                print_schedule(population[idx])
                print('\n\n')

        # 4) Check for perfect solution
        if best_fitness == 0:
            success_generation = gen
            if verbose:
                print(f"Solution found at generation {gen}!")
            break

        # 5) Create new population
        new_population: list[Genome] = []

        current_mutation_rate = (mutation_rate_end * (max_generations - gen) + mutation_rate_begin * gen) / max_generations

        while len(new_population) < pop_size:
          p1 = selection(population, fitnesses, tournament_k)
          p2 = selection(population, fitnesses, tournament_k)
          c1, c2 = recombination(p1, p2, crossover_prob)
          c1.mutate(current_mutation_rate, banned_list)
          c2.mutate(current_mutation_rate, banned_list)
          new_population.append(c1)
          new_population.append(c2)

        population = new_population

    return best_individual, best_fitness, success_generation

# After you implement all TODOs:
best, best_f, gen_succ = genetic_algorithm()
print("Best fitness:", best_f)
print("Success generation:", gen_succ)
print_schedule(best)