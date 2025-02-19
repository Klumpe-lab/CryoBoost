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

#. Set Invert Tiltangel and Invert Defocus Hand to No.

#. Alignment: Set sample thickness to 180nm

#. Alignment: Switch off tiltaxis refinement (only 1 tomo)

#. Move to ParticleSetup_copia tap.


Adapt Copia Particle Parameters
================================

.. image:: img/particleSetupCopia.png

#. Click on Generate(Volume) to create a template

#. Click on Use Basic shape to create a sphere as template

#. Enter 3x the diamter (of copia) 550:550:550 and OK

#. Click exit

#. Click Generate(Mask) to create a Mask

#. Enter 5 for Extend and SoftEdge (Relion Mask parameters) and OK

#. Enter 180 as angular increment and

#. Enter 550 as diamter for peak extraction (avoid mult. extraction)

#. Enter 224 cropped (used) box size in pixels

#. Enter 384 uncropped box size in pixels

#. Move to ParticleSetup_26S tap.

Adapt 26S Particle Parameters
==============================

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

#. Enter 12 to set Angular Increment

#. Enter 250 as diameter for peak extraction (half 26S diameter rod shape)

#. Enter 176 cropped (used) box size in pixels

#. Enter 224 uncropped box size in pixels

#. Move to Start Relion tap.



Start WorkFlow
===============

.. image:: img/start.png

#. Click on Generate Project.

#. Click on Import Data.

#. Click on Start.


Check Results
=============




Processing Copia
================

click on open Relion 

++++++++++++++++++++++
Reconstruct Particle
++++++++++++++++++++++

.. code-block:: bash
   
   Input Optimisation Set Extract/job20/optimisation_set.star
   
   Symmetry: I1
   Pre-read all particles into RAM: yes
   Box size: 384
   Cropped Box size: 224
   Submit to queue: yes
   
++++++++++++++++++++++
Class3d
++++++++++++++++++++++

.. code-block:: bash
   
   Input: Optimisation Set Extract/job20/optimisation_set.star
   RefereceMap: Reconstruct/job030/merged.mrc
   Inital Lowpass Filter (A): 45
   Symmetry: I1
   
   Pre-read all particles into RAM: yes
   Box size: 384
   Cropped Box size: 224
   Submit to queue: yes



++++++++++++++
Mask creation
++++++++++++++

.. code-block:: bash
   
   #Remove unstructured inner part
   cd myProjct
   module load EMAN
   e2proc3d.py InitialModel/job024/initial_model.mrc  InitialModel/job024/initial_model4Mask.mrc --process=mask.sharp:inner_radius=65 (73)
   Input 3d Map: InitialModel/job024/initial_model4Mask.mrc 
   Lowpass: 18
   Inital binarisation threshold: 0.1
   Extend binary Map this many pixels: 4 (5)
   Add soft-edge of this many pixels: 7
   

+++++++++
Refine3d
+++++++++

.. code-block:: bash
   
   Input Optimisation Set Extract/job020/optimisation_set.star
   Reference Map: InitialModel/job024/initial_model.mrc 
   Reference Mask: MaskCreate/job025/mask.mrc 
   Initial Lowpass Filter: 40
   Symmetry: I1
   Use Flattern Solvent CTF: yes
   Use Blush Regularisation: yes
   Pre-read all particles into RAM: yes
   Use GPU acceleration: yes
   Submit to queue: yes
   

++++++++++++++
Reconstruct
++++++++++++++

.. code-block:: bash
   
   Tau Fudge == 1   


++++++++++++++++++
PostProcessing
++++++++++++++++++

.. code-block:: bash
   
   Tau Fudge == 1   


+++++++++++++++++
Bayesian Polish
+++++++++++++++++

.. code-block:: bash
   
   Tau Fudge == 1   

+++++++++++++++
Extract 
+++++++++++++++

.. code-block:: bash
   
   Tau Fudge == 1   

++++++++++++++++
PostProcessing
++++++++++++++++

.. code-block:: bash
   
   Tau Fudge == 1   

+++++++++++++++
CTF Refinement
+++++++++++++++

.. code-block:: bash
   
   Tau Fudge == 1   

+++++++++++++++
Extract 
+++++++++++++++

.. code-block:: bash
   
   Tau Fudge == 1   


++++++++++++++++++
Reconstruct
++++++++++++++++++

.. code-block:: bash
   
   Tau Fudge == 1   

++++++++++++++++
PostProcessing
++++++++++++++++

.. code-block:: bash
   
   Tau Fudge == 1   


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