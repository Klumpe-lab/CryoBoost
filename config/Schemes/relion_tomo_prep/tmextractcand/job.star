
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
    fn_exe         crboost_extract_tm_candidates.py
  in_3dref         "" 
 in_coords         "" 
   in_mask         "" 
    in_mic         Schemes/relion_tomo_prep/templatematching/tomograms.star
    in_mov         "" 
   in_part         "" 
other_args         "--implementation pytom \"  
param1_label      "cutOffMethod" 
param1_value      "NumberOfFalsePositives" 
param2_label      "cutOffValue" 
param2_value      "1" 
param3_label      "scoreFilter" 
param3_value      "None" 
param4_label      "particleDiameterInAng" 
param4_value      "200"
param6_label      "maxNumParticles"
param6_value      "1500"    
param5_label      "apixScoreMap"
param5_value      "auto" 
param7_label      ""
param7_value      ""
param8_label      "" 
param8_value      "" 
param9_label      "" 
param9_value      "" 
param10_label     "" 
param10_value     "" 
nr_threads        1
do_queue         Yes 
queuename    openmpi 
qsub     sbatch 
qsubscript    qsub/qsub_relion_hpcl89.sh 
min_dedicated          1 
qsub_extra1          1 
qsub_extra2          1 
qsub_extra3    p.hpcl8 
qsub_extra4      2 
qsub_extra5      370G
 
