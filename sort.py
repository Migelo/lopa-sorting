import numpy as np
import argparse
import glob
import sys
from multiprocessing import Pool

parser = argparse.ArgumentParser(description='Sort the spectra.')
parser.add_argument('folder', metavar='FOLDER', type=str,
                  help='FOLDER with .lopa files to be processed')
parser.add_argument('--bins', metavar='bins', type=str,
                   help='file defining the wawelenghts bins')
parser.add_argument('--merged_file', type=str, default="merged.lopa",
                   help='set the location of the merged file, by default it will be stored in the current directory under the name "merged.lopa"')
#parser.add_argument('-n','--sub-bin-number', metavar='subbins', action='store_const',
#                  help='set the number of subbin each bin will be split during calculations')

args = parser.parse_args()
#set the necessary parameters for parsing

file_list = []
file_list = sorted(glob.glob(args.folder+'/*.lopa'), reverse=True)
#file_list = np.sort(file_list)
numberOfItems = len(file_list)
#create a list off all the .lopa files

merged_file = args.merged_file
#create a path to the merged file

cpuNumber = 42
#number of cores to use

def bining(depthList):
    minMax = np.loadtxt(str(depthList[0]).zfill(len(str(np.max(depthList)))) + '.segment') #get minimum and maximum wawelenghts from the first .segment file
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
    currentFile = str(currentFile).zfill(2) + '.segment'
    print('Reducing: ' + str(currentFile))
    data = np.loadtxt(currentFile) #load the current file to memory
    binData = np.loadtxt(args.bins)
    for singleBin in binData: #for each bin
        tempList = np.array([[0,0,0],[0,0,0]]) #list for storing the data which we then write to the file in the end
        encounteredBinYet = False
        for line in data: #for each line in a segmentFile
            outsideOfTheBin = True
            if (line[0] >= singleBin[0]) and (line[0] <= singleBin[1]): #check if the wawelength of the current line is within the bin, append it
                tempList = np.vstack([tempList, line])
                outsideOfTheBin = False
                encounteredBinYet = True
                if (np.array_equal(line, data[-1])): #if we are on the last line, we must also sort the array otherwise it will go unsorted                   
                    tempList = sort_array(tempList, 1, 2) #sort by opacities
                    sub_bins(1, singleBin, tempList, counter)
                    
            elif ((outsideOfTheBin == True) and (encounteredBinYet == True)):                    
                tempList = sort_array(tempList, 1, 2)#sort by opacities
                sub_bins(1, singleBin, tempList, counter)
                break #once we leave the part of the file containing current bin, break and go to the next segment file
    
    
def sub_bins(numberOfSubbins, singleBin, tempList, counter):
    subBinSize = (float(singleBin[1]) - float(singleBin[0])) / numberOfSubbins
    deltaLambda, temp, beginning, end = 0, 0, singleBin[0], 0
    subbinArray = np.array([1,1,1])
    for line in tempList: #templist contains one bin
        deltaLambda += line[2]
        temp += line[1] * line[2] #opacity_i*deltaLambda_i
        if (deltaLambda >= subBinSize):
            end = beginning + deltaLambda
            temp /= deltaLambda
            deltaLambda = 0
            subbinArray = np.vstack([subbinArray,[beginning, end, temp]])
            beginning = end
            end, temp = 0, 0
            if (np.array_equal(line,tempList[-1])):
                subbinArray = np.delete(subbinArray, (0), axis=0)
                f = open(str(counter) + '.reduced', "a")
                np.savetxt(f, subbinArray, fmt = '%.7e')
                f.close()
        elif (np.array_equal(line,tempList[-1])):
            end = beginning + deltaLambda
            temp /= deltaLambda
            deltaLambda = 0
            subbinArray = np.vstack([subbinArray,[beginning, end, temp]])
            subbinArray = np.delete(subbinArray, (0), axis=0)
            f = open(str(counter) + '.reduced', "a")
            np.savetxt(f, subbinArray, fmt = '%.7e')
            f.close()
  
def sort_array(array, column, removeHeader):
    if removeHeader > 0:
        for i in range(0, removeHeader):
            array = np.delete(array, (0), axis=0)
    array = array[np.argsort(array[:,column])]
    return array
  
def write_array(array, fileName, removeHeader = 0, resetTo = 0):
    if removeHeader > 0:
        for i in range(0, removeHeader):
            array = np.delete(array, (0), axis=0)
    f = open(fileName, "a")
    np.savetxt(f, array, fmt = '%.7e')
    f.close()
    if resetTo != 0:
        array = np.array(resetTo)
    return array

def deltaLambda(currentFile):
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
    np.savetxt(currentFile,sortedWorkBuffer, fmt = '%.7e')
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
    
  
def merge_files(filename):
    currentFileIndex = 1.
    depthList = []
    
    arrays = np.loadtxt(file_list[0])
    for array in arrays:
        if ((array[0] % 1) == 0) and ((array[1] % 1) == 0) and (int(array[1]) > 0):
            depthList.append(int(array[1]))
    #get the list of all depth points from the first .lopa file

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
#                    print('we are in the last segment')
                    currentFile = str(int(array[1])-1).zfill(len(str(np.max(depthList)))) + '.segment'
                    tempList = deleteOverlapping(tempList, filename)
                    tempList = write_array(tempList, currentFile, 0, [[0,0],[0,0]])
                    currentFile = str(int(array[1])).zfill(len(str(np.max(depthList)))) + '.segment'
                elif int(array[1] != 1):
                    currentFile = str(int(array[1])-1).zfill(len(str(np.max(depthList)))) + '.segment'
                    tempList = deleteOverlapping(tempList, filename)
                    tempList = write_array(tempList, currentFile, 0, [[0,0],[0,0]])
#                    print('Writing to: ' + currentFile)
            else:
                tempList = np.append(tempList, [array], 0) #if we are not in the header, append current line
                if (lastSegment == True) and (np.array_equal(array, arrays[-1])): #if we are in the last segment AND in the last line, write to file
                    tempList = deleteOverlapping(tempList, filename)
                    tempList = write_array(tempList, currentFile, 0, [[0,0],[0,0]])
#                    print('Writing to: ' + currentFile)
        
        
    segmentFileList = [str(item).zfill(len(str(np.max(depthList)))) + '.segment' for item in depthList]
    p = Pool(cpuNumber)
    p.map(deltaLambda, segmentFileList)
    #sort the files and generate the deltaLambda values for each line
#create a separate file for each depth point as listed in depthList
#iterate over the .lopa files as listed in file_list and fill the .segment files

    
    print('segmentFileList length: ' + str(len(segmentFileList)))
    return depthList


depthList = merge_files(file_list)


bining(depthList)