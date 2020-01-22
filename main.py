import deap
import numpy
import sys
import time
import copy
import random
import numpy
import operator
import statistics
from itertools import chain
from functools import partial

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

from dao import get_ind_file
from strategy import StrategySimulator, prog2, prog3, progn, if_then_else


def runGame(individual):
    global strategy
    initial_portfolio_total = strategy.portfolio_value
    routine = gp.compile(individual, pset)
    strategy._reset()
    timer = 0

    while strategy.portfolio_value >= strategy.trade_value and not timer == strategy.max_iter-3:
        routine()
        strategy.update_index()
        timer += 1
    return (strategy.portfolio_value - initial_portfolio_total,)


def runGameAvg(individual):
    # averages = []
    # for x in range(4):
    #     res = runGame(individual)
    #     averages.append(res[0])

    # ret = sum(averages)/len(averages)
    # return ret,
    return runGame(individual)


def setup_toolbox():
    global pset
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)
    toolbox = base.Toolbox()
    toolbox.register("expr_init", gp.genHalfAndHalf, pset=pset, min_=1, max_=3)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr_init)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", runGameAvg)
    kwargs = {"fitness_size": 7, "parsimony_size": 1.3, "fitness_first": False}
    toolbox.register("select", tools.selDoubleTournament, **kwargs)
    kwargs = {"termpb": 0.1}
    toolbox.register("mate", gp.cxOnePointLeafBiased, **kwargs)
    toolbox.register("expr_mut", gp.genGrow, min_=1, max_=3)
    toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
    toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
    toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
    return toolbox

def create_pset():
    global strategy
    pset = gp.PrimitiveSet("MAIN", 0)
    pset.addPrimitive(prog2, 2)
    pset.addPrimitive(prog3, 3)
    pset.addPrimitive(strategy.if_rsi_under_limit, 2)
    pset.addPrimitive(strategy.if_rsi_over_limit, 2)

    pset.addTerminal(strategy.do_buy)
    pset.addTerminal(strategy.do_sell)
    pset.addTerminal(strategy.do_nothing)
    return pset

def add_stats():
    stats_fit = tools.Statistics(key=lambda ind: ind.fitness.values)
    mstats = tools.MultiStatistics(fitness=stats_fit)
    mstats.register("avg", numpy.mean, axis=0)
    mstats.register("std", numpy.std, axis=0)
    mstats.register("min", numpy.min, axis=0)
    mstats.register("max", numpy.max, axis=0)
    return mstats

def main(rseed):
    random.seed(rseed)
    global strategy
    prices = get_ind_file("WIKI/APPL")
    strategy = StrategySimulator(prices)

    global pset
    pset = create_pset()
    toolbox = setup_toolbox()
    pop = toolbox.population(n=200)
    stats = add_stats()
    hof = tools.HallOfFame(1)

    pop, log = algorithms.eaSimple(pop, toolbox, 0.9, 0.1, 120, stats=stats, halloffame=hof, verbose=True)
    
    epr = tools.selBest(hof, 1)[0]
    iterations = 3
    runs = [runGame(epr)[0] for x in range(iterations)]
    print("Best from pop, run {} times: {}".format(iterations, runs))
    print("Best from pop, avg: {}".format(sum(runs)/len(runs)))
    return runs


if __name__ == "__main__":
    # results = []
    # seeds = [random.randint(0, sys.maxsize) for i in range(SEED_SIZE)]
    # for seed in seeds:
    #     results.append(main(seed))

    seed = 72
    runs = main(72)
