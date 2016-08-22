import numpy as np
import argparse
from multiprocessing import Pool


parser = argparse.ArgumentParser(description='Compare 2 spectra files.')
parser.add_argument('spectra1', help='First spectra, the one that will be devided.', type=str)
parser.add_argument('spectra2', help='Second spectra, the one we will devide BY.', type=str)
parser.add_argument('bins', help='Bins on which the comparison should be made, should be the same file as the used in reducing the binned spectra.', type=str)
parser.add_argument('outputFile', type=str, help='Set the output file.')
args = parser.parse_args()
#set the necessary parameters for parsing

cpuNumber = 2
#number of cores to use


binData = np.loadtxt(args.bins)
data = np.loadtxt(args.spectra1)
data2 = np.loadtxt(args.spectra2)

    
average = np.array([0])
average2 = np.array([0])

def compare(data):
    average = np.array([0])
    global binData
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
                if (np.array_equal(line, data[-1])): #if we are on the last line, we must also sort the array otherwise it will go unsorted                   
                    average = np.append(average,(summ / count))
            elif ((outsideOfTheBin == True) and (encounteredBinYet == True)):
                average = np.append(average,(summ / count))
                break #once we leave the part of the file containing current bin, break and go to the next bin
                
    average = np.delete(average, (0), axis=0)
    return average

p = Pool(2)
average = p.map(compare, [data, data2]) 
#binData = np.delete(binData, (0), axis=0)
output = np.c_[binData, np.divide(average[0],average[1])]
np.savetxt(args.outputFile, output, fmt = '%.7e')