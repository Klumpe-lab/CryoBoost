import numpy as np
from scipy import fftpack
import mrcfile

def gaussian_lowpass_mrc(input_mrc: str, output_mrc: str, cutoff_angstrom: float, 
                        voxel_size_angstrom: float = None,invert_contrast: bool = False,hard_cutoff_angstrom: float = None):
    """
    Apply Gaussian low-pass filter to MRC file
    
    Args:
        input_mrc (str): Path to input MRC file
        output_mrc (str): Path to output filtered MRC file
        cutoff_angstrom (float): Cutoff frequency in Ångströms (Å)
        voxel_size_angstrom (float, optional): Override voxel size in Ångströms. 
                                              If None, uses value from input MRC
    """
    
    # Read input MRC
    with mrcfile.open(input_mrc, permissive=True) as mrc:
        volume = mrc.data.copy()
        # Use provided voxel size or get from file
        voxel_size = voxel_size_angstrom if voxel_size_angstrom is not None else mrc.voxel_size.x
        
    # Calculate filter parameters in Ångströms
    nx, ny, nz = volume.shape
    kx = fftpack.fftfreq(nx, d=voxel_size)  # spatial frequencies in 1/Å
    ky = fftpack.fftfreq(ny, d=voxel_size)
    kz = fftpack.fftfreq(nz, d=voxel_size)
    
    kx_grid, ky_grid, kz_grid = np.meshgrid(kx, ky, kz, indexing='ij')
    k_squared = kx_grid**2 + ky_grid**2 + kz_grid**2
    k_magnitude = np.sqrt(k_squared)
    # Convert cutoff to sigma in Fourier space (1/Å)
    sigma = cutoff_angstrom / (2 * np.pi)
    gaussian_filter = np.exp(-k_squared * (2 * np.pi**2) * sigma**2)
    
     # Apply hard cutoff if specified
    if hard_cutoff_angstrom is not None:
        hard_cutoff_freq = 1.0 / hard_cutoff_angstrom
        hard_mask = k_magnitude <= hard_cutoff_freq
        gaussian_filter = gaussian_filter * hard_mask
    
    
    vol_fft = fftpack.fftn(volume)
    filtered_fft = vol_fft * gaussian_filter
    filtered_vol = np.real(fftpack.ifftn(filtered_fft))
    
    # Normalize filtered volume
    filtered_vol = filtered_vol - np.mean(filtered_vol)
    filtered_vol = filtered_vol / np.std(filtered_vol)
    
    # Invert contrast if requested
    if invert_contrast:
        filtered_vol = -filtered_vol
    
    
    # Write output MRC
    with mrcfile.new(output_mrc, overwrite=True) as mrc:
        mrc.set_data(filtered_vol.astype(np.float32))
        mrc.voxel_size = voxel_size