import os

def mkdir_if_not_exist(inputdir):
    if not os.path.isdir(inputdir):
        # the following exception capture is needed, because
        # if jobs are running in parallel another process may
        # make the folder right here in the code, leading
        # to a FileExistsError
        try:
            os.makedirs(inputdir)
        except FileExistsError: 
            pass
        
    return inputdir


def __create_pbs__(pbs_text, jobname, pbslogs):
    with open('{}.pbs'.format(jobname), 'w') as f:
        f.write(pbs_text)
    
    if not os.path.exists(pbslogs):
        os.makedirs(pbslogs)
