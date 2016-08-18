import numpy as np
import sys
import argparse


parser = argparse.ArgumentParser(description='Compare 2 spectra files.')
parser.add_argument('spectra1', metavar='SPECTRA', help='First spectra, the one that will be devided.', type=str)
parser.add_argument('spectra2', help='Second spectra, the one we will devide BY.', type=str)
parser.add_argument('bins', help='Bins on which the comparison should be made, should be the same file as the used in reducing the binned spectra.', type=str)
parser.add_argument('o','outputFile', type=str, help='Set the output file.')
args = parser.parse_args()
#set the necessary parameters for parsing

cpuNumber = 2
#number of cores to use

binData = np.loadtxt('/home/cernetic/Documents/sorting/lopa-sorting/bins')
data = np.loadtxt('medianSpectra')
data2 = np.loadtxt('spectra')

if len(data) != len(data2):
    sys.exit("Lenghts of the spectra files do not match, exiting!")
    
average = np.array([0])
average2 = np.array([0])

for singleBin in binData: #for each bin
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
np.savetxt(args.outputFile, output, fmt = '%.7e')