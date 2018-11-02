import numpy as np
import glob
from bigfile import BigFile


PATH_RUN = '/home/dir/PARTs/'


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


    np.save('partbhs/redshifts', np.array(redshifts))
    np.save('partbhs/mmbhmasss', np.array(mmbhmasss))
    np.save('partbhs/mmbhids', np.array(mmbhids))
    np.save('partbhs/mmbhaccs', np.array(mmbhaccs))
    np.save('partbhs/mmbhposs', np.array(mmbhposs))
    np.save('partbhs/mmbhvels', np.array(mmbhvels))

    print('There are %d mergers happened' %len(np.unique(mmbhids)))
    print('Done!')


if __name__ == '__main__':
    main()
