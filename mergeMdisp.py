import numpy as np
import glob
import argparse

parser = argparse.ArgumentParser(description='Merge .mdisp files.')
parser.add_argument('folder', metavar='SPECTRA', help='Folder with the mdisp files.', type=str)
parser.add_argument('outputFile', type=str, help='Set the output file.')
args = parser.parse_args()

file_list = sorted(glob.glob(args.folder + '/*.mdisp'))

print('Merging!')
#a = np.array([0,0])
merged = []
for filee in file_list:
    i = 0
    mdisp = open(filee, 'r')
    to_merge = []
    for line in mdisp:
        line=line.split()
        if str(line[-1]).split("-")[0][-1] != "E":
            line[-1] = float(str(line[-1]).split("-")[0] + "E-" + str(line[-1]).split("-")[-1])
            #print type(line)
        merged.append(line)
        i +=1
#    a = np.vstack([a,np.loadtxt(filee)])
    #print filee
#    merged.append(to_merge)
#a = np.delete(a, (0), axis=0)
#print merged
i=0
for line in merged:
    merged[i][0] = float(line[0])
    merged[i][1] = float(line[1])
    i+=1
np.savetxt(args.outputFile, merged, fmt = '%.7e')