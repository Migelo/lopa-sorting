import numpy as np
import glob
import argparse
import os

parser = argparse.ArgumentParser(description='Merge .mdisp files.')
parser.add_argument('folder', metavar='SPECTRA', help='Folder with the mdisp files.', type=str)
parser.add_argument('outputFile', type=str, help='Set the output file.')
args = parser.parse_args()

file_list = sorted(glob.glob(args.folder + '/*.mdisp'))

max_length = len(str(max([int(x.split('.mdisp')[0].split('/')[-1]) for x in file_list])))
for file_name in file_list:
    wavelength = str((file_name.split('.mdisp')[0]).split('/')[-1].zfill(max_length))
    original_length = len((file_name.split('.mdisp')[0]).split('/')[-1])
    if original_length < max_length:
        print file_name, file_name[:-6-original_length] + wavelength + '.mdisp'
        os.rename(file_name, file_name[:-6-original_length] + wavelength + '.mdisp')

file_list = sorted(glob.glob(args.folder + '/*.mdisp'))


print('Merging!')
merged = []
for filee in file_list:
    i = 0
    mdisp = open(filee, 'r')
    to_merge = []
    for line in mdisp:
        line=line.split()
        """Sometimes the exponent indicator 'E' will disappear from mdisp file, here we put it back"""
        if '-' in line[-1] and 'E-' not in line[-1]:
            line[-1] = line[-1].replace('-', 'E-')
        elif '+' in line[-1] and 'E+' not in line[-1]:
            line[-1] = line[-1].replace('+', 'E+')
#        if str(line[-1]).split(line[-1][-3])[0][-1] != "E" and str(line[-1]) != 'NaN':
#            line[-1] = float(str(line[-1]).split("-")[0] + "E-" + str(line[-1]).split("-")[-1])
        if str(line[-1]) == 'NaN':
            print line
            line[-1] = 0
        merged.append(line)
        i +=1
i=0
for line in merged:
    merged[i][0] = float(line[0])
    merged[i][1] = float(line[1])
    i+=1
np.savetxt(args.outputFile, merged, fmt = '%.7e')
