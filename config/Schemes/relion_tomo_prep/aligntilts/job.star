
# version 30001

data_job

_rlnJobTypeLabel             relion.aligntiltseries
_rlnJobIsContinue                       0
_rlnJobIsTomo                           0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
aretomo_thickness        250 
aretomo_tiltcorrect        Yes 
do_aretomo        Yes 
do_imod_fiducials         No 
do_imod_patchtrack         No 
  do_queue        Yes 
fiducial_diameter         10 
   gpu_ids        0:1 
in_tiltseries Schemes/relion_tomo_prep/filtertilts/tiltseries_filtered.star 
min_dedicated          1 
other_args         "" 
patch_overlap         50 
patch_size        100 
      qsub     sbatch 
qsub_extra1          3 
qsub_extra2          2 
qsub_extra3    p.hpcl8 
qsub_extra4      2 
qsubscript   qsub/qsub_hpcl89.sh 
 queuename    openmpi 
 
