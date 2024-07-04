=========
Setup
=========

install Miniconda
=================
.. code-block:: bash

   targetFolder=/path/to/my/installationFolder
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   ./Miniconda3-latest-Linux-x86_64.sh -b -p $targetFold/conda3
   export PATH=$targetFold/conda3/bin/:$PATH
   source $targetFold/conda3/etc/profile.d/conda.sh 

Install dependencies
====================
.. code-block:: bash
   
   conda create -n cryoboost python=3.11.5
   conda activate cryoboost
   conda install nvidia/label/cuda-11.8.0::cuda-toolkit
   pip3 install torch==2.2.1  torchvision==0.17.1 torchaudio==2.2.1 --index-url https://download.pytorch.org/whl/cu118
   conda install -c fastai fastai==2.7.14
   pip3 install --ignore-installed torch==2.2.1 torchvision==0.17.1 torchaudio==2.2.1 --index-url https://download.pytorch.org/whl/cu118 --no-cache-dir
   pip3 install pyqt6
   conda install conda-forge::timm
   conda install seaborn mrcfile 
   conda install anaconda::scikit-learn
   conda install anaconda::scikit-image
   #for local documentation use
   conda install sphinx sphinx_rtd_theme

Install cryoboost
====================
.. code-block:: bash
   
   cd /path/to/my/installationFolder/
   git clone https://github.com/FlorianBeckOle/CryoBoost.git
   cd cryoboost
   #adapt shebang wrapper for python iterperte needd
    

Test torch installation
====================
.. code-block:: bash
   
   python -c 'import torch; print(torch.cuda.is_available())'

Test fastai installation
====================
.. code-block:: bash
   
   python -c 'import fastai; print(fastai.__version__)'


generate documentation
======================
.. code-block:: bash
   
   cd /path/to/my/installationFolder/cryoboost
   cd docs
   make html
   
   
