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