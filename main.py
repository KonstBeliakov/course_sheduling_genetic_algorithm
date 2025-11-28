import random


# Encoding schedule with list of pairs of exam and timeinterval for it
def initial_population(n: int, exam_ids: list):
    population = []
    timestamps = 1 + len(exam_ids) // 5 # At the beginning there will be 5 exams on average at the same time
    for i in range(n):
        item = [[exam, random.randrange(timestamps)] for exam in exam_ids]

        population.append(item)

def fitness_function(schedule: list):
    raise NotImplementedError

def selection(population: list):
    raise NotImplementedError

def recombination(parent1: list, parent2: list, recombination_rate: float):
    if random.random() > recombination_rate:
        return parent1, parent2
    child1, child2 = [], []
    for gene1, gene2 in zip(parent1, parent2):
        if random.randrange(2):
            child1.append(gene1)
            child2.append(gene2)
        else:
            child1.append(gene2)
            child2.append(gene1)
    return child1, child2

def mutation(individual: list, mutation_rate: float):
    raise NotImplementedError


filename = 'problems/car-f-92.crs'

stu = []
exam_to_students = {}
banned_list = {} # which exams could not be held at the same time

with open(filename, 'r') as f:
    for student, line in enumerate(f.readlines()):
        exams = {int(i) for i in line.split()}
        stu.append(exams)
        for exam in exams:
            if exam not in banned_list:
                banned_list[exam] = set()
            if exam not in exam_to_students:
                exam_to_students[exam] = set()
            exam_to_students[exam].add(student)


print(stu[:10])
for i in sorted(exam_to_students):
    print(i, exam_to_students[i])
