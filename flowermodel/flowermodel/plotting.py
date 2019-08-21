import matplotlib.pyplot as plt
import flowermodel.find_blobs as fb
import pandas as pd
import seaborn as sns
import numpy as np

def plot_blob_overlay(vid, img_idx, blobs):
    img = fb.get_image(vid, img_idx)

    _, ax = plt.subplots(1, 1, figsize=(8,8))
    ax.imshow(img)

    def draw_circle(row, ax):
        c = plt.Circle((row['y'], row['x']), row['radius'], color=row['color'], linewidth=2, fill=False);
        ax.add_patch(c);

    blobs[blobs['frame'] == img_idx].apply(lambda row: draw_circle(row, ax), axis=1);

def plot_rdf_heatmap(rdf_file):
    rdfdf = pd.read_csv(rdf_file, index_col=0)
    rdfdf.columns.name = 'r'
    tmp = rdfdf.copy()
    # tmp = tmp.applymap(lambda x: '%.2e' % x)
    tmp.columns = (np.round(tmp.columns.astype(float))).astype(int)
    plt.figure(figsize=(23, 12))
    sns.heatmap(tmp)
    
def plot_rdfs(rdf_file):
    rdfdf = pd.read_csv(rdf_file, index_col=0)
    rdfdf.columns.name = 'r'

    plt.figure(figsize=(23, 3))
    plt.plot(rdfdf.columns.astype(float).tolist(), rdfdf.values.T);
    plt.xlabel('r');
    plt.ylabel('RDF');
    