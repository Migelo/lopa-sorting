import numpy as np
import argparse
from multiprocessing import Pool


parser = argparse.ArgumentParser(description='Compare 2 spectra files.')
parser.add_argument('bins', help='Bins on which the comparison should be made, should be the same file as the used in reducing the binned spectra.', type=str)
parser.add_argument('spectra1', help='First spectra, the one that will be devided.', type=str)
parser.add_argument('spectra2', help='Second spectra, the one we will divide BY.', type=str)
#parser.add_argument('outputFile', type=str, help='Set the output file.')
args = parser.parse_args()
#set the necessary parameters for parsing

cpuNumber = 2
#number of cores to use

print('Loading files.')
binData = np.loadtxt(args.bins)
print('bins loaded')
data = np.loadtxt(args.spectra1)
print('first spectra loaded')
data2 = np.loadtxt(args.spectra2)
print('All files loaded, starting comparison!')
    

def compare(data):
    average = []
    global binData
    summ, count, i, j = 0, 0, 0, 0
    spectraLength = len(data)
    while i < spectraLength:
        if j == len(binData): break
        if (data[i][0] >= binData[j][0]) and ((data[i][0]) < binData[j][1]):
            count += 1
            summ += data[i][1]
            i += 1
            if i == spectraLength - 1:
                    average.append(summ / count)
#                    print('does this ever happen?')
                    for k in range(j+1, len(binData)):
                        average.append(0)
                    break
        elif data[i][0] < binData[j][0]:
            i += 1
        elif data[i][0] >= binData[j][0]:
            j += 1
#            print(np.around(float(i)/spectraLength,4))
            if summ > 0:
                average.append(summ / count)
#                print(binData[j])
            else: average.append(0)
            summ, count = 0, 0
    return average

                
                
#    for singleBin in binData: #for each bin
#        print('In bin: ')
#        print(singleBin)
#        encounteredBinYet = False
#        count = 0
#        summ = 0
#        for line in data:
#            outsideOfTheBin = True
#            if (line[0] >= singleBin[0]) and (line[0] <= singleBin[1]): #check if the wawelength of the current line is within the bin
#                count += 1
#                summ += line[1]
#                outsideOfTheBin = False
#                encounteredBinYet = True
#                if (np.array_equal(line, data[-1])): #if we are on the last line, we must also sort the array otherwise it will go unsorted                   
#                    average = np.append(average,(summ / count))
#            elif ((outsideOfTheBin == True) and (encounteredBinYet == True)):
#                average = np.append(average,(summ / count))
#                break #once we leave the part of the file containing current bin, break and go to the next bin
#            elif (np.array_equal(line, data[-1])):
#                average = np.append(average,0)
#    average = np.delete(average, (0), axis=0)
#    return average

p = Pool(cpuNumber)
#compare(data2)
average = p.map(compare, [data, data2])
output = np.c_[binData, np.divide(average[0],average[1])]
np.savetxt(args.spectra1 + 'Comparison', output, fmt = '%.7e')
np.savetxt(args.spectra1 + '.averaged', np.c_[binData, average[0]],fmt = '%.7e')
np.savetxt(args.spectra2 + '.averaged', np.c_[binData, average[1]],fmt = '%.7e')