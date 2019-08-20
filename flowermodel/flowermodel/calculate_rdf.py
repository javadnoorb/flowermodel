import pandas as pd
import numpy as np


class framerdf:
    def __init__(self, vid, blobs, image_idx, color1, color2, nbins=100):
        blob = blobs[blobs['frame'] == image_idx]
        self.X1 = blob.loc[blob['color'] == color1, ['x', 'y']].values
        self.X2 = blob.loc[blob['color'] == color2, ['x', 'y']].values


#         (self.L1, self.L2, _) = vid.get_data().shape
        
        self.get_blob_dists()
        self.get_cell_counts_for_rdf()
        
        self.rvals, self.rdf = self.calculate_rdf(nbins=nbins)
        

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

    def calculate_point_rdf(self, r1, r2):
        a = np.pi * (r2**2 - r1**2)
        rdf = ((r1 <= self.dist) & (self.dist < r2)).sum()/ self.N/ a
        return rdf
    
    
    def calculate_rdf(self, nbins=100):

        rvals = np.linspace(0, self.maxL, nbins)

        rdf = np.zeros_like(rvals)
        for idx in range(len(rvals)-1):
            rdf[idx] = self.calculate_point_rdf(rvals[idx], rvals[idx+1])

        rvals = rvals[:-1]
        rdf = rdf[:-1]

        return rvals, rdf