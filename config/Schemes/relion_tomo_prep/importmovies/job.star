
# version 50001

data_job

_rlnJobTypeLabel             relion.importtomo
_rlnJobIsContinue                       1
_rlnJobIsTomo                           0
 

# version 50001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
        Cs        2.7 
        Q0        0.1 
    angpix       2.93 
  do_queue         No 
dose_is_per_movie_frame         No 
 dose_rate          3 
flip_tiltseries_hand         No 
images_are_motion_corrected         No 
        kV        300 
mdoc_files ./mdoc/*.mdoc 
min_dedicated          1 
movie_files ./frames/*.eer 
  mtf_file         "" 
optics_group_name         "" 
other_args         "" 
    prefix         "" 
      qsub     sbatch 
qsub_extra1          3 
qsub_extra2          3 
qsub_extra3    p.hpcl8 
qsub_extra4          2 
qsubscript qsub/qsub_hpcl89.sh 
 queuename    openmpi 
tilt_axis_angle        -95 
 
