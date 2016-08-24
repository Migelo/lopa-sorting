import numpy as np
import argparse
import glob
import sys
from multiprocessing import Pool

parser = argparse.ArgumentParser(description='Sort the spectra.')
parser.add_argument('--folder', type=str, help='Folder with .lopa files to be processed')
parser.add_argument('bins', type=str, help='File defining the wawelenght bins')
parser.add_argument('subBins', help='File defining the subBins distribution.')
parser.add_argument('cpuNumber', type=int, help='Number of CPUs to be used.')

args = parser.parse_args()
#set the necessary parameters for parsing

file_list = []
file_list = sorted(glob.glob(str(args.folder)+'/*.lopa'), reverse=True)
#file_list = np.sort(file_list)
numberOfItems = len(file_list)
#create a list off all the .lopa files

cpuNumber = args.cpuNumber
#number of cores to use

floatFormat = '%.7e'
#format for np.savetxt()

depthList = range(1,83)  
#arrays = np.loadtxt(file_list[0])
#for array in arrays:
#    if ((array[0] % 1) == 0) and ((array[1] % 1) == 0) and (int(array[1]) > 0):
#        depthList.append(int(array[1]))
depthLength = len(str(np.max(depthList)))
#get the list of all depth points from the first .lopa file
#depthLength is created as a global variable so all functions can access it

np.set_printoptions(precision=17)

def merge_files(filename):
    currentFileIndex = 1.

    for filename in file_list:
        lastSegment = False #tells us whether we are in the last segment of the current file
        print(filename)
        print(str('%.2f'%(currentFileIndex/float(numberOfItems)*100)) + '%')
        currentFileIndex = currentFileIndex + 1.
        #progress bar
        
        tempList = np.array([[0,0],[0,0]]) #define the array to which we later append the data, it is already populated, otherwise we cannot append an array with a size of (2,1) to it
        arrays = np.loadtxt(filename) #load the lopa file

        for array in arrays: #walk over the lopa file
            if ((array[0] % 1) == 0) and ((array[1] % 1) == 0) and (int(array[1]) > 0): #check whether we are in the header line
                if array[1] == depthList[-1]: #special case if we are in the last segment of the lopa file
                    lastSegment = True
                    currentFile = str(int(array[1])-1).zfill(depthLength) + '.segment'
                    tempList = deleteOverlapping(tempList, filename)
                    tempList = write_array(tempList, currentFile, 0, [[0,0],[0,0]])
                    currentFile = str(int(array[1])).zfill(depthLength) + '.segment'
                elif int(array[1] != 1):
                    currentFile = str(int(array[1])-1).zfill(depthLength) + '.segment'
                    tempList = deleteOverlapping(tempList, filename)
                    tempList = write_array(tempList, currentFile, 0, [[0,0],[0,0]])
            else:
                tempList = np.append(tempList, [array], 0) #if we are not in the header, append current line
                if (lastSegment == True) and (np.array_equal(array, arrays[-1])): #if we are in the last segment AND in the last line, write to file
                    tempList = deleteOverlapping(tempList, filename)
                    tempList = write_array(tempList, currentFile, 0, [[0,0],[0,0]])        
        
    segmentFileList = [str(item).zfill(depthLength) + '.segment' for item in depthList]
    p = Pool(cpuNumber)
    p.map(deltaLambda, segmentFileList)
    #sort the files and generate the deltaLambda values for each line
#create a separate file for each depth point as listed in depthList
#iterate over the .lopa files as listed in file_list and fill the .segment files

    print('segmentFileList length: ' + str(len(segmentFileList)))
#    return depthList


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
                    sub_bins(args.subBins, singleBin, tempList, counter)
                    
            elif ((outsideOfTheBin == True) and (encounteredBinYet == True)):                    
                tempList = sort_array(tempList, 1, 2)#sort by opacities
                sub_bins(args.subBins, singleBin, tempList, counter)
                break #once we leave the part of the file containing current bin, break and go to the next segment file
    

