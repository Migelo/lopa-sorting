import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Generate bins.')
parser.add_argument('beginning', help='Beginning of the first bin.', type=str)
parser.add_argument('end', help='End of the last bin.', type=str)
parser.add_argument('-interval', help='Size of the bin.', type=int)
parser.add_argument('-n', help='Number of bins.', type=int)
parser.add_argument('outputFile', type=str, help='Set the output file.')
parser.add_argument('-sb', type=bool, default=False, help='Use when \
                    creating sub-bins.')
args = parser.parse_args()

args.beginning = np.float(args.beginning)
args.end = np.float(args.end)

if (args.interval is not None) and (args.n is not None):
    parser.error('-n and -interval are mutually exclusive')

bins = []
i = args.beginning
if args.interval is not None:
    interval = args.interval
    while i < args.end:
        if i + interval > args.end:
            bins.append([i, args.end])
        else:
            bins.append([i, i + interval])
        i += interval
elif args.n is not None:
    if args.sb:
        interval = 1.
    else:
        interval = (args.end - args.beginning) / args.n
    for j in range(args.n):
        bins.append([i, i + interval])
        i += interval

np.savetxt(args.outputFile, bins)
