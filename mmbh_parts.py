import glob
import numpy as np

from typing import List
from bigfile import BigFile
from mmbh_param import PATH_RUN, TO_MSUN, TO_MSUN_YEAR




def append_mmbh_data(part: str, redshifts: List, mmbhmasss: List,
        mmbhids: List, mmbhaccs: List, mmbhposs: List, mmbhvels: List):
    """ Append the most massive BHs' quantities. """
    bf = BigFile(part)
    header = bf.open('Header')
    redshift = 1. / header.attrs['Time'][0] - 1.

    bhmass = bf.open('5/BlackholeMass')[:] * TO_MSUN

    no_blackhole = len(bhmass) == 0
    if no_blackhole:
        print('    No BH formed at z = %0.2f' % redshift)
        return  None

    bhid = bf.open('5/ID')[:]
    bhacc = bf.open('5/BlackholeAccretionRate')[:] * TO_MSUN_YEAR
    bhpos = bf.open('5/Position')[:]
    bhvel = bf.open('5/Velocity')[:]

    mmbhmass = bhmass.max()
    mmbhid = bhid[np.argmax(bhmass)]
    mmbhacc = bhacc[np.argmax(bhmass)]
    mmbhpos = bhpos[np.argmax(bhmass)]
    mmbhvel = bhvel[np.argmax(bhmass)]

    print('    Appending BH quantities at z = %0.4f' % redshift)
    redshifts.append(redshift)
    mmbhmasss.append(mmbhmass)
    mmbhids.append(mmbhid)
    mmbhaccs.append(mmbhacc)
    mmbhposs.append(mmbhpos)
    mmbhvels.append(mmbhvel)


def append_merger_data(part: str, mergerid: np.ndarray, merger_datas: List):
    """ Append the merger history of the most massive BH """
    bf = BigFile(part)
    header = bf.open('Header')
    redshift = 1. / header.attrs['Time'][0] - 1.

    bhmass = bf.open('5/BlackholeMass')[:] * TO_MSUN
    bhid = bf.open('5/ID')[:]
    bhacc = bf.open('5/BlackholeAccretionRate')[:] * TO_MSUN_YEAR
    bhpos = bf.open('5/Position')[:]
    bhvel = bf.open('5/Velocity')[:]

    if len(bhmass) > 0:
        mask_i = bhid == mergerid
        if True in mask_i:
            bhmass_i = bhmass[mask_i]
            bhacc_i = bhacc[mask_i]
            bhpos_i = bhpos[mask_i]
            bhvel_i = bhvel[mask_i]

            merger_data = [mergerid, redshift, bhmass_i[0], bhacc_i[0],
                           bhpos_i[0][0], bhpos_i[0][1], bhpos_i[0][2],
                           bhvel_i[0][0], bhvel_i[0][1], bhvel_i[0][2]]
            merger_datas.append(merger_data)



if __name__ == '__main__':

    print('Getting properties of the most massive BH from all PART files\n')
    parts = sorted(glob.glob('{}PART_*'.format(PATH_RUN)))
    print('There are %d PART files \n' % len(parts))

    redshifts = []
    mmbhmasss = []
    mmbhids = []
    mmbhaccs = []
    mmbhposs = []
    mmbhvels = []

    print('Starting looping through all PART files\n')
    for part in parts:
        append_mmbh_data(
            part, redshifts, mmbhmasss, mmbhids, mmbhaccs, mmbhposs, mmbhvels)

    print('\nConverting the lists into a dict\n')
    dict = {}
    dict['redshifts'] = np.array(redshifts)
    dict['mmbhmasss'] = np.array(mmbhmasss)
    dict['mmbhaccs'] = np.array(mmbhaccs)
    dict['mmbhposs'] = np.array(mmbhposs[0])
    dict['mmbhvels'] = np.array(mmbhvels[0])
    dict['mmbhids'] = np.array(mmbhids)

    print('Saving the dict to a npy\n')
    np.save('partmmbh', dict)

    print('Done with mmbh data from PARTs. \n')
    print('------------------------------------------------------------')

    print('\nStart dealing with mergers\n')
    mergerids = np.unique(mmbhids)    # bhids for the mmbh
    print('There are %d mergers happened. \n' % (len(mergerids) - 1))

    merger_datas = []

    print('Looping through all merger BH ids\n')
    for mergerid in mergerids:
        for part in parts:
            append_merger_data(part, mergerid, merger_datas)

    merger_datas = np.array(merger_datas)

    print('\nConverting the lists into a dict\n')
    dict = {}
    keys = ['mergerid', 'redshift', 'bhmass', 'bhacc',
            'bhposx', 'bhposy', 'bhposz', 'bhvelx', 'bhvely', 'bhvelz']
    for i,k in enumerate(keys):
        dict[k] = merger_datas[:, i]

    print('Saving the dict to a npy\n')
    np.save('mergermmbh', dict)

    print('Done with merger data.\n')
    print('Yeah we are finished :)')
