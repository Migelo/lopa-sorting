import numpy as np
import argparse
import glob
from natsort import natsorted


parser = argparse.ArgumentParser(description='Lopa files contain line opacity values for a small wavelength interval over all depth points. This script takes the lopa files and outputs segment files containing opacity values for all wavelengths for a single depth point')
parser.add_argument('folder', type=str, help='Folder with .lopa files to be processed')
args = parser.parse_args()


def deltaLambda(segment):
    """Calculates the deltaLambda for the given segment.

    Calculates the difference in wawelength in two adjancent data points in the segment.

    Parameters
    ----------
    segment : list
        list containing the current segment

    Returns
    -------
    list
        List with deltaLambdas as the third column.

    """
    for position in range(len(segment) - 1):
        segment[position].append(segment[position + 1][0] - segment[position][0])
    return segment
##############################################################################


def deleteOverlapping(tempList, fileName):
    """Deletes the overlapping parts of a .lopa file.

    Each .lopa file contains parts which partially overlap with the adjecent .lopa files, this function deletes those parts. If the file is first or last, it will only delete the last or first part respectively.

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
    if fileName == 0:
        specialPosition = 0
    elif fileName == len(file_list) - 1:
        specialPosition = -1
    else:
        specialPosition = 1
    fileName = int(file_list[fileName].split('/')[-1].split('.')[-2])
    minimum = fileName - 5.
    maximum = fileName + 5.

    if specialPosition == 1:
        tempTempList = [line for line in tempList if (line[0] < maximum) and (line[0] > minimum)]
    elif specialPosition == -1:
        tempTempList = [line for line in tempList if (line[0] < maximum)]
    elif specialPosition == 0:
        tempTempList = [line for line in tempList if (line[0] > minimum)]
    return tempTempList
##############################################################################

# create a list off all .lopa files
file_list = natsorted(glob.glob(str(args.folder) + '/*.lopa'), reverse=True)

# load an arbirtary file and determine number of depthpoints
firstFile = np.loadtxt(file_list[int(len(file_list) / 2)])
depth = 0
for array in firstFile:
    if ((array[0] % 1) == 0) and ((array[1] % 1) == 0) and (int(array[1]) > 0):  # check whether we are in the header line
        depth += 1
print("Number of depthpoints: " + str(depth))
depthList = range(1, depth + 1)


"""Load the files. Each item in data contains one lopa file"""
data = []

print("Loading files")
for item in file_list:
    print("File: ", item)
    data.append(np.loadtxt(item).tolist())
print("Files loaded")

"""Walk over the already loaded lopa file"""
file_number = 0
segments = []
for item in depthList:
    segments.insert(0, [])
for item in data:
    segment = -1
    segment_temp = []
    for line in item:
        if ((line[0] % 1) == 0) and ((line[1] % 1) == 0) and (int(line[1]) > 0):  # check whether we are in the header line
            if segment == -1:
                pass
            else:
                segment_temp = deleteOverlapping(segment_temp, file_number)
                for itemm in segment_temp:
                    segments[segment].append(itemm)
                segment_temp = []
            segment += 1
        else:
            segment_temp.append(line)
            if line[0] == item[-1][0]:
                segment_temp = deleteOverlapping(segment_temp, file_number)
                for itemmm in segment_temp:
                    segments[segment].append(itemmm)
                segment_temp = []
    file_number += 1

# Delta lambdas and writing files
for segment in range(len(segments)):
    segments[segment] = deltaLambda(segments[segment][::-1])
    segments[segment][-1].append(segments[segment][-2][-1])
    np.savetxt(str(segment + 1) + '.segment', segments[segment])
