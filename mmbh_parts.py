import numpy as np
import glob
from bigfile import BigFile
from mmbh_func import *
from numpy import linalg as la
from nbodykit.lab import *
from nbodykit.source.catalog import BigFileCatalog


def get_t1(part, mmbhpos, nmesh):
    """
    return t1 around the most massive BH
    """
    hydro = BigFileCatalog(part, dataset='0', header='Header')
    dm = BigFileCatalog(part, dataset='1', header='Header')
    star = BigFileCatalog(part, dataset='4', header='Header')
    bh = BigFileCatalog(part, dataset='5', header='Header')

    combined = MultipleSpeciesCatalog(['0', '1', '4', '5'], hydro, dm, star, bh)

    combined_mesh = combined.to_mesh(Nmesh=nmesh, compensated=True,
                                     window='tsc', weight='Mass')

    tidal_tensor = np.array([[[s for s in combined_mesh.paint().r2c().apply(
        lambda k, v: k[i] * k[j] / (sum(ki**2 for ki in k) + EPSILON) * v
    ).c2r().readout([mmbhpos])] for i in range(0, 3)] for j in range(0, 3)]).reshape(3, 3)

    tidal_tensor -= np.trace(tidal_tensor) * np.identity(3) / 3.

    # tt: eigenvalues of tidal field tensor
    tt = np.array([u for u in la.eigvals(tidal_tensor)])
    return tt.max()


def append_mmbh_data(part, redshifts, mmbhmasss, mmbhids,
                     mmbhaccs, mmbhposs, mmbhvels, mmbht1s):
    """
    append the most massive BHs' data
    """
    bf = BigFile(part)
    header = bf.open('Header')
    redshift = 1. / header.attrs['Time'][0] - 1.

    bhmass = bf.open('5/BlackholeMass')[:]

    no_blackhole = len(bhmass) == 0
    if no_blackhole:
        print('There is no BH formed at z = %0.2f' % redshift)
        return

    print('Calculating properties at z = %0.2f' % redshift)
    bhid = bf.open('5/ID')[:]
    bhacc = bf.open('5/BlackholeAccretionRate')[:]
    bhpos = bf.open('5/Position')[:]
    bhvel = bf.open('5/Velocity')[:]

    mmbhmass = bhmass.max()
    mmbhid = bhid[np.argmax(bhmass)]
    mmbhacc = bhacc[np.argmax(bhmass)]
    mmbhpos = bhpos[np.argmax(bhmass)]
    mmbhvel = bhvel[np.argmax(bhmass)]

    if (redshift - round(redshift) < DZ):
        print('    calculating t1...')
        mmbht1 = [get_t1(part, mmbhpos, nmesh) for nmesh in NMESHS]
    else:
        print('    skip t1 calculation because it is not close to int(z)')
        mmbht1 = [np.nan] * len(NMESHS)

    # append data
    redshifts.append(redshift)
    mmbhmasss.append(mmbhmass)
    mmbhids.append(mmbhid)
    mmbhaccs.append(mmbhacc)
    mmbhposs.append(mmbhpos)
    mmbhvels.append(mmbhvel)
    mmbht1s.append(mmbht1)


def append_merger_data(part, mergerid, merger_datas):
    """
    append the merger tree from the most massive BHs' data
    """
    bf = BigFile(part)
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
    print('Start getting properties of mmbhs from all PARTs')
    parts = sorted(glob.glob('{}PART_*'.format(PATH_RUN)))
    print('There are %d part files \n' % len(parts))

    redshifts = []
    mmbhmasss = []
    mmbhids = []
    mmbhaccs = []
    mmbhposs = []
    mmbhvels = []
    mmbht1s = []

    for part in parts:
        append_mmbh_data(part, redshifts, mmbhmasss, mmbhids,
                         mmbhaccs, mmbhposs, mmbhvels, mmbht1s)

    dir_name = 'partbhs/'
    create_dir(dir_name)

    np.save('{}redshifts'.format(dir_name), np.array(redshifts))
    np.save('{}mmbhmasss'.format(dir_name), np.array(mmbhmasss))
    np.save('{}mmbhids'.format(dir_name), np.array(mmbhids))
    np.save('{}mmbhaccs'.format(dir_name), np.array(mmbhaccs))
    np.save('{}mmbhposs'.format(dir_name), np.array(mmbhposs[0]))
    np.save('{}mmbhvels'.format(dir_name), np.array(mmbhvels[0]))
    np.save('{}mmbht1s'.format(dir_name), np.array(mmbht1s))

    print('\n')
    print('t1 are measured in (Mpc):')
    print(BOXSIZE / np.array([NMESHS]))
    print('Done with mmbh data from PARTs :) \n')

    print('Start dealing with mergers')
    mergerids = np.unique(mmbhids)
    print('There are %d mergers happened. \n' % len(mergerids))

    merger_datas = []

    for mergerid in mergerids:
        for part in parts:
            append_merger_data(part, mergerid, merger_datas)

    merger_datas = np.array(merger_datas)
    np.save('{}merger_datas'.format(dir_name), merger_datas)

    print('Done with merger data.')
    print('Yeah we are finished :)')


if __name__ == '__main__':
    main()