def sub_bins(subBinFile, singleBin, tempList, counter):
    subBins = np.loadtxt(subBinFile)
    subBins = np.vstack([[0,0], subBins])
    subBins = np.delete(subBins, (0), axis=0)
    subBinsLength = np.array([0.])
    for line in subBins: subBinsLength = np.append(subBinsLength, (singleBin[1]-singleBin[0]) * (line[1] - line[0]))
    subBinsLength = np.delete(subBinsLength, (0), axis=0)
    subBinsLength = np.around(subBinsLength, 7)
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
            if (np.array_equal(line,tempList[-1])): end = singleBin[1]
            temp /= deltaLambda
            deltaLambda = 0
            subbinArray = np.vstack([subbinArray,[beginning, end, temp]])
            beginning = end
            end, temp = 0, 0
            if (np.array_equal(line,tempList[-1])):
                end = singleBin[1]
                subbinArray = np.delete(subbinArray, (0), axis=0)
                f = open(str(counter) + '.reduced' + args.subBins.split('s')[-1], "a")
                np.savetxt(f, subbinArray, fmt = floatFormat)
                f.close()
        elif (np.array_equal(line,tempList[-1])):
            end = singleBin[1]
            temp /= deltaLambda
            deltaLambda = 0
            subbinArray = np.vstack([subbinArray,[beginning, end, temp]])
            subbinArray = np.delete(subbinArray, (0), axis=0)
            f = open(str(counter) + '.reduced' + args.subBins.split('s')[-1], "a")
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

def deltaLambda(currentFile):
    """Calculates the deltaLambda for the given lopa file.

    Calculates the difference in wawelength in two adjancent data points in the given lopa file.

    Parameters
    ----------
    currentFile : string
        name of the file for deltaLambda calculations

    Returns
    -------
    none
        Overwrites the given.

    """
    print('Delta lambda calculations for: ' + str(currentFile))
    workBuffer = np.loadtxt(currentFile,comments=None)
    #sortedWorkBuffer = workBuffer[np.argsort(workBuffer[:,0])] #sort by the first column (wavelenghts)
    sortedWorkBuffer = workBuffer        
    bufferPosition = 0
    deltaLambdaList = np.array([])
    for line in sortedWorkBuffer:
        if bufferPosition <= len(sortedWorkBuffer) - 2:
            deltaLambdaList = np.append(deltaLambdaList, (abs(sortedWorkBuffer[bufferPosition+1][0] - line[0])))
            bufferPosition = bufferPosition + 1
    deltaLambdaList = np.append(deltaLambdaList, 0)
    sortedWorkBuffer = np.c_[sortedWorkBuffer, deltaLambdaList] #append the column with delta lambda values
    np.savetxt(currentFile,sortedWorkBuffer, fmt = floatFormat)
    pass

def deleteOverlapping(tempList, fileName):
    """Deletes the overlapping parts of a .lopa file.

    Each .lopa file contains parts which partially overlap with the next or the previous .lopa file, this function deletes those parts. If the file is first or last, it will only delete the last or first part respectively.

    Parameters
    ----------
    tempList : np.array()
        An array containing one segment of the .lopa file
    fileName : str
        Name of the current .lopa file.

    Returns
    -------
    np.array()
        Array without the overlapping parts.

    """
    tempList = np.delete(tempList, (0), axis=0)
    tempList = np.delete(tempList, (0), axis=0)
    if fileName == file_list[0]: specialPosition = 0
    elif fileName == file_list[-1]: specialPosition = -1
    else: specialPosition = 1
    fileName = int(fileName.split('/')[-1].split('.')[0])
    minimum = fileName - 5.
    maximum = fileName + 5.
    tempTempList = np.array([0,0])

    if specialPosition == 1:
        for line in tempList:
            if (line[0] < maximum) and (line[0] > minimum):
                tempTempList = np.vstack([tempTempList, [line]])
    elif specialPosition == -1:
        for line in tempList:
            if line[0] < maximum:
                tempTempList = np.vstack([tempTempList, [line]])        
    elif specialPosition == 0:
        for line in tempList:
            if line[0] > minimum:
                tempTempList = np.vstack([tempTempList, [line]])
    tempList = np.delete(tempTempList, (0), axis=0)
    return tempList

#merge_files(file_list)
bining(depthList)