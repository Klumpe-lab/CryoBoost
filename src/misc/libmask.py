import numpy as np
import mrcfile
from src.misc.libimVol import gaussian_lowpass_mrc
from scipy.ndimage import distance_transform_edt
import subprocess
from skimage import filters

def ellipsoid_mask(box_size, radii, outer_radii=None, decay_width=5.0, voxel_size=1.0, output_path=None, dtype=np.float32):
    """
    Create ellipsoid mask with specific Gaussian decay width at edges and outer cutoff
    Parameters:
    box_size: tuple (nx, ny, nz) - size of volume in voxels
    radii: tuple (rx, ry, rz) - inner radii of ellipsoid in voxels
    outer_radii: tuple (rx, ry, rz) - outer radii where mask becomes zero (default: radii + 3*decay_width)
    decay_width: float - width of Gaussian decay in voxels
    voxel_size: float - voxel size in Angstroms
    """
    # Set default outer radii if not provided
    if outer_radii is None:
        outer_radii = tuple(r + 3*decay_width for r in radii)

    # Create coordinate grids
    x = np.linspace(-box_size/2, box_size/2, box_size)
    y = np.linspace(-box_size/2, box_size/2, box_size)
    z = np.linspace(-box_size/2, box_size/2, box_size)
    x, y, z = np.meshgrid(x, y, z)

    # Create inner and outer ellipsoid masks
    inner_ellipsoid = ((x/radii[0])**2 + (y/radii[1])**2 + (z/radii[2])**2)
    outer_ellipsoid = ((x/outer_radii[0])**2 + (y/outer_radii[1])**2 + (z/outer_radii[2])**2)

    # Create mask with smooth transition
    mask = np.ones_like(inner_ellipsoid, dtype=dtype)
    transition_region = (inner_ellipsoid > 1.0) & (outer_ellipsoid <= 1.0)
    
    # Calculate smooth transition in the region between inner and outer radii
    mask[transition_region] = 0.5 * (1.0 + np.cos(np.pi * 
        (np.sqrt(inner_ellipsoid[transition_region]) - 1.0) / 
        (np.sqrt(outer_ellipsoid[transition_region]) - 1.0)))
    
    # Set outer region to zero
    mask[outer_ellipsoid > 1.0] = 0.0

    # Write to MRC file
    if output_path is not None:
        with mrcfile.new(output_path, overwrite=True) as mrc:
            mrc.set_data(mask)
            mrc.voxel_size = voxel_size
       
        
    return mask

def genMaskRelion(inputVolume,outputMask=None,threshold=0.001,extend=3,softEdgeSize=6,lowpass=20,threads=20):
    
    program='relion_mask_create'
    inp=' --i ' + inputVolume
    outp=' --o ' + outputMask
    thr=' --ini_threshold ' + str(threshold)
    ext=' --extend_inimask ' + str(extend)
    soft=' --width_soft_edge ' + str(softEdgeSize)
    lowp=' --lowpass ' + str(lowpass)
    threads=' --j ' + str(threads)
    
    call=program + inp + outp
    call+=thr + ext + soft + lowp + threads 

    print(call)
    subprocess.run(call,shell=True)
    
def caclThreshold(inputVolume,lowpass=None):
    
    if isinstance(inputVolume, str):
        with mrcfile.open(inputVolume) as mrc:
            vol = mrc.data
            voxS=mrc.voxel_size.x
    if lowpass is not None:
        vol=gaussian_lowpass_mrc(vol,None,lowpass,voxel_size_angstrom=voxS)
    
    thresh_otsu = filters.threshold_otsu(vol)
    thresh_isodata = filters.threshold_isodata(vol)
    thresh_li = filters.threshold_li(vol)
    thresh_yen = filters.threshold_yen(vol)
    thresh_fb = np.mean(vol) + 1.85* np.std(vol)
    return {
        'otsu': thresh_otsu,
        'isodata': thresh_isodata,
        'li': thresh_li,
        'yen': thresh_yen,
        'fb' : thresh_fb
    }
    