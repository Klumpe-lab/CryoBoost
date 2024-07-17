=========
Tutorial
=========

Requiremets
=================

* check if you can login to the submission node without password

.. code-block:: bash
   
   ssh hpcl8001

* no other version of Relion is in your .bashrc


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

#. Click on Set Jobs to create the Job taps

#. Click on Auto to create a prefix

#. Click on show cluster status to check which queue is free

#. Choose queue and number of nodes

#. Check the parameters of the jobs

#. Click on start relion job tap


Start WorkFlow
=================

.. image:: img/start.png

#. Click on Generate Project

#. Click on Import Data

#. Click on Start 

