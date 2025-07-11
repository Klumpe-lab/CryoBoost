import os
import numpy as np
from src.rw.particleList import particleListMeta
from scipy.spatial.transform import Rotation
import mrcfile

class neighbourMap:
    """
    Class for generating neighbour maps.

    Args:
      
    """

    def __init__(self,particleListName=None, outputMapName=None,tomoCoordPixs=None,boxsize=96, pixs=3.0,calc=True,recenterCoords=True,particleListName2=None,tomoSize="4096,4096,2048"):
        """
        Initializes the tiltSeriesMeta class.
        """
        self.particleListName = particleListName
        self.particleListName2 = particleListName2
        
        if outputMapName is None or outputMapName == 'default':
            print('No output map name provided, using default ' + particleListName.replace('.star', '_neighborMap.mrc') )
            self.outputMapName = particleListName.replace('.star', '_neighborMap.mrc')
        else:
            self.outputMapName = outputMapName
        self.tomoCoordPixs = tomoCoordPixs
        self.boxsize = int(boxsize)
        self.pixs = pixs
        self.recenterCoords = recenterCoords
        self.tomoSize = np.array([int(x) for x in tomoSize.split(',')], dtype=float);
        
        if calc:
            self.calc()
          
    def euler2matrix(self,rot, tilt, psi):
        """Convert Euler angles to rotation matrix."""
        rot = Rotation.from_euler('zyz', [-rot, -tilt, -psi], degrees=True)
        return np.linalg.inv(rot.as_matrix())
    
    def pairwise_dist(self,pos1, pos2):
        """Calculate pairwise Euclidean distances."""
        return np.sqrt(np.sum((pos1.reshape(-1,1) - pos2)**2, axis=0))
   
    
    def calc(self):
        """
        Generate a neighbor plot for a particle list.
        
        Args:
            motl_name (str): Input particle list star file
            output_root (str): Output MRC file name
            boxsize (int): Size of the output volume
            scaling (float): Scaling factor for coordinates
        """
    
        partList = particleListMeta(self.particleListName)
        if self.particleListName2 is not None:
            partList2 = particleListMeta(self.particleListName2)
        else:
            partList2 = None
           
        tomos = partList.all_particle_df['rlnTomoName'].unique()
        if self.recenterCoords:
            print('Re-centering coordinates...')
            partList.centerCoords(self.tomoCoordPixs)    
            if partList2 is not None:
                partList2.centerCoords(self.tomoCoordPixs)
        cen = self.boxsize // 2
        d_cut = (self.boxsize - 1) // 2
        nplot = np.zeros((self.boxsize, self.boxsize, self.boxsize))
        if partList2 is not None:
            nplot2 = np.zeros((self.boxsize, self.boxsize, self.boxsize))
        
        scaling =float(self.tomoCoordPixs) / float(self.pixs)
        print(f'Scaling factor for coordinates: {scaling}')
        
        # Process each tomogram
        for tomo in tomos:
         
            # Get coordinates and angles for this tomogram
            coords = partList.getImodCoords(tomo,self.tomoSize)
            angles = partList.getAngles(tomo)
            pos = coords.T * float(scaling)
            
            if partList2 is not None:
                coords2 = partList2.getImodCoords(tomo)
                angles2 = partList2.getAngles(tomo)
                pos2 = coords2.T * float(scaling)
            
            # Process each position
            for j in range(pos.shape[1]):
                dist = self.pairwise_dist(pos[:,j], pos)
                d_idx = dist <= d_cut
                temp_pos = pos[:,d_idx] - pos[:,j:j+1]
                rmat = self.euler2matrix(angles[j,0], angles[j,1], angles[j,2])
                rpos = np.round(rmat @ temp_pos).astype(int) + cen
                valid_idx = np.all((rpos >= 0) & (rpos < self.boxsize), axis=0)
                nplot[rpos[2,valid_idx], rpos[1,valid_idx], rpos[0,valid_idx]] += 1
                if partList2 is not None:
                    dist2 = self.pairwise_dist(pos[:,j], pos2)
                    d_idx2 = dist2 <= d_cut
                    temp_pos2 = pos2[:,d_idx2] - pos[:,j:j+1]
                    rmat2 = self.euler2matrix(angles[j,0], angles[j,1], angles[j,2])
                    rpos2 = np.round(rmat2 @ temp_pos2).astype(int) + cen
                    valid_idx2 = np.all((rpos2 >= 0) & (rpos2 < self.boxsize), axis=0)
                    nplot2[rpos2[2,valid_idx2], rpos2[1,valid_idx2], rpos2[0,valid_idx2]] += 1
                
        
                
        # Normalize central peak
        nplot = nplot / nplot[cen,cen,cen]
        nplot[cen,cen,cen] = 0
        nplot[cen,cen,cen] = np.max(nplot)
        if partList2 is not None:
            nplot2 = nplot2 / nplot[cen,cen,cen]
               
        
        # Write output
        print(f'Writing output to {self.outputMapName}')
        with mrcfile.new(self.outputMapName, overwrite=True) as mrc:
            mrc.set_data(nplot.astype(np.float32))
            mrc.voxel_size = self.pixs
        if partList2 is not None:
            root, ext = os.path.splitext(self.outputMapName)
            outputmap2Name = root+ '_2' + ext 
            print(f'Writing output to {outputmap2Name}')
            with mrcfile.new(outputmap2Name, overwrite=True) as mrc2:
                mrc2.set_data(nplot2.astype(np.float32))
                mrc2.voxel_size = self.pixs    