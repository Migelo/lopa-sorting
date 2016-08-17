import numpy as np
import glob

file_list = []
file_list = sorted(glob.glob('./*.mdisp'))
#file_list = np.sort(file_list)
numberOfItems = len(file_list)
#create a list off all the .lopa files

#merged_file = args.merged_file
#create a path to the merged file

cpuNumber = 42
#number of cores to use
a = np.array([0,0])
for filee in file_list:
    a = np.vstack([a,np.loadtxt(filee)])
    a = np.delete(a, (0), axis=0)
    np.savetxt('spectra100bin', a, fmt = '%.7e')


binData = np.loadtxt('/home/cernetic/Documents/sorting/lopa-sorting/bins')
data = np.loadtxt('medianSpectra')
data2 = np.loadtxt('spectra')
average = np.array([0])
average2 = np.array([0])
for singleBin in binData: #for each bin
    print('Doing bin: ')
    print(singleBin)
    encounteredBinYet = False
    count = 0
    summ = 0
    for line in data:
        outsideOfTheBin = True
        if (line[0] >= singleBin[0]) and (line[0] <= singleBin[1]): #check if the wawelength of the current line is within the bin
            count += 1
            summ += line[1]
            outsideOfTheBin = False
            encounteredBinYet = True
        elif ((outsideOfTheBin == True) and (encounteredBinYet == True)):
            average = np.append(average,(summ / count))
            break #once we leave the part of the file containing current bin, break and go to the next bin    

for singleBin in binData: #for each bin
    encounteredBinYet = False
    count = 0
    summ = 0
    for line in data2:
        outsideOfTheBin = True
        if (line[0] >= singleBin[0]) and (line[0] <= singleBin[1]): #check if the wawelength of the current line is within the bin
            count += 1
            summ += line[1]
            outsideOfTheBin = False
            encounteredBinYet = True
        elif ((outsideOfTheBin == True) and (encounteredBinYet == True)):
            average2 = np.append(average2,(summ / count))
            break #once we leave the part of the file containing current bin, break and go to the next bin

average = np.delete(average, (0), axis=0)
average2 = np.delete(average2, (0), axis=0)
binData = np.delete(binData, (0), axis=0)
output = np.c_[binData, np.divide(average,average2)]
np.savetxt('comparison100bin', output, fmt = '%.7e')