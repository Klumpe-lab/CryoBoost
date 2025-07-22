# Exchange these for container once Artem has figured it out
export targetFold=/users/sven.klumpe/software/python                            
source $targetFold/conda3/etc/profile.d/conda.sh
source /programs/sbgrid.shrc
#source /users/sven.klumpe/software/CryoBoost/.cbenv
#source /users/sven.klumpe/99_Testing/relion_5_LG.sh

source /groups/klumpe/software/Setup/CryoBoost/.cbenv
#source /groups/klumpe/software/Setup/CryoBoost/config/pytom_bash_wrapper.sh
#source /groups/klumpe/software/Setup/CryoBoost/config/linuxwarp_bash_wrapper.sh

conda activate cryoboost

export PATH="/groups/klumpe/software/cisTEM/bin/:$PATH"
