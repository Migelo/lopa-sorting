import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Generate bins.')
parser.add_argument('beginning', help='Beginning of the first bin.', type=int)
parser.add_argument('end', help='End of the last bin.', type=int)
parser.add_argument('interval', help='Size of the bin.', type=int)
parser.add_argument('outputFile', type=str, help='Set the output file.')
args = parser.parse_args()
#set the necessary parameters for parsing

bins = np.array([0,0])
i = args.beginning
interval = args.interval
while i + interval <= args.end:
   bins = np.vstack([bins, [i, i + interval]])
   i += interval
bins = np.delete(bins, (0), axis=0)
np.savetxt(args.outputFile, bins, fmt = '%.4d')