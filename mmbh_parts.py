import numpy as np
import glob
from bigfile import BigFile


PATH_RUN = '/home/dir/PARTs/'


def create_dir(dir_name):
    """ create directory name according to the run """
    import os
    import errno
    if not os.path.exists(os.path.dirname(dir_name)):
        try:
            os.makedirs(os.path.dirname(dir_name))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


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


    dir_name = 'partbhs/'
    create_dir(dir_name)

    np.save('{}redshifts'.format(dir_name), np.array(redshifts))
    np.save('{}mmbhmasss'.format(dir_name), np.array(mmbhmasss))
    np.save('{}mmbhids'.format(dir_name), np.array(mmbhids))
    np.save('{}mmbhaccs'.format(dir_name), np.array(mmbhaccs))
    np.save('{}mmbhposs'.format(dir_name), np.array(mmbhposs))
    np.save('{}mmbhvels'.format(dir_name), np.array(mmbhvels))

    print('There are %d mergers happened' %len(np.unique(mmbhids)))
    print('Done!')


if __name__ == '__main__':
    main()
