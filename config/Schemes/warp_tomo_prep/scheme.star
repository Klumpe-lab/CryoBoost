
# version 50001

data_scheme_general

_rlnSchemeName                       Schemes/warp_tomo_prep/
_rlnSchemeCurrentNodeName            WAIT
 

# version 50001

data_scheme_floats

loop_ 
_rlnSchemeFloatVariableName #1 
_rlnSchemeFloatVariableValue #2 
_rlnSchemeFloatVariableResetValue #3 
do_at_most   500.000000   500.000000 
maxtime_hr    48.000000    48.000000 
  wait_sec   180.000000   180.000000 
 

# version 50001

data_scheme_operators

loop_ 
_rlnSchemeOperatorName #1 
_rlnSchemeOperatorType #2 
_rlnSchemeOperatorOutput #3 
_rlnSchemeOperatorInput1 #4 
_rlnSchemeOperatorInput2 #5 
EXIT       exit  undefined  undefined  undefined
EXIT_maxtime exit_maxtime  undefined maxtime_hr  undefined 
      WAIT       wait  undefined   wait_sec  undefined 
 

# version 50001

data_scheme_jobs

loop_ 
_rlnSchemeJobNameOriginal #1 
_rlnSchemeJobName #2 
_rlnSchemeJobMode #3 
_rlnSchemeJobHasStarted #4 
importmovies importmovies   continue            0 
fs_motion_and_ctf fs_motion_and_ctf continue 0 
aligntilts aligntilts continue 0 

# version 50001

data_scheme_edges

loop_ 
_rlnSchemeEdgeInputNodeName #1 
_rlnSchemeEdgeOutputNodeName #2 
_rlnSchemeEdgeIsFork #3 
_rlnSchemeEdgeOutputNodeNameIfTrue #4 
_rlnSchemeEdgeBooleanVariable #5 
      WAIT EXIT_maxtime            0  undefined  undefined 
EXIT_maxtime importmovies            0  undefined  undefined 
importmovies fs_motion_and_ctf       0 undefined  undefined 
fs_motion_and_ctf aligntilts       0 undefined  undefine
aligntilts    EXIT                    0 undefined
