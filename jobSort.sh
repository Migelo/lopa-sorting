#!/bin/bash
#PBS -q atlasq
#PBS -N lopa-sorting
#PBS -M cernetic@mps.mpg.de
#PBS -l nodes=2:ppn=48
#PBS -l walltime=100:00:00

# name(s) of module(s) to load
MODULES=mvapich2_pgi

# initialize modules environment
. $MODULESHOME/init/bash

# load module(s)
module load $MODULES

# change to submit dir
cd $PBS_O_WORKDIR

# number of processes
NP=$(cat $PBS_NODEFILE | wc -l)

# number of processes per node
PPN=$(($NP/$(cat $PBS_NODEFILE|uniq|wc -l)))

# set number of hardware contexts
export PSM_SHAREDCONTEXTS_MAX=$(((($PPN+3))/4))

# start your job
	python /home/cernetic/Documents/sorting/lopa-sorting/sort.py ~/Documents/sorting/lopa-sorting/bins ~/Documents/sorting/lopa-sorting/subBinsTest 82
# unload module(s)
module unload $MODULES

