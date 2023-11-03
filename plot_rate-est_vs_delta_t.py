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
    print(ests_df['mu_hat'].mean(0))
    print(ests_df['mu_hat'].var(0))

    plt.scatter(ests_df['delta_t'], ests_df['mu_hat'])
    plt.axhline(mu, color='red', label=f'$\mu={mu}$')
    plt.axhline(lam, color='green', label=f'$\lambda={lam}$')
    plt.title(f'Rate estimate')
    plt.xlabel('Time range $\Delta t$ time units')
    plt.ylabel('Rate estimate $\hat{\mu}$ customers served per unit time')
    plt.legend()
    plt.tight_layout()
    # plt.show()

    plot_dir = 'plots'
    os.makedirs(plot_dir, exist_ok=True)
    plot_filename = f'{plot_dir}/scatter--{filename_base}.png'
    plt.savefig(plot_filename)

    print(f'Scatter plot output as {plot_filename}')


