from astropy import units as u                                                                                                             
from astropy.nddata import CCDData                                                                                                         
from astropy.io import fits
#from astropy.stats import sigma_clip
import ccdproc
from ccdproc import Combiner        
import numpy as np
#import numpy.ma as ma
import matplotlib.pyplot as plt
import glob
plt.style.use("dark_background")
plt.rcParams['figure.figsize'] = [14, 7]

def print_err(err_msg):
    print(f"\033[31mERROR\033[0m: {err_msg}")
    exit(1)

def trim_fits(arr):
    shape = arr.shape
    ccd = CCDData(arr, unit=u.adu)
    ccd = ccdproc.trim_image(ccd[:shape[0]-17, :]) #34
    ccd = ccdproc.trim_image(ccd[:, 12:]) #24
    return ccd

def bin_image(arr, block_size):
    return ccdproc.block_average(arr, block_size=block_size)

def create_bias(file_path: str, out_name: str, overwrite=True) -> None:
    header_red = False
    data = []
    files = glob.glob(file_path)
    for file in files:
        if header_red == False:
            header = fits.getheader(file)
            header_red == True
        ccd = CCDData(fits.getdata(file), unit=u.adu)
        data.append(ccd)
    combiner = Combiner(data)
    combined_median = combiner.median_combine()
    fits.writeto(out_name, combined_median, header, overwrite=overwrite)

def create_dark(file_path, out_name, bias_path=None, overwrite=True):
    header_red = False
    if bias_path is not None:
        bias = CCDData(fits.getdata(bias_path), unit=u.adu)
        
    data = []
    files = glob.glob(file_path)
    for file in files:
        if header_red == False:
            header = fits.getheader(file)
        ccd = CCDData(fits.getdata(file), unit=u.adu)
        data.append(ccd)
    
    combiner = Combiner(data)
    combined_median = combiner.median_combine()
    
    if bias_path is not None:
        result = combined_median.subtract(bias)
        fits.writeto(out_name, result, header, overwrite=overwrite)
    else:
        fits.writeto(out_name, combined_median, header, overwrite=overwrite)

def create_flat(file_path, out_name, bias_path=None, dark_path=None, overwrite=True):
    header_red = False
    bd_remove = False
    if bias_path is not None and dark_path is not None:
        bd_remove = True
        bias_data = fits.getdata(bias_path) 
        dark_data = fits.getdata(dark_path)
        bias_max = np.max(bias_data)
        dark_max = np.max(dark_data)
        dark = CCDData(bias_data, unit=u.adu)
        bias = CCDData(dark_data, unit=u.adu)
    elif bias_path is not None or dark_path is not None:
        print("Error: provide bias and dark images or none")
        exit(1)
        
    data = []
    files = glob.glob(file_path)
    for file in files:
        fits_file = fits.getdata(file)
        if header_red == False:
            header = fits.getheader(file, 0)
            header_red = True
        flat_av = np.mean(fits_file)
        ccd = CCDData(fits_file, unit=u.adu)
        if bd_remove == True:
            ccd = ccd.subtract(bias)
            ccd = ccd.subtract(dark)
        ccd = ccd.divide(flat_av)
        data.append(ccd)
    
    combiner = Combiner(data)
    combined_median = combiner.median_combine()
    fits.writeto(out_name, combined_median, header, overwrite=overwrite)

def remove_hot_pix(arr, hot_pix_file):
    x, y = [], []
    with open(hot_pix_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            text = line.split()
            x.append(int(text[0]))
            y.append(int(text[1]))

    for i, j in zip(x, y):
        med = np.median(arr[i-1:i+2, j-1:j+2])
        arr[i, j] = med
    return arr
    
def create_reduced_image(image, bias, dark, flat, out_name, hot_pix_file, exposure_key, bin_size=1, flat_corr_min_val=0.001):
    """
    Function does image reduction and trimming.
    image, bias, dark, flat - paths to images
    """
    im = CCDData.read(image, unit=u.adu)
    bs = CCDData.read(bias, unit=u.adu)
    dk = CCDData.read(dark, unit=u.adu)
    ft = CCDData.read(flat, unit=u.adu)
    
    im = trim_fits(im)
    bs = trim_fits(bs)
    dk = trim_fits(dk)
    ft = trim_fits(ft)
    bias_subtracted = ccdproc.subtract_bias(im, bs)
    dark_subtracted = ccdproc.subtract_dark(bias_subtracted, dk, exposure_time=exposure_key, exposure_unit=u.second, scale=False)
    flat_corr = ccdproc.flat_correct(dark_subtracted, ft, min_value=flat_corr_min_val)
    header = flat_corr.header
    fits.writeto(out_name, flat_corr, header, overwrite=True)
    reduced = fits.getdata(out_name)
    
    reduced = remove_hot_pix(reduced, hot_pix_file)
    reduced = np.clip(reduced, 0, 65535)
    if bin_size > 1:
        reduced = bin_image(reduced, bin_size)
        header["XBINNING"] = bin_size
        header["YBINNING"] = bin_size
    reduced = reduced.astype(np.uint16)
    fits.writeto(out_name, reduced, header, overwrite=True)


if __name__ == "__main__":
    dr = "/home/fischwagen/prg/astronomy/BDF/"
    create_bias("/home/fischwagen/prg/astronomy/BDF/BIAS*.FIT", "mbias.fit")

