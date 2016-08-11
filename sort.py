import numpy as np
import argparse
import glob
import sys

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
file_list = sorted(glob.glob(args.folder+'*.lopa'))
#print(file_list)
file_list = np.sort(file_list)
#print(file_list)
numberOfItems = len(file_list)
#create a list off all the .lopa files

merged_file = args.merged_file
#create a path to the merged file

def bining(depthList):
    reducedFileList = [str(item) + '.reduced' for item in depthList]
    segmentFileList = [str(item) + '.segment' for item in depthList]
    minMax = np.loadtxt(str(depthList[0]) + '.segment') #get minimum and maximum wawelenghts from the first .segment file
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
    counter = 0
    for currentSegmentFile in segmentFileList: #for every segmentFile
        print('Reducing: ' + str(currentSegmentFile))
        data = [np.array(map(float, line.split())) for line in open(currentSegmentFile)]
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
#==============================================================================
# Subbins
#==============================================================================
                        sub_bins(10, singleBin, tempList, counter, reducedFileList)
                        
                elif ((outsideOfTheBin == True) and (encounteredBinYet == True)):
                    tempList = sort_array(tempList, 1, 2)#sort by opacities                    
                    sub_bins(10, singleBin, tempList, counter, reducedFileList)
                    break #once we leave the part of the file containing current bin, break and go to the next segment file
        counter = counter + 1
  #iterate over the segment files and extract only the data coresponding to the bins
  
def sub_bins(numberOfSubbins, singleBin, tempList, counter, reducedFileList):
    subBinSize = (float(singleBin[1]) - float(singleBin[0])) / numberOfSubbins
#    print('Subbin size: ' + str(subBinSize))
    deltaLambda, temp, beginning, end = 0, 0, singleBin[0], 0
    subbinArray = np.array([1,1,1])
    for line in tempList: #templist contains one bin
#        print(line[2])
        deltaLambda += line[2]
        temp += line[1] * line[2] #opacity_i*deltaLambda_i
#        print(deltaLambda)
        if (deltaLambda >= subBinSize):
            end = beginning + deltaLambda
            temp /= deltaLambda
            deltaLambda = 0
            subbinArray = np.vstack([subbinArray,[beginning, end, temp]])
            beginning = end
            end, temp = 0, 0
        elif (np.array_equal(line,tempList[-1])):
            end = beginning + deltaLambda
            temp /= deltaLambda
            deltaLambda = 0
            subbinArray = np.vstack([subbinArray,[beginning, end, temp]])
            subbinArray = np.delete(subbinArray, (0), axis=0)
            f = open(reducedFileList[counter], "a")
            np.savetxt(f, subbinArray, fmt = '%.6e')
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
    np.savetxt(f, array, fmt = '%.6e')
    f.close()
    if resetTo != 0:
        array = np.array(resetTo)
    return array
    
    
  
def merge_files(filename):
    currentFileIndex = 1.
    depthList = []
    
    #arrays = [np.array(map(float, line.split())) for line in open(file_list[0])]
    arrays = np.loadtxt(file_list[0])
    for array in arrays:
        if ((array[0] % 1) == 0) and ((array[1] % 1) == 0) :
            depthList.append(int(array[1]))
       #get the list of all depth points from the first .lopa file


    for filename in file_list:
        lastSegment = False #tells us whether we are in the last segment of the current file
        print(filename)
        print(str('%.2f'%(currentFileIndex/float(numberOfItems)*100)) + '%')
        currentFileIndex = currentFileIndex + 1.
        #progress bar
        
        tempList = np.array([[0,0],[0,0]]) #define the array to which we later append the data, it is already populated, otherwise we cannot append an array with a size of (2,1) to it
        arrays = [np.array(map(float, line.split())) for line in open(filename)] #load the lopa file
        
        
        for array in arrays: #walk over the lopa file
            if int(array[1]) > 1: #check whether we are in the header line
                currentFile = str(int(array[1])-1) + '.segment'
                tempList = write_array(tempList, currentFile, 2, [[0,0],[0,0]])

                if array[1] == depthList[-1]: #special case if we are in the last segment
                    lastSegment = True
                    currentFile = str(int(array[1])) + '.segment'
                    
            elif int(array[1]) < 1:
                tempList = np.append(tempList, [array], 0) #if we are not in the header, append current line
                if (lastSegment == True) and (np.array_equal(array, arrays[-1])): #if we are in the last segment AND in the last line, write to file
                     tempList = write_array(tempList, currentFile, 2, [[0,0],[0,0]])                    
        
        
    segmentFileList = [str(item) + '.segment' for item in depthList]
    print(depthList)
    print(segmentFileList)
    for currentFile in segmentFileList:
        print('Delta lambda calculations for: ' + str(currentFile))
        workBuffer = np.loadtxt(currentFile,comments=None)
        sortedWorkBuffer = workBuffer[np.argsort(workBuffer[:,0])] #sort by the first column (wavelenghts)
        #sortedWorkBuffer = workBuffer        
        bufferPosition = 0
        deltaLambdaList = np.array([])
        for line in sortedWorkBuffer:
            if bufferPosition <= len(sortedWorkBuffer) - 2:
                deltaLambdaList = np.append(deltaLambdaList, (sortedWorkBuffer[bufferPosition+1][0] - line[0]))
                bufferPosition = bufferPosition + 1
        deltaLambdaList = np.append(deltaLambdaList, 0)
        sortedWorkBuffer = np.c_[sortedWorkBuffer, deltaLambdaList] #append the column with delta lambda values
        np.savetxt(currentFile,sortedWorkBuffer, fmt = '%.6e')
        
        #sort the files and generate the deltaLambda values for each line
#create a separate file for each depth point as listed in depthList
#iterate over the .lopa files as listed in file_list and fill the .segment files

    
    print('segmentFileList length: ' + str(len(segmentFileList)))
    return depthList


depthList = merge_files(file_list)
##depthList = [4,55,67]##
bining(depthList)