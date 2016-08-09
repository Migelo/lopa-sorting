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
file_list = glob.glob(args.folder+'/*.lopa')
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
    for currentSegmentFile in segmentFileList:
        print('Reducing: ' + str(currentSegmentFile))
        #f = open(reducedFileList[counter], 'a')
        #data = np.loadtxt(currentSegmentFile) #loads the n-th segment file for processing
        data = [np.array(map(float, line.split())) for line in open(currentSegmentFile)]
        for singleBin in binData:
            tempList = np.array([[0,0,0],[0,0,0]]) #list for storing the data which we then write to the file in the end
            encounteredBinYet = False
            for line in data:
                outsideOfTheBin = True
                if (line[0] >= singleBin[0]) and (line[0] <= singleBin[1]):
                    ##tempList = np.append(tempList, [line], 0)
                    tempList = np.vstack([tempList, line])
                    #f.write(str(line[0]) + '   ' + str(line[1]) + '\n')
                    outsideOfTheBin = False
                    encounteredBinYet = True
                elif ((outsideOfTheBin == True) and (encounteredBinYet == True)):
                    tempList = np.delete(tempList, (0), axis=0)
                    tempList = np.delete(tempList, (0), axis=0)
                    tempList = tempList[np.argsort(tempList[:,1])] #sort by opacities

                    numberOfSubbins = 10
                    subbinSize = (singleBin[1] - singleBin[0]) / numberOfSubbins
                    print('Subbin size: ' + str(singleBin[1]-singleBin[0]))
                    deltaLambda, temp, beginning, end = 0, 0, singleBin[0], 0
                    subbinArray = np.array([0,0,0])
                    for line in tempList:
                        deltaLambda = deltaLambda + line[2]
                        temp += line[1] * line[2] #opacity_i*deltaLambda_i
                        if (deltaLambda >= subbinSize):
                            end += beginning + deltaLambda
                            beginning += deltaLambda
                            deltaLambda = 0
                            temp /= subbinSize
                            subbinArray = np.vstack([subbinArray,[beginning, end, temp]])
                            temp = 0
                        elif (np.array_equal(line,tempList[-1])):
                            end += beginning + deltaLambda
                            beginning += deltaLambda
                            deltaLambda = 0
                            temp /= subbinSize
                            subbinArray = np.vstack([subbinArray,[beginning, end, temp]])
                            subbinArray = np.delete(subbinArray, (0), axis=0)
                            f = open(reducedFileList[counter], "a")
                            np.savetxt(f, subbinArray, fmt = '%.6e')
                            f.close()
                            temp = 0
                                        
                    #tenValuesList = np.array([])
                    #for i in range(0, tempList, stepSize):
                    #tenValuesList = np.append(tenValuesList, tempList[i])
                    #with open(reducedFileList[counter], 'a') as f:
                    ##f = open(reducedFileList[counter], "a")
                    ##np.savetxt(f, tempList, fmt = '%.6e')
                    ##f.write('\n')
                    ##f.close()
                    break
        #print(tempList)
        counter = counter + 1
  #iterate over the segment files and extract only the data coresponding to the bins
  
  
  
def merge_files(filename):
    currentFileIndex = 1.
    depthList = []
    
    arrays = [np.array(map(float, line.split())) for line in open(file_list[0])]
    for array in arrays:
        if int(array[1]) > 0:
            depthList.append(int(array[1]))
       #get the list of all depth points from the first .lupa file


    for filename in file_list:
        print(filename)
        print(str('%.2f'%(currentFileIndex/float(numberOfItems)*100)) + '%')
        currentFileIndex = currentFileIndex + 1.
        #progress bar
        
        tempList = np.array([[0,0],[0,0]])##
        arrays = [np.array(map(float, line.split())) for line in open(filename)]
        
        
        for array in arrays:
            if int(array[1]) > 0:
                if int(array[1]) == 2:
                    tempList = np.delete(tempList, (0), axis=0)
                    tempList = np.delete(tempList, (0), axis=0)
                    currentFile = str(int(array[1]-1)) + '.segment'
                    f = open(currentFile, "a")
                    np.savetxt(f, tempList, fmt = '%.6e')
                    f.close()
                    tempList = np.array([[0,0],[0,0]])##
                elif int(array[1]) > 1:
                    tempList = np.delete(tempList, (0), axis=0)
                    tempList = np.delete(tempList, (0), axis=0)
                    f = open(currentFile, "a")
                    np.savetxt(f, tempList, fmt = '%.6e')
                    #np.savetxt(currentFile, tempList, fmt = '%.5e')
                    f.close()
                    tempList = np.array([[0,0],[0,0]])##
                currentFile = str(int(array[1])) + '.segment'
                ##f = open(currentFile, 'a')
            else:
                tempList = np.append(tempList, [array], 0)##
                #print array
                ##f.write(str(array[0]) + '   ' + str(array[1]) + '\n')
        tempList = np.delete(tempList, (0), axis=0)
        tempList = np.delete(tempList, (0), axis=0)
        f = open(currentFile, "a")
        np.savetxt(f, tempList, fmt = '%.6e')
        f.close()
        tempList = np.array([[0,0],[0,0]])##
        np.savetxt(currentFile, tempList, fmt = '%.6e')
        
        
    segmentFileList = [str(item) + '.segment' for item in depthList]
    for currentFile in segmentFileList:
        print('Sorting: ' + str(currentFile))
        workBuffer = np.loadtxt(currentFile,comments=None)
        sortedWorkBuffer = workBuffer[np.argsort(workBuffer[:,0])] #sort by the first column (wavelenghts)
        bufferPosition = 0
        deltaLambdaList = np.array([])
        for line in sortedWorkBuffer:
            if bufferPosition <= len(sortedWorkBuffer)-2:
                deltaLambdaList = np.append(deltaLambdaList, (sortedWorkBuffer[bufferPosition+1][0] - line[0]))
                bufferPosition = bufferPosition + 1
        deltaLambdaList = np.append(deltaLambdaList, 0)
        sortedWorkBuffer = np.c_[sortedWorkBuffer, deltaLambdaList] #append the column with delta lambda values
        np.savetxt(currentFile,sortedWorkBuffer, fmt = '%.6e')
        
        #sor the files and generate the deltaLambda values for each line
#create a separate file for each depth point as listed in depthList
#iterate over the .lopa files as listed in file_list and fill the .segment files

    
    print('segmentFileList length: ' + str(len(segmentFileList)))
    return depthList


depthList = merge_files(file_list)
##depthList = [4,55,67]##
bining(depthList)


