import simpy
from typing import Callable
from functools import partial
import numpy as np
import numpy.random as npr
import matplotlib.pyplot as plt


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


def exponential_time(lam):
    return npr.exponential(1.0/lam)


def service(env: simpy.Environment, q: simpy.Resource, reqno: int, stime: float):
    with q.request() as request:
        yield request
        yield env.timeout(stime)
        # print(f'stime: {reqno} {stime} {env.now}')


def arrival_process(env: simpy.Environment, q: simpy.Resource, Q0:int, arrival_time: Callable, service_time: Callable):
    reqno = Q0
    while True:
        atime = arrival_time()
        stime = service_time()
        reqno += 1
        yield env.timeout(atime)
        env.process(service(env, q, reqno, stime))
        # print(f'arrival: {reqno} {atime} {env.now}')


def run_simulation(mc: int, T:float, Q0:int, interarrival_time: Callable, service_time: Callable):
    # print(f'iteration: {mc}')
    env = simpy.Environment()
    q = simpy.Resource(env, 1)
    for reqno in range(Q0):
        stime = service_time()
        env.process(service(env, q, reqno, stime))
    env.process(arrival_process(env, q, Q0, interarrival_time, service_time))
    env.process(log(logs, env, mc, T, delta_t, q))
    env.run(T)


def run_simulations(MC: int, T:float, Q0:int, interarrival_time: Callable, service_time: Callable):
    for mc in range(MC):
        run_simulation(mc, T, Q0, interarrival_time, service_time)


logs = list()


def log(logs: list, env: simpy.Environment, mc: int, T: float, delta_t: float, q: simpy.Resource):
    K = int(T / delta_t) + 1
    mclogs = list()
    logs.append(mclogs)
    for k in range(K):
        mclogs.append((mc, k, env.now, len(q.queue)+q.count))
        yield env.timeout(delta_t)

MC=500
T=100.0
lam=20.0
mu=30.0
Q0=100
delta_t = 1.0
eta = 0.2

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    npr.seed(1)
    interarrival_time = partial(exponential_time, lam)
    service_time = partial(exponential_time, mu*eta)

    run_simulations(MC, T, Q0, interarrival_time, service_time)

    mu_hats = list()
    t_ests = list()
    for mc in range(MC):
        mclogs = logs[mc]
        K = len(mclogs)
        k1, k2 = sorted(npr.choice(K, 2, replace=False))
        l1, l2 = mclogs[k1], mclogs[k2]
        q1, q2 = l1[3], l2[3]
        t1, t2 = l1[2], l2[2]
        t_est = t2 - t1
        mu_hat = -1.0/(eta*(t_est))*(q2-q1-lam*(t_est))
        mu_hats.append(mu_hat)
        t_ests.append(t_est)
    print(np.mean(mu_hats))
    print(np.var(mu_hats))
    print(np.std(mu_hats))

    fig, (p1, p2) = plt.subplots(1, 2)
    p1.hist(mu_hats, bins=20)
    p1.set_title('Distribution of Service Rate Estimate')
    p1.axvline(mu, color='red')
    p1.axvline(lam, color='green')
    p2.scatter(t_ests, mu_hats)
    p2.axhline(mu, color='red')
    p2.axhline(lam, color='green')
    p2.set_title(f'Rate estimate for mu={mu}')
    p2.set_xlabel('Time range t_2 - t_1')
    p2.set_ylabel('Rate estimate mu_hat')
    plt.tight_layout()
    plt.show()





# See PyCharm help at https://www.jetbrains.com/help/pycharm/
