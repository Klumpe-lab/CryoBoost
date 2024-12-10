import numpy as np
import mrcfile
from scipy.ndimage import distance_transform_edt

def ellipsoid_mask(box_size, radii, decay_width=5.0, voxel_size=1.0,output_path=None):
    """
    Create ellipsoid mask with specific Gaussian decay width at edges
    
    Parameters:
    box_size: tuple (nx, ny, nz) - size of volume in voxels
    radii: tuple (rx, ry, rz) - radii of ellipsoid in voxels
    decay_width: float - width of Gaussian decay in voxels
    voxel_size: float - voxel size in Angstroms
    """
    # Create coordinate grids
    x = np.linspace(-box_size[0]/2, box_size[0]/2, box_size[0])
    y = np.linspace(-box_size[1]/2, box_size[1]/2, box_size[1])
    z = np.linspace(-box_size[2]/2, box_size[2]/2, box_size[2])
    
    x, y, z = np.meshgrid(x, y, z)
    
    # Create binary ellipsoid mask
    binary_mask = ((x/radii[0])**2 + (y/radii[1])**2 + (z/radii[2])**2) <= 1.0
    binary_mask = binary_mask.astype(np.float32)
    
    # Calculate distance from mask edge
    distance_inside = distance_transform_edt(binary_mask)
    distance_outside = distance_transform_edt(1.0 - binary_mask)
    
    # Combine distances
    distance = distance_outside - distance_inside
    
    # Create smooth transition using error function
    smooth_mask = 0.5 * (1.0 - np.tanh(distance / decay_width))
    
    # Write to MRC file
    if output_path is not None:
        with mrcfile.new(output_path, overwrite=True) as mrc:
            mrc.set_data(smooth_mask)
            mrc.voxel_size = voxel_size
    
        
    return smooth_mask

