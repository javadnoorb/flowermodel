import os
from flowermodel import util
from flowermodel.find_blobs import get_allframes_blobs
import imageio
import glob
import pandas as pd


def get_frame_blobs(args):
    outputdir = os.path.join(args.out_dir, )
    util.mkdir_if_not_exist(outputdir)

    blobs = get_allframes_blobs(args.filename, min_idx=args.frame_index, max_idx=args.frame_index+1)
    blobs.to_csv(os.path.join(outputdir, '{:s}.blob{:d}.csv'.format(os.path.basename(args.filename), args.frame_index)), index=False)

def count_frames(args):
    vid = imageio.get_reader(args.filename,  'ffmpeg')
    print(vid.count_frames())

def create_pbs(args):
    vid = imageio.get_reader(args.filename,  'ffmpeg')
    last_frame_index = vid.count_frames() - 1

    pbs_text = '''#!/bin/bash
#PBS -l nodes=1:ppn={num_cores}
#PBS -l walltime={walltime}
#PBS -l mem=4GB
#PBS -q batch
#PBS -N {jobname}
#PBS -t 0-{last_frame_index}
#PBS -o {pbslogs}/$PBS_JOBNAME.o
#PBS -e {pbslogs}/$PBS_JOBNAME.e

cd $PBS_O_WORKDIR
FILE="{moviefile}"
. /projects/chuang-lab/jnh/miniconda3/etc/profile.d/conda.sh
conda activate flower
flowermodel blob --filename $FILE --frame-index $PBS_ARRAYID  --out-dir {out_dir}
'''.format(num_cores=args.num_cores, walltime=args.walltime, jobname=args.jobname, moviefile=args.filename,
               last_frame_index=last_frame_index, pbslogs=args.pbslogs, out_dir=args.out_dir)

    util.__create_pbs__(args.pbs_text, args.jobname, args.pbslogs)


def get_video_blobs(args, save_output=True, monocolor_blob_threshold=0.1):
#     files = glob.glob('{:s}.blob*.csv'.format(args.filename))
    blobs = [pd.read_csv(file) for file in args.filenames]
    blobs = pd.concat(blobs).sort_values(['frame', 'color', 'x', 'y']).reset_index(drop=True)

    if args.infer_monocolor: # remove all blobs of one color if too few are present 
        blobcolors = blobs['color'].value_counts(normalize=True) > monocolor_blob_threshold
        blobcolors = blobcolors[blobcolors].index
        blobs = blobs[blobs['color'].isin(blobcolors)]        

    if save_output:
        blobs.to_csv(args.output_file, index=False)
    else:
        return blobs

def clip_video(args):
    '''
    Clip videos which have multiple panels in them into
    separete videos.
    '''
    from moviepy.editor import VideoFileClip

    clip = VideoFileClip(args.filename)
    
    if args.infer_dimensions:
        L = 1024
        nrows = clip.get_frame(0).shape[0]//L
        ncols = clip.get_frame(0).shape[1]//L
    else:
        L = clip.get_frame(0).shape[0]//args.nrows
        nrows = args.nrows
        ncols = args.ncols
    
    if (nrows==1) & (ncols==1):
        print('No need for clipping')
        clipfile = args.filename+'.clip-0-0.mov' 
        os.symlink(args.filename, clipfile) # for output in nextflow implementation
    else:       
        for i in range(nrows):
            for j in range(ncols):
                clipfile = args.filename+'.clip-{:d}-{:d}.mov'.format(i, j)
                croppedclip = clip.crop(y1=i*L, x1=j*L, width=L, height=L)       
                croppedclip.write_videofile(clipfile, codec='mpeg4')
                print('#'*30+'\n')