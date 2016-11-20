# lopa-sorting


python 2.7 required


1. create the bins and subBins file by hand or using the bins.py (suggested name for subBins file is 'subBins' + some description, see 5.)
2. get the lopa files in a folder and run the mergeLopa.py, specifying the folder with the lopa files, bins file and cpuNumber
3. in the current directory the code will make 82 .segment files
4. run the sort.py in the directory with the .segment files, specifying the bins, subBins and cpuNumber
5. you end up with filenames which have the name like this: "*.r"+ (whatever comes after the last letter "s" in the subBins file) (if subBins file is named "subBins3c", the reduced files will be named "#.r3c")
6. open the job.sh script where you change the 32th line (also says changeMe on the line) to match the name of the reduced files, in our case, if we have "subBins3c" we put "3c"
7. copy the script to IT_ASPLUND_C directory
8. make sure the path to bins and reference spectra is correct in the script
9. login to helios1
10. qsub job.sh
11. If everything goes well you will end up with 3 files on the deskop (spectra3csub - pure spectra, spectra3csub.averaged - spectra averaged over bins, spectra3cComparison - comparison to reference spectra)


Explanation:

* bins.py - makes the bins or subBins file
* mdispCompare.py - averages the spectra and reference spectra and compares them
* mergeLopa.py - merges lopa files into segment files which represent one depthPoint
* mergeMdisp - merges mdisp files into a single file
* sory.py - reduces the segment files to subBins

stupid shit
