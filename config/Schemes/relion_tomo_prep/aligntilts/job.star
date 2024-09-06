
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
in_tiltseries Schemes/relion_tomo_prep/filtertilts/tiltseries_filtered.star 
do_imod_fiducials         No 
fiducial_diameter         10 
do_imod_patchtrack         No 
patch_size        100 
patch_overlap         50 
do_aretomo        Yes 
aretomo_thickness        250 
aretomo_tiltcorrect        Yes 
gpu_ids        0:1 
do_queue        Yes 
queuename    openmpi 
qsub     sbatch 
qsubscript   qsub/qsub_hpcl89.sh 
min_dedicated          1 
other_args         "" 
qsub_extra1          1 
qsub_extra2          1 
qsub_extra3    p.hpcl8 
qsub_extra4      2 
qsub_extra5      370G
 
