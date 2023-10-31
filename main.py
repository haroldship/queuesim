import simpy
from typing import Callable
from functools import partial
import numpy.random as npr


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


def exponential_time(lam):
    return npr.exponential(1.0/lam)


def service(env: simpy.Environment, q: simpy.Resource, reqno: int, stime: float):
    with q.request() as request:
        yield request
        yield env.timeout(stime)
        print(f'stime: {reqno} {stime} {env.now}')


def arrival_process(env: simpy.Environment, q: simpy.Resource, Q0:int, arrival_time: Callable, service_time: Callable):
    reqno = Q0
    while True:
        atime = arrival_time()
        stime = service_time()
        reqno += 1
        yield env.timeout(atime)
        env.process(service(env, q, reqno, stime))
        print(f'arrival: {reqno} {atime} {env.now}')


def run_simulation(mc: int, T:float, Q0:int, interarrival_time: Callable, service_time: Callable):
    print(f'iteration: {mc}')
    env = simpy.Environment()
    q = simpy.Resource(env, 1)
    for reqno in range(Q0):
        stime = service_time()
        env.process(service(env, q, reqno, stime))
    env.process(arrival_process(env, q, Q0, interarrival_time, service_time))
    env.run(T)


def run_simulations(MC: int, T:float, Q0:int, interarrival_time: Callable, service_time: Callable):
    for mc in range(MC):
        run_simulation(mc, T, Q0, interarrival_time, service_time)


MC=1
T=1.0
lam=2.0
mu=5.0
Q0=10

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    npr.seed(1)
    interarrival_time = partial(exponential_time, lam)
    service_time = partial(exponential_time, mu)

    run_simulations(MC, T, Q0, interarrival_time, service_time)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
