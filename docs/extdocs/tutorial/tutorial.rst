=========
Tutorial
=========

Open CryoBoost
=================

.. code-block:: bash

   module load CRYOBOOST
   # or
   source /path/to/my/Folder/CryoBoost/.cbenv
   crboost_pipe.py -mov '/fs/pool/pool-bmapps/allSystem/appData/dataSets/copia/frames/*.eer' -m '/fs/pool/pool-bmapps/allSystem/appData/dataSets/copia/mdoc/*.mdoc' --proj testProj/copia --pixS 2.95
   #or without arguments
   crboost_pipe.py 

Adapt Parameters
=================

.. image:: img/setup.png

#. Click on Set Jobs to create the Job tabs.

#. Click on Auto to create a prefix.

#. Click on show cluster status to check which queue is free.

#. Choose queue and number of nodes.

#. Check the parameters of the jobs.

#. Move to the Start Relion tab.


Start WorkFlow
===============

.. image:: img/start.png

#. Click on Generate Project.

#. Click on Import Data.

#. Click on Start.


Add new data (from a new folder) to an existing project 
=======================================================

* If crboost_pipe.py was closed, open it again
   with the same project path and path to new frames and mdocs
   (here frames2 and mdoc2).
   
   .. code-block:: bash

      module load CRYOBOOST
      # or
      source /path/to/my/Folder/CryoBoost/.cbenv
      crboost_pipe.py --proj testProj/copia -mov '/fs/pool/pool-bmapps/allSystem/appData/dataSets/copia/frames2/*.eer' -m '/fs/pool/pool-bmapps/allSystem/appData/dataSets/copia/mdoc2/*.mdoc' --pixS 2.95
   
* If crboost_pipe.py is still running, move to Jobs and Set-Up and browse/adapt the path for the new frames and mdocs.
      
 frames: /fs/pool/pool-bmapps/allSystem/appData/dataSets/copia/frames2/*.eer
      
 mdoc: /fs/pool/pool-bmapps/allSystem/appData/dataSets/copia/mdoc2/*.mdoc


#. Move to Start Relion.

#. Click on Import Data.

#. Click on Start.