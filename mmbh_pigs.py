import numpy as np
import glob
from bigfile import BigFile
from mmbh_func import *


def main():
    """
    get properties of the most massive black hole from all PIG files
    """
    pigs = sorted(glob.glob('{}PIG_*'.format(PATH_RUN)))
    bfs = [BigFile(pig) for pig in pigs]

    redshifts = []
    mmbhmasss = []
    mmbhhalomasss = []
    mmbhstarmasss = []

    for bf in bfs:
        header = bf.open('Header')
        redshift = 1. / header.attrs['Time'][0] - 1.

        bhmass = bf.open('5/BlackholeMass')[:]
        bhfofid = bf.open('5/GroupID')[:]
        halomass = bf.open('FOFGroups/Mass')[:]
        halofofid = bf.open('FOFGroups/GroupID')[:]
        starmass = bf.open('FOFGroups/MassByType')[:][:, 4]

        no_blackhole = len(bhmass) == 0

        if no_blackhole:
            mmbhmass = np.nan
            mmbhhalomass = np.nan
            mmbhstarmass = np.nan
        else:
            mmbhmass = bhmass.max()

            fofid_target = bhfofid[np.argmax(bhmass)]
            if sum(halofofid == fofid_target) > 1:
                mmbhhalomass = np.nan
                mmbhstarmass = np.nan
            else:
                mmbhhalomass = halomass[halofofid == fofid_target][0]
                mmbhstarmass = starmass[halofofid == fofid_target][0]

        # append data
        redshifts.append(redshift)
        mmbhmasss.append(mmbhmass)
        mmbhhalomasss.append(mmbhhalomass)
        mmbhstarmasss.append(mmbhstarmass)

    dir_name = 'pigbhs/'
    create_dir(dir_name)

    np.save('{}redshifts'.format(dir_name), np.array(redshifts))
    np.save('{}mmbhmasss'.format(dir_name), np.array(mmbhmasss))
    np.save('{}mmbhhalomasss'.format(dir_name), np.array(mmbhhalomasss))
    np.save('{}mmbhstarmasss'.format(dir_name), np.array(mmbhstarmasss))

    print('Done with mmbh data from PIGs.')


if __name__ == '__main__':
    main()
