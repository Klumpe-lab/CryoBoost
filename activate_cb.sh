# Exchange these for container once Artem has figured it out
export targetFold=/users/sven.klumpe/software/python                            
source $targetFold/conda3/etc/profile.d/conda.sh
source /programs/sbgrid.shrc
#source /users/sven.klumpe/software/CryoBoost/.cbenv
source /groups/klumpe/software/Setup/CryoBoost/.cbenv

conda activate cryoboost

export PATH="/groups/klumpe/software/cisTEM/bin/:$PATH"
