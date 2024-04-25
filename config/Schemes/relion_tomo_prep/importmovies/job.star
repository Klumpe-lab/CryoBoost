
# version 30001

data_job

_rlnJobTypeLabel             relion.importtomo
_rlnJobIsContinue                       0
_rlnJobIsTomo                           0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
        Cs        2.7 
        Q0        0.1 
    angpix       2.93 
 do_coords         No 
do_coords_flipZ         No 
 do_flipYZ        Yes 
  do_flipZ        Yes 
  do_other         No 
  do_queue         No 
do_tiltseries        Yes 
   do_tomo         No 
dose_is_per_movie_frame         No 
 dose_rate          3 
flip_tiltseries_hand         No 
fn_in_other    ref.mrc 
      hand         "" 
images_are_motion_corrected         No 
  io_tomos         "" 
        kV        300 
mdoc_files frames_schemes/*.mdoc 
min_dedicated          1 
movie_files frames_schemes/*.eer 
  mtf_file         "" 
 node_type "Set of tomograms STAR file (.star)" 
optics_group_particles         "" 
order_list         "" 
other_args         "" 
 part_star         "" 
part_tomos         "" 
    prefix         "" 
      qsub     sbatch 
qsub_extra1          3 
qsub_extra2          3 
qsub_extra3    p.hpcl8 
qsub_extra4     2 
qsubscript    qsub/qsub_hpcl89.sh 
 queuename    openmpi 
tilt_axis_angle        -95 
 tomo_star         "" 
 
