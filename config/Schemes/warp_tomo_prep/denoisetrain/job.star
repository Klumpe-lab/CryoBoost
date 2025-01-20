
# version 50001

data_job

_rlnJobTypeLabel             relion.denoisetomo
_rlnJobIsContinue                       1
_rlnJobIsTomo                           0
 

# version 50001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
in_tomoset  Schemes/warp_tomo_prep/tsReconstruct/tomograms.star 
cryocare_path /fs/pool/pool-bmapps/hpcl8/app/soft/CRYO-CARE/0.3/conda3/envs/cryocare_11/bin/ 
gpu_ids          0 
do_cryocare_train        Yes 
tomograms_for_training Position_1 
number_training_subvolumes        600 
subvolume_dimensions         64 
do_cryocare_predict         No 
care_denoising_model         "" 
ntiles_x          2 
ntiles_y          2 
ntiles_z          2 
denoising_tomo_name         "" 
do_queue        Yes 
queuename    openmpi 
qsub     sbatch 
qsubscript qsub/qsub_relion_hpcl89.sh 
min_dedicated          1 
other_args         "" 
qsub_extra1          1 
qsub_extra2          1 
qsub_extra3   p.hpcl93 
qsub_extra4          1 
qsub_extra5       384G  
