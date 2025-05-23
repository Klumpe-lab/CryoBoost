from src.rw.particleList import particleListMeta
import numpy as np
from scipy.spatial.transform import Rotation
import mrcfile

class neighbourMap:
    """
    Class for generating neighbour maps.

    Args:
      
    """

    def __init__(self,particleListName=None, outputMapName=None, boxsize=96, scaling=1.0,calc=True,recenterCoords=True):
        """
        Initializes the tiltSeriesMeta class.
        """
        self.particleListName = particleListName
        if outputMapName is None or outputMapName == 'default':
            print('No output map name provided, using default ' + particleListName.replace('.star', '_neighborMap.mrc') )
            self.outputMapName = particleListName.replace('.star', '_neighborMap.mrc')
        else:
            self.outputMapName = outputMapName
        self.boxsize = int(boxsize)
        self.scaling = scaling
        self.recenterCoords = recenterCoords
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
        tomos = partList.all_particle_df['rlnTomoName'].unique()
    
        cen = self.boxsize // 2
        d_cut = (self.boxsize - 1) // 2
        nplot = np.zeros((self.boxsize, self.boxsize, self.boxsize))
        
        # Process each tomogram
        for tomo in tomos:
            print(f'Processing tomogram {tomo}...')
            
            # Get coordinates and angles for this tomogram
            coords = partList.getImodCoords(tomo, [self.boxsize]*3)
            angles = partList.getAngles(tomo)
            pos = coords.T * self.scaling
            
            # Process each position
            for j in range(pos.shape[1]):
                dist = self.pairwise_dist(pos[:,j], pos)
                d_idx = dist <= d_cut
                temp_pos = pos[:,d_idx] - pos[:,j:j+1]
                rmat = self.euler2matrix(angles[j,0], angles[j,1], angles[j,2])
                rpos = np.round(rmat @ temp_pos).astype(int) + cen
                valid_idx = np.all((rpos >= 0) & (rpos < self.boxsize), axis=0)
                nplot[rpos[2,valid_idx], rpos[1,valid_idx], rpos[0,valid_idx]] += 1
                
        # Normalize central peak
        nplot = nplot / nplot[cen,cen,cen]
        nplot[cen,cen,cen] = 0
        nplot[cen,cen,cen] = np.max(nplot)
        
        # Write output
        print(f'Writing output to {self.outputMapName}')
        with mrcfile.new(self.outputMapName, overwrite=True) as mrc:
            mrc.set_data(nplot.astype(np.float32))