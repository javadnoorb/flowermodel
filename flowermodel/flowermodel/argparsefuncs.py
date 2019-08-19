import os
from flowermodel import util
from flowermodel.find_blobs import get_allframes_blobs
import imageio

def get_frame_blobs(args):
    outputdir = os.path.join(args.out_dir, os.path.basename(args.filename))
    util.mkdir_if_not_exist(outputdir)

    blobs = get_allframes_blobs(args.filename, min_idx=args.blob_index, max_idx=args.blob_index+1)
    blobs.to_csv(os.path.join(outputdir, 'blob{:d}.csv'.format(args.blob_index)), index=False)
    
    
def count_frames(args):
    vid = imageio.get_reader(args.filename,  'ffmpeg')
    print(vid.count_frames())
