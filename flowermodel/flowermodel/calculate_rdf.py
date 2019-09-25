import pandas as pd
import numpy as np
from tqdm import tqdm

class __vidrdf__:
    def __init__(self, blobfile, vidfile, nbins=100, shellwidth=1):
        import imageio
        self.nbins = nbins
        self.shellwidth = shellwidth
        if type(blobfile) == str:
            self.blobs = pd.read_csv(blobfile)
        else:
            self.blobs = blobfile
        if type(vidfile) == str:
            self.vid = imageio.get_reader(vidfile,  'ffmpeg')
        else:
            self.vid = vidfile
        self.num_frames = self.vid.count_frames()
        (self.L1, self.L2, _) = self.vid.get_data(0).shape
        self.maxL = min(self.L1, self.L2)

class vidrdf(__vidrdf__):
    def __init__(self, data_path, moviefile, **kwargs):
        self.data_path = data_path
        self.moviefile = moviefile
        self.blobfile = '{:s}/blobs/{:s}.blob.csv'.format(data_path, moviefile)
        self.vidfile = '{:s}/movies/{:s}'.format(data_path, moviefile)

        super().__init__(self.blobfile, self.vidfile, **kwargs)
        self.vid_qc()

    def __get_rdf__(self, color1, color2):       
        rdfs = []
        for image_idx in tqdm(range(self.num_frames)):
            rdf = framerdf(self.blobs, self.vid, image_idx, color1, color2, nbins=self.nbins)
            rdfs.append(rdf.rdf)
        rvals = rdf.rvals
        return rvals, np.array(rdfs)

    def vid_qc(self):
        assert np.all(np.diff(np.array([self.vid.get_data(0).shape for n in range(self.num_frames)]), 
                      axis=0) == 0), 'Some video frames have a different size'
           
        if self.L1!=self.L2:
            print('The images are not exactly squares. Using the minumum dimension for analysis')

    def get_rdf(self, color1, color2, save_to_file=True):
        self.rdf_file = '{:s}/blobs/{:s}.blob.rdf.color_{:s}{:s}.csv'.format(self.data_path, self.moviefile, color1, color2)
        rvals, rdfs = self.__get_rdf__(color1, color2)
        rdfdf = pd.DataFrame(rdfs, columns=rvals)
        rdfdf.columns.name = 'r'
        rdfdf.index.name = 'frame index'

        if save_to_file:
            rdfdf.to_csv(self.rdf_file)
        return rdfdf

    def get_rdfs_for_all_colorpairs(self):
        blobcolors = self.blobs['color'].unique()

        for color1 in blobcolors:
            for color2 in blobcolors:
                rdfdf = self.get_rdf(color1, color2)

class framerdf(__vidrdf__):
    def __init__(self, blobfile, vidfile, image_idx, color1, color2, **kwargs):
        self.set_zeros_to_infinity = (color1==color2) # set zero distances to infinity to ignore self-distances
        super().__init__(blobfile, vidfile, **kwargs)
        blob = self.blobs[self.blobs['frame'] == image_idx]
        self.X1 = blob.loc[blob['color'] == color1, ['x', 'y']].values
        self.X2 = blob.loc[blob['color'] == color2, ['x', 'y']].values

        self.get_blob_dists()
        self.get_cell_counts_for_rdf()
        
        self.rvals, self.rdf = self.calculate_rdf()

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
        
        if self.set_zeros_to_infinity:
            self.dist[self.dist == 0] = np.inf

    def get_cell_counts_for_rdf(self):
        '''
        This function finds the number of cells for RDF calculation, 
        given the periodic boundary conditions, and the assumption that 
        pairs of cells further than minimum dimension of the image 
        should be ignored. Because of periodic boundary conditions 
        some cells (with 'color2') may never be used in the analysis and hence are
        not counted toward the total count.
        ''' 
        self.N = (self.dist <= self.maxL).sum()

    def calculate_point_rdf(self, r1, r2):
        a = np.pi * (r2**2 - r1**2)
        rdf = ((r1 <= self.dist) & (self.dist < r2)).sum()/ self.N/ a
        return rdf
    
    
    def calculate_rdf(self):
        rvals = np.linspace(0, self.maxL, self.nbins)

        rdf = np.zeros_like(rvals)
        for idx in range(len(rvals)-self.shellwidth):
            rdf[idx] = self.calculate_point_rdf(rvals[idx], rvals[idx+self.shellwidth])

        rvals = rvals[:-1]
        rdf = rdf[:-1]
        
        return rvals, rdf      


def get_maxrdf_locs(data_path):
    import pkg_resources
    import os
    import glob
    import re

    PACKAGE_DATA_PATH = pkg_resources.resource_filename('flowermodel', 'data/')
    clipmeta = pd.read_csv(os.path.join(PACKAGE_DATA_PATH, 'clip-metadata.txt'), sep='\t')
    rdffiles = glob.glob(os.path.join(data_path, 'blobs/*.color_*.csv'))
    rdffiles += glob.glob(os.path.join(data_path, 'blobs/*/*.color_*.csv'))
    rdffiles = pd.DataFrame(rdffiles, columns=['rdffile'])
    p = re.compile('(41586_2019_1429_MOESM\d_ESM.*)\.blob.rdf.color_(..)\.csv')
    rdffiles['movfile'] = rdffiles['rdffile'].map(lambda x: re.search(p, x)[1])
    rdffiles['color-pair'] = rdffiles['rdffile'].map(lambda x: re.search(p, x)[2])
    rdffiles = pd.merge(rdffiles, clipmeta, on='movfile', how='left')

    def get_maxrdf_loc(rdf_file):
        rdf = pd.read_csv(rdf_file, index_col=0)
        return float(rdf.mean().idxmax())

    rdffiles['maxrdf_loc'] = rdffiles['rdffile'].map(get_maxrdf_loc)
    return rdffiles