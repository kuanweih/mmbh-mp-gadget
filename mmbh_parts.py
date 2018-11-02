import numpy as np
import glob
from bigfile import BigFile
from mmbh_func import *


def append_mmbh_data(bf, redshifts, mmbhmasss, mmbhids, mmbhaccs, mmbhposs, mmbhvels):
    """
    append the most massive BHs' data
    """
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
    redshifts.append(redshift)
    mmbhmasss.append(mmbhmass)
    mmbhids.append(mmbhid)
    mmbhaccs.append(mmbhacc)
    mmbhposs.append(mmbhpos)
    mmbhvels.append(mmbhvel)


def append_merger_data(bf, mergerid, merger_datas):
    """
    append the merger tree from the most massive BHs' data
    """
    header = bf.open('Header')
    redshift = 1. / header.attrs['Time'][0] - 1.

    bhmass = bf.open('5/BlackholeMass')[:]
    bhid = bf.open('5/ID')[:]
    bhacc = bf.open('5/BlackholeAccretionRate')[:]
    bhpos = bf.open('5/Position')[:]
    bhvel = bf.open('5/Velocity')[:]

    if len(bhmass) > 0:
        mask_i = bhid == mergerid
        if True in mask_i:
            bhmass_i = bhmass[mask_i]
            bhacc_i = bhacc[mask_i]
            bhpos_i = bhpos[mask_i]
            bhvel_i = bhvel[mask_i]

            merger_data = np.array([mergerid, redshift, bhmass_i[0], bhacc_i[0],
                                    bhpos_i[0][0], bhpos_i[0][1], bhpos_i[0][2],
                                    bhvel_i[0][0], bhvel_i[0][1], bhvel_i[0][2]])
            merger_datas.append(merger_data)


def main():
    """
    get properties of the most massive black hole from all PART files
    """
    parts = sorted(glob.glob('{}PART_*'.format(PATH_RUN)))
    bfs = [BigFile(part) for part in parts]

    redshifts = []
    mmbhmasss = []
    mmbhids = []
    mmbhaccs = []
    mmbhposs = []
    mmbhvels = []

    for bf in bfs:
        append_mmbh_data(bf, redshifts, mmbhmasss,
                         mmbhids, mmbhaccs, mmbhposs, mmbhvels)

    dir_name = 'partbhs/'
    create_dir(dir_name)

    np.save('{}redshifts'.format(dir_name), np.array(redshifts))
    np.save('{}mmbhmasss'.format(dir_name), np.array(mmbhmasss))
    np.save('{}mmbhids'.format(dir_name), np.array(mmbhids))
    np.save('{}mmbhaccs'.format(dir_name), np.array(mmbhaccs))
    np.save('{}mmbhposs'.format(dir_name), np.array(mmbhposs[0]))
    np.save('{}mmbhvels'.format(dir_name), np.array(mmbhvels[0]))

    print('Done with mmbh data from PARTs.')

    mergerids = np.unique(mmbhids)
    print('There are %d mergers happened.' % len(mergerids))

    merger_datas = []

    for mergerid in mergerids:
        for bf in bfs:
            append_merger_data(bf, mergerid, merger_datas)

    merger_datas = np.array(merger_datas)
    np.save('{}merger_datas'.format(dir_name), merger_datas)

    print('Done with merger data.')
    print('Yeah we are finished :)')


if __name__ == '__main__':
    main()
