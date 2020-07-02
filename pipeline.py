'''

See also:

- <https://combine-lab.github.io/alevin-tutorial/2019/selective-alignment/>

'''

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
    Downloads a copy of a genome fasta file.
    '''
    
    url = PARAMS['url']['genome']
    
    log = outfile.replace('.fa.gz', '.log')
    
    statement = '''wget %(url)s -O %(outfile)s > %(log)s'''
    
    P.run(statement, to_cluster=False)


@follows(mkdir('resources'))
@originate('resources/transcriptome.fa.gz')
def download_transcriptome(outfile):
    '''
    Downloads a copy of a transcriptome fasta file.
    '''
    
    url = PARAMS['url']['transcriptome']
    
    log = outfile.replace('.fa.gz', '.log')
    
    statement = '''wget %(url)s -O %(outfile)s > %(log)s'''
    
    P.run(statement, to_cluster=False)


@merge(download_genome, 'resources/decoys.txt')
def decoys(infiles, outfile):
    '''
    Salmon indexing requires the names of the genome targets, which is extractable by using the grep command.
    '''
    
    genome = infiles[0]
    
    log = outfile.replace('.fa.gz', '.log')
    
    statement = '''grep "^>" <(gunzip -c %(genome)s) |
        cut -d " " -f 1 |
        sed -e 's/>//g' > %(outfile)s
        '''
    
    P.run(statement, to_cluster=False)


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
