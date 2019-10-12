import glob
import numpy as np
# import multiprocessing as mp

from mmbh_param import *
# from typing import Type
from bigfile import BigFile
# from functools import partial


def extract(x: np.ndarray, bin_min: float, bin_max: float):
    """ Get center and number of data points in each bin.
    : return : center x of each bin
    : return : number of data points in each bin
    """
    mask = (x > bin_min) & (x < bin_max)
    return  0.5 * (bin_min + bin_max), len(x[mask])


def mass_function(
        x: np.ndarray, x_min: float, x_max: float, n_bin: int, boxsize: float):
    """ Get mass function based on a given PIG file (thanks to A. Bhowmick)

    : x : x array, e.g. halo mass
    : x_min, x_max : min and max of x bins
    : n_bin : number of bins of x
    : boxsize : simulation box size

    : return : x centers of each bin
    : return : mass function of each bin: MF(x_i)
    : return : number counts of each bin: N(x_i)
    """
    x_bins = np.logspace(np.log10(x_min), np.log10(x_max), n_bin, endpoint=True)
    out = [extract(x, x_bins[i], x_bins[i + 1]) for i in range(len(x_bins) - 1)]

    out = np.array(out)
    x_centers, y_counts = out[:, 0], out[:, 1]

    dlogx = np.diff(np.log10(x_centers))[0]
    mass_func = y_counts / dlogx / (boxsize / HUBBLE)**3
    con = mass_func > 0

    return  x_centers[con], mass_func[con], y_counts[con]


def calc_mf_each_bf(dir_name: str, bf: BigFile):
    """ Calculate MFs of a single bf file"""
    header = bf.open('Header')
    redshift = 1. / header.attrs['Time'][0] - 1.

    bhmass = bf.open('5/BlackholeMass')[:] * TO_MSUN
    halomass = bf.open('FOFGroups/Mass')[:] * TO_MSUN
    starmass = bf.open('FOFGroups/MassByType')[:][:, 4] * TO_MSUN

    halo_mf = mass_function(halomass, HALO_MIN, HALO_MAX, N_BIN, BOXSIZE)
    star_mf = mass_function(starmass, STAR_MIN, STAR_MAX, N_BIN, BOXSIZE)
    bh_mf = mass_function(bhmass, BH_MIN, BH_MAX, N_BIN, BOXSIZE)

    print('    Saving MFs at z = %0.4f' % redshift)
    np.save('{}halo_mf_%0.4f'.format(dir_name) %redshift, halo_mf)
    np.save('{}star_mf_%0.4f'.format(dir_name) %redshift, star_mf)
    np.save('{}bh_mf_%0.4f'.format(dir_name) %redshift, bh_mf)



if __name__ == '__main__':
    print('Getting MFs of all PIGs\n')
    pigs = sorted(glob.glob('{}PIG_*'.format(PATH_RUN)))
    bfs = [BigFile(pig) for pig in pigs]
    print('There are %d PIG files \n' % len(bfs))

    print('Creating pigmfs dir to output MFs.\n')
    dir_name = 'pigmfs/'
    create_dir(dir_name)

    print('Looping through all PIG files\n')
    for bf in bfs:
        calc_mf_each_bf(dir_name, bf)

    # TODO multiprocessing bug. sad reacts only
    # p = mp.Pool(16)
    # func = partial(get_mf_each_bf, dir_name)
    # p.map(func, bfs)
    # p.close()
    # p.join()
    print('\nDone getting mass functions from PIGs =)')
