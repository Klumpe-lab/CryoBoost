
# version 30001

data_job

_rlnJobTypeLabel             relion.reconstructtomograms
_rlnJobIsContinue                       0
_rlnJobIsTomo                           0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
binned_angpix      11.72 
  do_queue        Yes 
generate_split_tomograms         No 
in_tiltseries Schemes/relion_tomo_prep/aligntilts/aligned_tilt_series.star
min_dedicated          1 
    nr_mpi          3 
nr_threads          24 
other_args         "" 
      qsub     sbatch 
qsub_extra1          3 
qsub_extra2          1 
qsub_extra3    p.hpcl8 
qsub_extra4          2 
qsubscript     qsub/qsub_hpcl89.sh 
 queuename    openmpi 
 tomo_name         "" 
      xdim       4096 
      ydim       4096 
      zdim       2048 
 
