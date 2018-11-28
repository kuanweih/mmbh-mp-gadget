import numpy as np
import glob
import multiprocessing
from bigfile import BigFile
from mmbh_func import *


def extract(x, bin_min, bin_max):
    """
    get center and number of data points in each bin
    """
    mask = (x > bin_min) & (x < bin_max)
    return 0.5 * (bin_min + bin_max), len(x[mask])


def mass_function(x, x_min, x_max, n_bin, boxsize):
    """
    get mass function based on a given PIG file (thanks to A. Bhowmick)
    x: x array, e.g. halo mass
    x_min, x_max, n_bin: minimum, maximum, number of bins of x
    boxsize: simulation box size
    return: x_centers, mass function, histogram
    """
    x_bins = np.logspace(np.log10(x_min), np.log10(x_max), n_bin, endpoint=True)

    # out = [extract(x, x_bins[i], x_bins[i + 1]) for i in range(len(x_bin) - 1)]
    out = (extract(x, x_bins[i], x_bins[i + 1]) for i in range(len(x_bin) - 1))

    x_centers = np.array(zip(*out)[0])
    y_counts = np.array(zip(*out)[1])

    dlogx = np.diff(np.log10(x_centers))[0]
    mass_func = y_counts / dlogx / (boxsize / HUBBLE)**3
    con = mass_func > 0

    return x_centers[con], mass_func[con], y_counts[con]


def main():
    pigs = sorted(glob.glob('{}PIG_*'.format(PATH_RUN)))
    bfs = [BigFile(pig) for pig in pigs]

    dir_name = 'pigmfs/'
    create_dir(dir_name)
    print('Created pigmfs for mass functions.')

    for bf in bfs:
        header = bf.open('Header')
        redshift = 1. / header.attrs['Time'][0] - 1.

        bhmass = bf.open('5/BlackholeMass')[:] * TOMSUN
        halomass = bf.open('FOFGroups/Mass')[:] * TOMSUN
        starmass = bf.open('FOFGroups/MassByType')[:][:, 4] * TOMSUN

        halo_mf = mass_function(halomass, HALO_MIN, HALO_MAX, N_BIN, BOXSIZE)
        star_mf = mass_function(starmass, STAR_MIN, STAR_MAX, N_BIN, BOXSIZE)
        bh_mf = mass_function(bhmass, BH_MIN, BH_MAX, N_BIN, BOXSIZE)

        np.save('{}halo_mf_{}'.format(dir_name, redshift), halo_mf)
        np.save('{}star_mf_{}'.format(dir_name, redshift), star_mf)
        np.save('{}bh_mf_{}'.format(dir_name, redshift), bh_mf)


# TODO: use multiprocessing when it is working fine
# p = multiprocessing.Pool(16)
# out = p.map(mmbh_from_txt, PATH_RUNS)
# p.close()


if __name__ == '__main__':
    main()
    print('Done getting mass functions from PIGs.')
