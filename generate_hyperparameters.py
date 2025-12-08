import json

import optuna

from oop_genetic_algorithm import genetic_algorithm


def objective(trial):
    global best_fitness, best_hyperparameters

    pop_size = trial.suggest_int("pop_size", 20, 300)
    mutation_rate_begin   = trial.suggest_float("mutation_rate_begin", 0.001, 0.5, log=True)
    mutation_rate_end = trial.suggest_float("mutation_rate_end", 0.0001, 0.1, log=True)
    crossover_prob  = trial.suggest_float("crossover_prob", 0.1, 1.0)
    tournament_k = trial.suggest_int("tournament_k", 2, 20)

    hyperparams = {
        "pop_size": pop_size,
        "mutation_rate_begin": mutation_rate_begin,
        "mutation_rate_end": mutation_rate_end,
        "crossover_prob": crossover_prob,
        "tournament_k": tournament_k,
    }

    best_individual, fitness, _ = genetic_algorithm(verbose=False, **hyperparams)

    return fitness


if __name__ == '__main__':
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=50)

    print("Best params:", study.best_params)
    print("Best fitness:", study.best_value)

    with open("best_params.json", "w", encoding='utf-8') as f:
        json.dump(study.best_params, f, indent=4)
