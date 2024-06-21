
# version 30001

data_job

_rlnJobTypeLabel             relion.external
_rlnJobIsContinue                       0
_rlnJobIsTomo                           0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
  do_queue         Yes 
    fn_exe /fs/pool/pool-fbeck/projects/4TomoPipe/rel5Pipe/src/CryoBoost/bin/crboost_filterTitlts.py
  in_3dref         "" 
 in_coords         "" 
   in_mask         "" 
    in_mic         Schemes/relion_tomo_prep/ctffind/tilt_series_ctf.star
    in_mov         "" 
   in_part         "" 
min_dedicated          1 
nr_threads          24
other_args         "" 
param10_label         "" 
param10_value         "" 
param1_label      model 
param1_value      default
param2_label      defocusInAng
param2_value      2000,140000,-70,70 
param3_label      ctfMaxResolution
param3_value      0,50,-70,70 
param4_label      driftInAng
param4_value      1,90000,-70,70    
param5_label         "" 
param5_value         "" 
param6_label         "" 
param6_value         "" 
param7_label         "" 
param7_value         "" 
param8_label         "" 
param8_value         "" 
param9_label         "" 
param9_value         "" 
      qsub     sbatch 
qsub_extra1          1 
qsub_extra2          1 
qsub_extra3    p.hpcl8 
qsub_extra4      2 
qsub_extra5      370G
qsubscript    qsub/qsub_hpcl89.sh 
 queuename    openmpi 
 
