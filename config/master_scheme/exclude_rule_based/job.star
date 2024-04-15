
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
  do_queue         No 
    fn_exe ../../../../00-Other/CryoTheraPy/bin/parser_exclude_tilts_rules.py 
  in_3dref         "" 
 in_coords         "" 
   in_mask         "" 
    in_mic         Schemes/master_scheme/feature_analysis/feature_analysis.star 
    in_mov         "" 
   in_part         "" 
min_dedicated          1 
nr_threads          1 
other_args         "" 
param10_label         "" 
param10_value         "" 
param1_label      shift 
param1_value       0-20 
param2_label    defocus 
param2_value 15000-40000 
param3_label resolution 
param3_value       0-20 
param4_label         "" 
param4_value         "" 
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
qsub_extra1          3 
qsub_extra2          3 
qsub_extra3    p.hpcl8 
qsub_extra4      gpu:2 
qsubscript /fs/pool/pool-bmapps/hpcl8/app/soft/RELION/5.0-beta-1//scripts/qsub.sh 
 queuename    openmpi 
 
