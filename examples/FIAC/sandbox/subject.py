import fiac, fixed, sys, time, os, fpformat
import run as FIACrun

def FIACsubject(subj=3):
    ttoc = time.time()
    for run in range(1, 5):
        toc = time.time()
        vdict = {'subj':subj, 'run':run}

        fsldir = fiac.FIACpath('fsl', subj=subj, run=run, base='http://kff.stanford.edu/FIAC')

        if os.path.exists('%s/filtered_func_data.img' % fsldir):
            os.chdir(fsldir)

            FIACrun.FIACrun(subj=subj, run=run)
            tic = time.time()
            print 'time for subj=%(subj)d, run=%(run)d:' % vdict, fpformat.fix(tic-toc, 3)
        
    fixed.FIACrun(subj=subj)
    ttic = time.time()

    print 'total time for  subject %d (minutes): %02f' % ((subj), ((ttic-ttoc)/60))

if __name__ == '__main__':

    subj = int(sys.argv[1])
    FIACsubject(subj=subj)