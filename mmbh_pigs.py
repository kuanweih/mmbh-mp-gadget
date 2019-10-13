import glob
import numpy as np

from bigfile import BigFile
from mmbh_param import PATH_RUN, TO_MSUN, TO_MSUN_YEAR



if __name__ == '__main__':
    print('\n------------------------------------------------------------\n')
    print('Getting properties of the most massive BH from all PIG files\n')
    pigs = sorted(glob.glob('{}PIG_*'.format(PATH_RUN)))
    bfs = [BigFile(pig) for pig in pigs]
    print('There are %d PIG files \n' % len(bfs))

    redshifts = []
    mmbhmasss = []
    mmbhhalomasss = []
    mmbhstarmasss = []
    mmbhaccs = []
    mmbhsfrs = []

    print('Starting looping through all PIG files\n')
    for bf in bfs:
        header = bf.open('Header')
        redshift = 1. / header.attrs['Time'][0] - 1.

        bhmass = bf.open('5/BlackholeMass')[:] * TO_MSUN
        bhfofid = bf.open('5/GroupID')[:]
        halomass = bf.open('FOFGroups/Mass')[:] * TO_MSUN
        halofofid = bf.open('FOFGroups/GroupID')[:]
        starmass = bf.open('FOFGroups/MassByType')[:][:, 4] * TO_MSUN
        bhacc = bf.open('5/BlackholeAccretionRate')[:] * TO_MSUN_YEAR
        sfr = bf.open('FOFGroups/StarFormationRate')[:]

        no_blackhole = len(bhmass) == 0

        if no_blackhole:
            mmbhmass = np.nan
            mmbhhalomass = np.nan
            mmbhstarmass = np.nan
            mmbhacc = np.nan
            mmbhsfr = np.nan
        else:
            mmbhmass = bhmass.max()
            mmbhacc = bhacc[np.argmax(bhmass)]

            fofid_target = bhfofid[np.argmax(bhmass)]
            if sum(halofofid == fofid_target) > 1:
                mmbhhalomass = np.nan
                mmbhstarmass = np.nan
                mmbhsfr = np.nan
            else:
                mask_fofid = halofofid == fofid_target
                mmbhhalomass = halomass[mask_fofid][0]
                mmbhhalomass = np.nan if mmbhhalomass==0 else mmbhhalomass
                mmbhstarmass = starmass[mask_fofid][0]
                mmbhstarmass = np.nan if mmbhstarmass==0 else mmbhstarmass
                mmbhsfr = sfr[mask_fofid][0]

        print('    Appending BH quantities at z = %0.4f' % redshift)
        redshifts.append(redshift)
        mmbhmasss.append(mmbhmass)
        mmbhhalomasss.append(mmbhhalomass)
        mmbhstarmasss.append(mmbhstarmass)
        mmbhaccs.append(mmbhacc)
        mmbhsfrs.append(mmbhsfr)

    print('\nConverting the lists into a dict\n')
    dict = {}
    dict['redshift'] = np.array(redshifts)
    dict['mmbhmass'] = np.array(mmbhmasss)
    dict['mmbhhalomass'] = np.array(mmbhhalomasss)
    dict['mmbhstarmass'] = np.array(mmbhstarmasss)
    dict['mmbhacc'] = np.array(mmbhaccs)
    dict['mmbhsfr'] = np.array(mmbhsfrs)

    print('Saving the dict to a npy\n')
    np.save('output/pigmmbh', dict)

    print('Done with mmbh data from PIGs :)')
