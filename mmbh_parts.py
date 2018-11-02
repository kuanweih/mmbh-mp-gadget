import numpy as np
import glob
from bigfile import BigFile
from mmbh_func import *


PATH_RUN = '/home/dir/PARTs/'


def append_mmbh_data(bf, mmbh_datas):
    header = bf.open('Header')
    redshift = 1. / header.attrs['Time'][0] - 1.

    bhmass = bf.open('5/BlackholeMass')[:]
    bhid = bf.open('5/ID')[:]
    bhacc = bf.open('5/BlackholeAccretionRate')[:]
    bhpos = bf.open('5/Position')[:]
    bhvel = bf.open('5/Velocity')[:]

    no_blackhole = len(bhmass) == 0

    if no_blackhole:
        mmbhmass = np.nan
        mmbhid = np.nan
        mmbhacc = np.nan
        mmbhpos = np.nan
        mmbhvel = np.nan
    else:
        mmbhmass = bhmass.max()
        mmbhid = bhid[np.argmax(bhmass)]
        mmbhacc = bhacc[np.argmax(bhmass)]
        mmbhpos = bhpos[np.argmax(bhmass)]
        mmbhvel = bhvel[np.argmax(bhmass)]

    # append data
    mmbh_data = [redshift, mmbhmass, mmbhid, mmbhacc, mmbhpos, mmbhvel]
    mmbh_datas.append(mmbh_data)


def append_merger_data(bf, mergerid, merger_datas):
    header = bf.open('Header')
    redshift = 1. / header.attrs['Time'][0] - 1.

    bhmass = bf.open('5/BlackholeMass')[:]
    bhid = bf.open('5/ID')[:]
    bhacc = bf.open('5/BlackholeAccretionRate')[:]
    bhpos = bf.open('5/Position')[:]
    bhvel = bf.open('5/Velocity')[:]

    if len(bhmass) > 0:
        mask_i = bhid == mergerid
        bhmass_i = bhmass[mask_i][0]
        bhacc_i = bhacc[mask_i][0]
        bhpos_i = bhpos[mask_i][0]
        bhvel_i = bhvel[mask_i][0]

        merger_data = [mergerid, redshift,
                       bhmass_i, bhacc_i, bhpos_i, bhvel_i]

        merger_datas.append(merger_data)


def main():
    """
    get properties of the most massive black hole from all PART files
    """
    parts = sorted(glob.glob('{}PART_*'.format(PATH_RUN)))
    bfs = [BigFile(part) for part in parts]

    mmbh_datas = []

    for bf in bfs:
        append_mmbh_data(bf, mmbh_datas)


    dir_name = 'partbhs/'
    create_dir(dir_name)

    data_names = ['redshifts', 'mmbhmasss',
                  'mmbhids', 'mmbhaccs', 'mmbhposs', 'mmbhvels']

    mmbh_datas = np.array(mmbh_datas)
    for v, data_name in enumerate(data_names):
        np.save('{}{}'.format(dir_name, data_name), mmbh_datas[:,v])

    mergerids = np.unique(mmbh_datas[:,2])
    print('There are %d mergers happened' %len(mergerids))

    merger_datas = []

    for mergerid in mergerids:
        for bf in bfs:
            append_merger_data(bf, mergerid, merger_datas)

    merger_datas = np.array(merger_datas)
    np.save('{}merger_datas'.format(dir_name), merger_datas)




    print('Done!')


if __name__ == '__main__':
    main()
