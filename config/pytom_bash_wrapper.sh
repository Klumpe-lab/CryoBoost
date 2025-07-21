pytom_match_template.py() {
	    apptainer run --nv /groups/klumpe/software/PyTom_tm/PyTom_tm.sif pytom_match_template.py "$@"
    }
pytom_extract_candidates.py() {
	        apptainer run --nv /groups/klumpe/software/PyTom_tm/PyTom_tm.sif pytom_extract_candidates.py "$@"
	}
export -f pytom_match_template.py pytom_extract_candidates.py






#pytom_match_template.py() {
#	    apptainer run --nv /groups/klumpe/software/PyTom_tm/PyTom_tm.sif pytom_match_template.py "$@"
#    }
#    export -f pytom_match_template.py



