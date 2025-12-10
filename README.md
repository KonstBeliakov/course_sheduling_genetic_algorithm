This project is a genetic algorithm for generating schedules.

**Genome**: gene with number i has index of time interval corresponding to the exam with index i  

**Fitness function**: big penalty for each pair of exams that are handled at the same time and share the same student.
Small penalty for the number of used time intervals (we want to create a compact schedule, and we don't want to stretch out the exam period over several months)

**Selection**: tournament selection with coefficient k

**Recombination**: for each exam choosing the timestamp from one of the parents. 
Because recombination very often breaks schedule (creates many pairs of exams which are held at the same time, but should not) I set the recombination rate to the 0.2)

**Mutation**: each exam could change its time interval to the neighbouring one. 
Decreasing the mutation rate with each generation for fast convergence at the beginning and finding local minimum (and not just jumping around) at the end.

##### Hyperparameters
- To optimize hyperparameters I used `optuna` library. After 50 trials it produced this:
```json
{
    "pop_size": 279,
    "mutation_rate_begin": 0.4393080313063388,
    "mutation_rate_end": 0.007496253380755332,
    "crossover_prob": 0.10453288265950048,
    "tournament_k": 12
}
```
As I expected, the recombination rate is very low, because recombination very often breaks the schedule, and if most of 
schedules are broken, then the algorithm may never recover. At the beginning mutation rate is very high 
(schedules need to be changed a lot and most of changes are improving the result, because at the start we put every exam into its own time interval),
at the end the mutation rate is low, because most of changes are breaking the schedule.