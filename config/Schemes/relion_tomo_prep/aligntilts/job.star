# version 50001

data_job

_rlnJobTypeLabel             relion.aligntiltseries
_rlnJobIsContinue                       0
_rlnJobIsTomo                           0
 

# version 50001

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
do_aretomo2        Yes 
do_aretomo_ctf         No 
do_aretomo_phaseshift         No 
do_aretomo_tiltcorrect         Yes 
aretomo_tiltcorrect_angle        999 
tomogram_thickness        250 
other_aretomo_args         "" 
fn_aretomo_exe    /fs/pool/pool-bmapps/hpcl8/app/soft/ARETOMO2/1.1.2/AreTomo2
fn_batchtomo_exe /fs/pool/pool-bmapps/hpcl8/app/soft/IMOD/4.12.17/bin/batchruntomo
min_dedicated          1 
gpu_ids    0:1 
do_queue        Yes 
other_args         "" 
queuename    openmpi 
qsub        sbatch 
qsubscript qsub/qsub_relion_hpcl89.sh 
nr_mpi          3 
qsub_extra1          1 
qsub_extra2          1 
qsub_extra3   p.hpcl8 
qsub_extra4          2 
qsub_extra5       370G 
