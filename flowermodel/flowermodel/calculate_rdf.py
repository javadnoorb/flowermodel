# import pandas as pd
import numpy as np

def get_blob_dists(vid, blobs, image_idx, color1, color2):
    '''
    This function calculates pairwise distance between all blobs
    of 'color1' to blobs of 'color2' assuming periodic boundary
    conditions (only for one iteration).
    '''
    from scipy.spatial import distance_matrix

    blob = blobs[blobs['frame'] == image_idx]

    X1 = blob.loc[blob['color'] == color1, ['x', 'y']].values
    X2 = blob.loc[blob['color'] == color2, ['x', 'y']].values

    (L1, L2, _) = vid.get_data(0).shape
    dists = []
    for i in [0, -L1, L1]:
        for j in [0, -L2, L2]:
            X2shift = X2 + [i, j]
            dist = distance_matrix(X1, X2shift)
            dists.append(dist)
    dists = np.hstack(dists)
    return dists

def get_cell_counts_for_rdf(vid, dist):
    '''
    This function finds the number of cells for RDF calculation, 
    given the periodic boundary conditions, and the assumption that 
    pairs of cells further than minimum dimension of the image 
    should be ignored. Because of periodic boundary conditions 
    some cells (with 'color2') may never be used in the analysis and hence are
    not counted toward the total count.
    ''' 

    (L1, L2, _) = vid.get_data(0).shape

    if L1!=L2: 
        print('The images are not exactly squares. Using the minumum dimension for analysis')

    maxL = min(L1, L2)
    N = (dist <= maxL).sum()
    return N

def calculate_rdf(dist, r1, r2, N):
    rdf = ((r1 <= dist) & (dist < r2)).sum()/ N
    return rdf