#! /bin/bash

# first job - no dependencies
jid1=$(sbatch  retrieval_prep.slurm)

# multiple jobs can depend on a single job
jid2=$(sbatch  --dependency=afterany:$jid1 retrieval.slurm)


