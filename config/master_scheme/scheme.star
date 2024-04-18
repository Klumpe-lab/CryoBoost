
# version 30001

data_scheme_general

_rlnSchemeName                       Schemes/master_scheme/
_rlnSchemeCurrentNodeName            reconstruction
 

# version 30001

data_scheme_floats

loop_ 
_rlnSchemeFloatVariableName #1 
_rlnSchemeFloatVariableValue #2 
_rlnSchemeFloatVariableResetValue #3 
do_at_most   500.000000   500.000000 
maxtime_hr    48.000000    48.000000 
  wait_sec   180.000000   180.000000 
 

# version 30001

data_scheme_operators

loop_ 
_rlnSchemeOperatorName #1 
_rlnSchemeOperatorType #2 
_rlnSchemeOperatorOutput #3 
_rlnSchemeOperatorInput1 #4 
_rlnSchemeOperatorInput2 #5 
EXIT_maxtime exit_maxtime  undefined maxtime_hr  undefined 
      WAIT       wait  undefined   wait_sec  undefined 
 

# version 30001

data_scheme_jobs

loop_ 
_rlnSchemeJobNameOriginal #1 
_rlnSchemeJobName #2 
_rlnSchemeJobMode #3 
_rlnSchemeJobHasStarted #4 
aligntilts AlignTiltSeries/job109/   continue            1 
ctffind CtfFind/job107/   continue            1 
exclude_rule_based External/job108/   continue            1
feature_analysis  External/   continue    1
importmovies ImportTomo/job105/   continue            1 
motioncorr MotionCorr/job106/   continue            1 
reconstruction ReconstructTomograms/job110/   continue            1
 

# version 30001

data_scheme_edges

loop_ 
_rlnSchemeEdgeInputNodeName #1 
_rlnSchemeEdgeOutputNodeName #2 
_rlnSchemeEdgeIsFork #3 
_rlnSchemeEdgeOutputNodeNameIfTrue #4 
_rlnSchemeEdgeBooleanVariable #5 
      WAIT EXIT_maxtime            0  undefined  undefined 
EXIT_maxtime importmovies            0  undefined  undefined 
importmovies motioncorr            0  undefined  undefined 
motioncorr    ctffind            0  undefined  undefined 
ctffind     feature_analysis             0  undefined  undefined
feature_analysis     exclude_rule_based             0  undefined  undefined
exclude_rule_based  aligntilts            0  undefined  undefined  
aligntilts reconstruction            0  undefined  undefined 
reconstruction       WAIT            0  undefined  undefined 
 
