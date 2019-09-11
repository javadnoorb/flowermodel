import os
from flowermodel import util
from flowermodel.find_blobs import get_allframes_blobs
import imageio

def get_frame_blobs(args):
    outputdir = os.path.join(args.out_dir, os.path.basename(args.filename))
    util.mkdir_if_not_exist(outputdir)

    blobs = get_allframes_blobs(args.filename, min_idx=args.frame_index, max_idx=args.frame_index+1)
    blobs.to_csv(os.path.join(outputdir, 'blob{:d}.csv'.format(args.frame_index)), index=False)
    
    
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
flowermodel blob --filename $FILE --blob-index $PBS_ARRAYID
'''.format(num_cores=args.num_cores, walltime=args.walltime, jobname=args.jobname, moviefile=args.filename,
               last_frame_index=last_frame_index, pbslogs=args.pbslogs)

    with open('{}.pbs'.format(args.jobname), 'w') as f:
        f.write(pbs_text)
    
    if not os.path.exists(args.pbslogs):
        os.makedirs(args.pbslogs)
        
        
def clip_video(args):
    '''
    Clip videos which have multiple panels in them into
    separete videos.
    '''
    from moviepy.editor import VideoFileClip

    clip = VideoFileClip(args.filename)

    L = clip.get_frame(0).shape[0]//args.nrows

    clipspath = args.filename+'.clips'
    util.mkdir_if_not_exist(clipspath)

    for i in range(args.nrows):
        for j in range(args.ncols):
            clipname = 'clip-{:d}-{:d}.mp4'.format(i, j)
#             print('Analyzing ', clipname)        
            clipfile = os.path.join(clipspath, clipname)

            croppedclip = clip.crop(y1=i*L, x1=j*L, width=L, height=L)       
            croppedclip.write_videofile(clipfile)
            print('#'*30+'\n')