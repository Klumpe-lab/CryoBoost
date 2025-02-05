=========
Tutorial
=========

Open CryoBoost
=================

.. code-block:: bash

   module load CRYOBOOST
   # or
   source /path/to/my/Folder/CryoBoost/.cbenv
   crboost_pipe.py -mov '/fs/pool/pool-bmapps/allSystem/appData/dataSets/copia/frames//Position_1*.eer' -m '/fs/pool/pool-bmapps/allSystem/appData/dataSets/copia/mdoc//Position_1*.mdoc' --proj testProj/copia26S --scheme "warp_tomo_prep" --species "copia,26S"
   
   #or without arguments
   crboost_pipe.py 

Adapt Tomogram Parameters
======================

.. image:: img/setup.png

#. Click on Set Jobs to create the Job tabs.

#. Click on Auto to create a prefix.

#. Set sample thickness to 180nm

#. Switch off tiltaxis refinement (only 1 tomo)

#. Move to ParticleSetup_copia tap.

Adapt Copia Particle Parameters
======================

.. image:: img/particleSetupCopia.png

#. Click on Generate(Volume) to create a template

#. Click on Use Basic shape to create a sphere as template

#. Enter 3x the diamter (of copia) 550:550:550 and OK

#. Click exit

#. Click Generate(Mask) to create a Mask

#. Enter 5 for Extend and SoftEdge (Relion Mask parameters) and OK

#. Enter 550 as diamter for peak extraction (avoid mult. extraction)

#. Enter 224 cropped (used) box size in pixels

#. Enter 384 uncropped box size in pixels

#. Move to ParticleSetup_26S tap.

Adapt 26S Particle Parameters
======================

.. image:: img/particleSetup26S.png

#. Click on Generate(Volume) to create a template

#. Click on Fetch Pdb to download pdb from pdb www.rcsb.org

#. Enter 5GJR and click OK

#. Click Sim from Pdb to simulate em density from pdb with cistem's simulate

#. Click Gen And Exit to start the simulation

#. Click Exit

#. Click Generate(Mask) to create a Mask

#. Enter 5 for Extend  (Relion Mask parameters) 

#. Enter 6 for SoftEdge (Relion Mask parameters) and OK

#. Enter 250 as diamter for peak extraction (half 26S diameter rod shape)

#. Enter 176 cropped (used) box size in pixels

#. Enter 224 uncropped box size in pixels

#. Move to Start Relion tap.



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