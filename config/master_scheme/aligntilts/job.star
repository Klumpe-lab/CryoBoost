
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
aretomo_thickness        200 
aretomo_tiltcorrect        Yes 
do_aretomo        Yes 
do_imod_fiducials         No 
do_imod_patchtrack         No 
  do_queue        Yes 
fiducial_diameter         10 
   gpu_ids        0:1 
in_tiltseries Schemes/master_scheme/exclude_rule_based/excluded_tilts_rule.star 
min_dedicated          1 
other_args         "" 
patch_overlap         50 
patch_size        100 
      qsub     sbatch 
qsub_extra1          3 
qsub_extra2          2 
qsub_extra3    p.hpcl8 
qsub_extra4      gpu:2 
qsubscript ../../qsub_gpu_Relion5.sh 
 queuename    openmpi 
 
