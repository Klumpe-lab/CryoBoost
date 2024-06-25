
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
care_denoising_model         "" 
cryocare_path /fs/pool/pool-bmapps/hpcl8/app/soft/CRYO-CARE/0.2/conda3/envs/cryocare_11/bin/ 
denoising_tomo_name         "" 
do_cryocare_predict         No 
do_cryocare_train        Yes 
  do_queue        Yes 
   gpu_ids          0 
in_tomoset  Schemes/relion_tomo_prep/reconstruction/tomograms.star 
min_dedicated          1 
  ntiles_x          2 
  ntiles_y          2 
  ntiles_z          2 
number_training_subvolumes        600 
other_args         "" 
      qsub     sbatch 
qsub_extra1          1 
qsub_extra2          1 
qsub_extra3   p.hpcl93 
qsub_extra4          1 
qsub_extra5       384G 
qsubscript /fs/pool/pool-bmapps/hpcl8/app/soft/RELION/5.0-beta-3//scripts/qsubNC.sh 
 queuename    openmpi 
subvolume_dimensions         64 
tomograms_for_training Position_1 
 
