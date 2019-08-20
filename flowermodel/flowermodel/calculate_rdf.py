import pandas as pd
import numpy as np


class blobrdf:
    def __init__(self, vid, blobs, image_idx, color1, color2):
        print('get blob')
        blob = blobs[blobs['frame'] == image_idx]
        print('get X1, X2')
        self.X1 = blob.loc[blob['color'] == color1, ['x', 'y']].values
        self.X2 = blob.loc[blob['color'] == color2, ['x', 'y']].values

#         self.vid_qc(vid)
        print('get L1, L2')
        (self.L1, self.L2, _) = vid.get_data(0).shape
        if self.L1!=self.L2: 
            print('The images are not exactly squares. Using the minumum dimension for analysis')
        
        print('get dist')
        self.get_blob_dists()
        print('get cell count ')
        self.get_cell_counts_for_rdf()
        
    def vid_qc(self, vid):
        assert np.all(np.diff(np.array([vid.get_data(0).shape for n in range(vid.count_frames())]), 
                      axis=0) == 0), 'Some video frames have a different size'

    def get_blob_dists(self):
        '''
        This function calculates pairwise distance between all blobs
        of 'color1' to blobs of 'color2' assuming periodic boundary
        conditions (only for one iteration).
        '''
        from scipy.spatial import distance_matrix

        dists = []
        for i in [0, -self.L1, self.L1]:
            for j in [0, -self.L2, self.L2]:
                X2shift = self.X2 + [i, j]
                dist = distance_matrix(self.X1, X2shift)
                dists.append(dist)
        self.dist = np.hstack(dists)

    def get_cell_counts_for_rdf(self):
        '''
        This function finds the number of cells for RDF calculation, 
        given the periodic boundary conditions, and the assumption that 
        pairs of cells further than minimum dimension of the image 
        should be ignored. Because of periodic boundary conditions 
        some cells (with 'color2') may never be used in the analysis and hence are
        not counted toward the total count.
        ''' 

        self.maxL = min(self.L1, self.L2)
        self.N = (self.dist <= self.maxL).sum()

    def calculate_rdf(self, r1, r2):
        rdf = ((r1 <= self.dist) & (self.dist < r2)).sum()/ self.N
        return rdf