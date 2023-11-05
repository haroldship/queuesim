import errno
import os.path
import sys
import matplotlib.pyplot as plt
import pandas as pd

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f'Usage: {os.path.basename(sys.argv[0])} <ests_filename>', file=sys.stderr)
        sys.exit(errno.EINVAL)

    ests_filename = sys.argv[1]

    filename_base = os.path.splitext(os.path.basename(ests_filename))[0]
    pairs = str.split(filename_base, '--')[1:]
    params = {str.split(p, '-')[0]:str.split(p, '-')[1] for p in pairs}
    mu = float(params['mu'])
    lam = float(params['lam'])
    Q0 = float(params['Q0'])
    T = float(params['T'])
    delta_t = float(params['delta_t'])
    eta = float(params['eta'])

    ests_df = pd.read_csv(ests_filename)

    avg_df = ests_df.groupby(['delta_t'])['mu_hat'].mean()

    plt.plot(avg_df)
    plt.axhline(mu, color='red', label=f'$\mu={mu}$')
    plt.axhline(lam, color='green', label=f'$\lambda={lam}$')
    plt.title(f'Average Rate Estimate by Time Difference')
    plt.xlabel('Time range $\Delta t$ time units')
    plt.ylabel('Average rate estimate $\hat{\mu}$ customers per unit time')
    plt.legend()
    plt.tight_layout()
    # plt.show()

    plot_dir = 'plots'
    os.makedirs(plot_dir, exist_ok=True)
    plot_filename = f'{plot_dir}/average_rates--{filename_base}.png'
    plt.savefig(plot_filename)
    plt.cla()

    print(f'Rate averages plot output as {plot_filename}')

    var_df = ests_df.groupby(['delta_t'])['mu_hat'].var()

    plt.plot(var_df)
    plt.title(f'Variance of Rate Estimate by Time Difference')
    plt.xlabel('Time range $\Delta t$ time units')
    plt.ylabel('Variance of rate estimate $\hat{\mu}$')
    plt.tight_layout()
    # plt.show()

    plot_dir = 'plots'
    os.makedirs(plot_dir, exist_ok=True)
    plot_filename = f'{plot_dir}/variance_rates--{filename_base}.png'
    plt.savefig(plot_filename)

    print(f'Rate variance plot output as {plot_filename}')

