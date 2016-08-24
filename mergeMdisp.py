import numpy as np
import glob
import argparse

parser = argparse.ArgumentParser(description='Merge .mdisp files.')
parser.add_argument('folder', metavar='SPECTRA', help='Folder with the mdisp files.', type=str)
parser.add_argument('outputFile', type=str, help='Set the output file.')
args = parser.parse_args()

file_list = sorted(glob.glob(args.folder + '/*.mdisp'))

print('Merging!')
a = np.array([0,0])
for filee in file_list:
    a = np.vstack([a,np.loadtxt(filee)])
a = np.delete(a, (0), axis=0)
np.savetxt(args.outputFile, a, fmt = '%.7e')