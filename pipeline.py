

from ruffus import *
from cgatcore import pipeline as P

import sys
import os

# load options from the config file
PARAMS = P.get_parameters(
    ["%s/pipeline.yml" % os.path.splitext(__file__)[0],
     "../pipeline.yml",
     "pipeline.yml"])



@follows(mkdir('resources'))
@originate('resources/genome.fa.gz')
def download_genome(outfile):
    '''
    '''
    
    url = PARAMS['url']['genome']
    
    log = outfile.replace('.fa.gz', '.log')
    
    statement = '''wget %(url)s -O %(outfile)s > %(log)s'''
    
    P.run(statement)


# ---------------------------------------------------
# Generic pipeline tasks
def full():
    pass


def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)
    pass


if __name__ == "__main__":
    sys.exit(main())
