import numpy as np
import glob
import argparse
from natsort import natsorted

parser = argparse.ArgumentParser(description='Merge .mdisp files.')
parser.add_argument('folder', metavar='folder', help='Folder with mdisp files.', type=str)
parser.add_argument('outputFile', type=str, help='Output file.')
args = parser.parse_args()

file_list = natsorted(glob.glob(args.folder + '/*.mdisp'))
merged = []
print('Merging!')

for filee in file_list:
    mdisp = open(filee, 'r')
    to_merge = []
    for line in mdisp:
        line = line.split()
        # Sometimes the exponent indicator 'E' will disappear from mdisp file
        # put it back so the file can be interpreted correctly
        if '-' in line[-1] and 'E-' not in line[-1]:
            line[-1] = line[-1].replace('-', 'E-')
        elif '+' in line[-1] and 'E+' not in line[-1]:
            line[-1] = line[-1].replace('+', 'E+')
        if str(line[-1]) == 'NaN':
            print(line)
            line[-1] = 0
        merged.append([float(line[0]), float(line[1])])

np.savetxt(args.outputFile, merged, fmt='%.7e')
