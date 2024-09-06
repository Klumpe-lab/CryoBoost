
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
in_tiltseries Schemes/relion_tomo_prep/aligntilts/aligned_tilt_series.star
xdim       4096 
ydim       4096 
zdim       2048 
binned_angpix      11.72 
generate_split_tomograms         No 
tiltangle_offset          0 
tomo_name         "" 
do_proj        Yes 
centre_proj          0
thickness_proj         10 
nr_mpi          3 
nr_threads          24 
do_queue        Yes 
queuename    openmpi 
qsub     sbatch 
qsubscript     qsub/qsub_hpcl89.sh 
min_dedicated          1 
other_args         "" 
qsub_extra1          3 
qsub_extra2          1 
qsub_extra3    p.hpcl8 
qsub_extra4          2 
qsub_extra5      370G
 
