import numpy as np
import argparse
import sys
from multiprocessing import Pool

parser = argparse.ArgumentParser(description='Sort the spectra in subBins.')
parser.add_argument('bins', type=str, help='File defining the wawelenght bins')
parser.add_argument('subBins', help='File defining the subBins distribution.')
parser.add_argument('cpuNumber', type=int, help='Number of CPUs to be used.')

args = parser.parse_args()
#set the necessary parameters for parsing

cpuNumber = args.cpuNumber
#number of cores to use

floatFormat = '%.7e'
#format for np.savetxt()

depthList = range(1,83)  
depthLength = len(str(np.max(depthList)))
#set the number of depth points
#depthLength is created as a global variable so all functions can access it


def bining(depthList):
    minMax = np.loadtxt(str(depthList[0]).zfill(depthLength) + '.segment') #get minimum and maximum wawelenghts from the first .segment file
    wawelenghts = [array[0] for array in minMax]
    minimum = np.min(wawelenghts)
    maximum = np.max(wawelenghts)
    print('Minimum: ' + str(minimum))
    print('Maximum: ' + str(maximum))
    binData = np.loadtxt(args.bins)
    if (np.min(binData) < minimum) or (np.max(binData) > maximum):
        print('Bins intervals exceede the available wawelenghts. Please check your bins and make sure they are within the following limits')
        print('Minimum: ' + str(minimum) + '\n')
        print('Maximum: ' + str(maximum) + '\n')
        sys.exit('Check your bins')
        #check if the bins are within range of wawelenghts
    
    p = Pool(cpuNumber)    
    p.map(reducing, depthList)
    
  
def reducing(currentFile):
    counter = currentFile
    currentFile = str(currentFile).zfill(depthLength) + '.segment'
    print('Reducing: ' + str(currentFile))
    data = np.loadtxt(currentFile) #load the current file to memory
    binData = np.loadtxt(args.bins)
    for singleBin in binData: #for each bin
        tempList = np.array([[0,0,0],[0,0,0]]) #list for storing the data which we then write to the file in the end
        encounteredBinYet = False
        for line in data: #for each line in a segmentFile
            outsideOfTheBin = True
            if (line[0] >= singleBin[0]) and ((line[0] + line[2]) <= singleBin[1]): #check if the wawelength of the current line is within the bin, append it
                tempList = np.vstack([tempList, line])
                outsideOfTheBin = False
                encounteredBinYet = True
                if (np.array_equal(line, data[-1])): #if we are on the last line, we must also sort the array otherwise it will go unsorted                   
                    tempList = sort_array(tempList, 1, 2) #sort by opacities
                    f = open(currentFile.split('.')[0] + '.binned' + args.subBins.split('s')[-1], "a")
                    np.savetxt(f, tempList, fmt = floatFormat)
                    f.close()
                    sub_bins(args.subBins, singleBin, tempList, counter)
                    
            elif ((outsideOfTheBin == True) and (encounteredBinYet == True)):                    
                tempList = sort_array(tempList, 1, 2)#sort by opacities
                f = open(currentFile.split('.')[0] + '.binned' + args.subBins.split('s')[-1], "a")
                np.savetxt(f, tempList, fmt = floatFormat)
                f.close()
                sub_bins(args.subBins, singleBin, tempList, counter)
                break #once we leave the part of the file containing current bin, break and go to the next segment file
    

def sub_bins(subBinFile, singleBin, tempList, counter):
    subBins = np.loadtxt(subBinFile)
    subBinsLength = np.array([0.])
    for line in subBins: subBinsLength = np.append(subBinsLength, (singleBin[1]-singleBin[0]) * (line[1] - line[0]))
    subBinsLength = np.delete(subBinsLength, (0), axis=0)
    subBinsLength = np.around(subBinsLength, 7)
    subBinsLength = subBinsLength[::-1]
    deltaLambda, temp, beginning, end = 0, 0, singleBin[0], 0
    subbinArray = np.array([1,1,1])
    i = 0
    for line in tempList: #templist contains one bin
        subBinSize = subBinsLength[i]
        deltaLambda += line[2]
        temp += line[1] * line[2] #opacity_i*deltaLambda_i
        if np.greater_equal(deltaLambda, subBinSize):
            i += 1
            end = beginning + deltaLambda
            if (np.array_equal(line,tempList[-1])): end = singleBin[1] # set end to the end of the bin if we are in the last line
            temp /= deltaLambda
            deltaLambda = 0
            subbinArray = np.vstack([subbinArray,[beginning, end, temp]])
            beginning = end
            end, temp = 0, 0
            if (np.array_equal(line,tempList[-1])):
                end = singleBin[1]
                subbinArray = np.delete(subbinArray, (0), axis=0)
                f = open(str(counter) + '.r' + args.subBins.split('s')[-1], "a")
                np.savetxt(f, subbinArray, fmt = floatFormat)
                f.close()
        elif (np.array_equal(line,tempList[-1])):
            end = singleBin[1]
            temp /= deltaLambda
            deltaLambda = 0
            subbinArray = np.vstack([subbinArray,[beginning, end, temp]])
            subbinArray = np.delete(subbinArray, (0), axis=0)
            f = open(str(counter) + '.r' + args.subBins.split('s')[-1], "a")
            np.savetxt(f, subbinArray, fmt = floatFormat)
            f.close()



def sort_array(array, column, removeHeader):
    if removeHeader > 0:
        for i in range(0, removeHeader):
            array = np.delete(array, (0), axis=0)
    array = array[np.argsort(array[:,column])]
    return array
  
def write_array(array, fileName, removeHeader = 0, resetTo = 0):
    """Deletes the header of the array before writing it to the disk.

    Writes the array as fileName while removing removeHeader lines from array and returning resetTo.

    Parameters
    ----------
    array : np.array
        Array to be written.
    fileName : str
        File to write to.
    removeHeader : int
        Number of header lines to delete before writing.
    resetTo : int/float/np.array...
        Returns this object.

    Returns
    -------
    resetTo
        Returns the object specified in arguments, by default it is integer 0.

    """
    if removeHeader > 0:
        for i in range(0, removeHeader):
            array = np.delete(array, (0), axis=0)
    f = open(fileName, "a")
    np.savetxt(f, array, fmt = floatFormat)
    f.close()
    if resetTo != 0:
        array = np.array(resetTo)
    return array


bining(depthList)