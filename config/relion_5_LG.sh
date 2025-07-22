#!/bin/bash


# Check if the script is being sourced or not
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "This script must be sourced. Run 'source ${BASH_SOURCE[0]}'"
    exit 1
fi

# Load the module environment
module use /software/extra/juraj/modules/all/

# Load the build environment
ml build-env/f2022

# Load the specific version of RELION
#ml relion/ja240319_5.0-beta2-a0b145a-foss-2022b
#ml relion/ja240429_5.0-beta3-ad0c1f2-foss-2022b
#ml relion/ja240523_5.0-beta2-6331fe6-foss-2022b
#ml relion/ja240527_5.0-beta2-6331fe6-foss-2022b
ml relion/ja241203_5.0-140fb8f-foss-2022b
ml pyqt5/5.15.7-gcccore-12.2.0

