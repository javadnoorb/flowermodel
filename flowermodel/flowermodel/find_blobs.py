from skimage.restoration import inpaint_biharmonic#, denoise_wavelet
# import matplotlib.pyplot as plt
import imageio
from skimage.filters import threshold_otsu
import numpy as np
# from skimage.morphology import disk, square
# from skimage.filters import rank
# from skimage.util import img_as_ubyte
# from skimage.exposure import equalize_hist, equalize_adapthist
from skimage.feature import blob_dog, blob_log, blob_doh
import pandas as pd
from tqdm import tqdm

def remove_text(img):
    th = threshold_otsu(img[:, :, 2])
    mask = img[:, :, 2] > th
    newimg = img.copy()
    newimg[:, :, 2] = 0
    newimg = inpaint_biharmonic(newimg, mask, multichannel=True)
    return newimg

def get_image(vid, img_idx):
    img = vid.get_data(img_idx)
    img = remove_text(img)
    # img = img[35:-42, :, :] # remove annotations on the image
    return img

def get_blobs(imgray, min_sigma=3, max_sigma=10, num_sigma=10, threshold=.1, opening_disk_radius = 5):
#     imgray_opened = opening((imgray * 256).astype(int), disk(opening_disk_radius))/256     
    # blobs_dog = blob_dog(image_gray, max_sigma=30, threshold=.1)
    # blobs_doh = blob_doh(image_gray, max_sigma=30, threshold=.01)
    blobs = blob_log(imgray, max_sigma=max_sigma, min_sigma=min_sigma, num_sigma=num_sigma, threshold=threshold)
    blobs = pd.DataFrame(blobs, columns=['x', 'y', 'radius'])
    blobs['radius'] *= np.sqrt(2)
    return blobs

def plot_blobs(blobs, ax, color='r'):
    for y, x, r in blobs:
        c = plt.Circle((x, y), r, color=color, linewidth=2, fill=False)
        ax.add_patch(c)
#         ax.set_axis_off()


def get_frame_blobs(img, min_sigma=10, max_sigma=15, num_sigma=10, threshold=.1):    
    blobs_r = get_blobs(img[:, :, 0], max_sigma=max_sigma, min_sigma=min_sigma, num_sigma=num_sigma, threshold=threshold)
    blobs_g = get_blobs(img[:, :, 1], max_sigma=max_sigma, min_sigma=min_sigma, num_sigma=num_sigma, threshold=threshold)   

    blobs_r['color'] = 'r'
    blobs_g['color'] = 'g'

    blobs = pd.concat([blobs_r, blobs_g])
    blobs.reset_index(drop=True, inplace=True)
    blobs[['x', 'y']] = blobs[['x', 'y']].astype(int)
    return blobs

def get_allframes_blobs(filename, min_idx=0, max_idx=None, min_sigma=10, max_sigma=15, num_sigma=10, threshold=.1):
    vid = imageio.get_reader(filename,  'ffmpeg')
    allblobs = None
    if max_idx is None:
        max_idx = vid.count_frames()
    for img_idx in tqdm(range(min_idx, max_idx)):
        img = get_image(vid, img_idx)
        blobs = get_frame_blobs(img, min_sigma=min_sigma, max_sigma=max_sigma, num_sigma=num_sigma, threshold=threshold)
        blobs['frame'] = img_idx
        allblobs = pd.concat([allblobs, blobs])

    allblobs.reset_index(drop=True, inplace=True)
    return allblobs