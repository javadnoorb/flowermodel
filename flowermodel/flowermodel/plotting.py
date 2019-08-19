import matplotlib.pyplot as plt
import flowermodel.find_blobs as fb
import pandas as pd

def plot_blob_overlay(vid, img_idx, blobs):
    img = fb.get_image(vid, img_idx)

    _, ax = plt.subplots(1, 1, figsize=(8,8))
    ax.imshow(img)

    def draw_circle(row, ax):
        c = plt.Circle((row['y'], row['x']), row['radius'], color=row['color'], linewidth=2, fill=False);
        ax.add_patch(c);

    blobs[blobs['frame'] == img_idx].apply(lambda row: draw_circle(row, ax), axis=1);
