
# version 30001

data_job

_rlnJobTypeLabel             relion.motioncorr.own
_rlnJobIsContinue                       0
_rlnJobIsTomo                           1
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
   bfactor        150 
bin_factor          1 
do_even_odd_split        Yes 
do_float16         No 
do_own_motioncor        Yes 
  do_queue        Yes 
do_save_ps        Yes 
eer_grouping         39 
 fn_defect         "" 
fn_gain_ref         "" 
fn_motioncor2_exe /fs/pool/pool-bmapps/hpcl8/app/soft/MOTIONCOR2/1.4.0/bin/motioncor2 
 gain_flip "No flipping (0)" 
  gain_rot "No rotation (0)" 
   gpu_ids          0 
group_for_ps         10 
group_frames          1 
input_star_mics Schemes/relion_tomo_prep/importmovies/tilt_series.star  
min_dedicated          1 
    nr_mpi          72 
nr_threads          1 
other_args         "" 
other_motioncor2_args         "" 
   patch_x          1 
   patch_y          1 
      qsub     sbatch 
qsub_extra1          3 
qsub_extra2          24 
qsub_extra3    p.hpcl8 
qsub_extra4      2 
qsub_extra5      370G
qsubscript    qsub/qsub_hpcl89.sh 
 queuename    openmpi 
 
