import errno, os, sys

import simpy
from typing import Callable
from functools import partial
import numpy.random as npr
import tomli
import pandas as pd


def exponential_time(lam):
    return npr.exponential(1.0/lam)


def service(env: simpy.Environment, q: simpy.Resource, reqno: int, stime: float):
    with q.request() as request:
        yield request
        yield env.timeout(stime)


def arrival_process(env: simpy.Environment, q: simpy.Resource, Q0:int, arrival_time: Callable, service_time: Callable):
    reqno = Q0
    while True:
        atime = arrival_time()
        stime = service_time()
        reqno += 1
        yield env.timeout(atime)
        env.process(service(env, q, reqno, stime))


def run_simulation(mc: int, T:float, Q0:int, interarrival_time: Callable, service_time: Callable):
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


if __name__ == '__main__':
    npr.seed(1)
    if len(sys.argv) != 3:
        print(f'Usage: {os.path.basename(sys.argv[0])} <param-file> <controls-file>', file=sys.stderr)
        sys.exit(errno.EINVAL)

    param_filename, controls_filename = sys.argv[1:]

    with open(param_filename, "rb") as f:
        queue_params = tomli.load(f)
        Q0 = queue_params['Q0']
        lam = queue_params['lam']
        mu = queue_params['mu']
        T = queue_params['T']
        
    with open(controls_filename, "rb") as f:
        queue_controls = tomli.load(f)
        delta_t = queue_controls['delta_t']
        eta = queue_controls['eta']
        MC = queue_controls['MC']

    print(f'Running {MC} simulations of queue with lamdba={lam} mu={mu} Q0={Q0} over time {T}')
    print(f'    Sampling every {delta_t} and using control {eta}.')

    interarrival_time = partial(exponential_time, lam)
    service_time = partial(exponential_time, mu*eta)

    run_simulations(MC, T, Q0, interarrival_time, service_time)

    out_dir = 'output'
    os.makedirs(out_dir, exist_ok=True)

    out_filename = f'{out_dir}/mu-{mu}--lam-{lam}--Q0-{Q0}--T-{T}--delta_t-{delta_t}--eta-{eta}.csv'
    log_list = [log for mclogs in logs for log in mclogs]
    log_df = pd.DataFrame(data=log_list, columns=('mc', 'k', 't_k', 'Q_k'))
    log_df.to_csv(out_filename, index=False)

    print(f'Results saved to {out_filename}')

    # mu_hats = list()
    # t_ests = list()
    # for mc in range(MC):
    #     mclogs = logs[mc]
    #     K = len(mclogs)
    #     k1, k2 = sorted(npr.choice(K, 2, replace=False))
    #     l1, l2 = mclogs[k1], mclogs[k2]
    #     q1, q2 = l1[3], l2[3]
    #     t1, t2 = l1[2], l2[2]
    #     t_est = t2 - t1
    #     mu_hat = -1.0/(eta*(t_est))*(q2-q1-lam*(t_est))
    #     mu_hats.append(mu_hat)
    #     t_ests.append(t_est)
    #
    #
    # print(np.mean(mu_hats))
    # print(np.var(mu_hats))
    # print(np.std(mu_hats))
    #
    # fig, (p1, p2) = plt.subplots(1, 2)
    # p1.hist(mu_hats, bins=20)
    # p1.set_title('Distribution of Service Rate Estimate')
    # p1.axvline(mu, color='red')
    # p1.axvline(lam, color='green')
    # p2.scatter(t_ests, mu_hats)
    # p2.axhline(mu, color='red')
    # p2.axhline(lam, color='green')
    # p2.set_title(f'Rate estimate for mu={mu}')
    # p2.set_xlabel('Time range t_2 - t_1')
    # p2.set_ylabel('Rate estimate mu_hat')
    # plt.tight_layout()
    # plt.show()





# See PyCharm help at https://www.jetbrains.com/help/pycharm/
