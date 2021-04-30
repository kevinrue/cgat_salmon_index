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


@merge([download_genome, download_transcriptome], 'resources/gentrome.fa.gz')
def concatenate_genome_transcriptome(infiles, outfile):
    '''
    Along with the list of decoys salmon also needs the concatenated transcriptome and genome reference file for index.
    NOTE: the genome targets (decoys) should come after the transcriptome targets in the reference
    '''
    
    genome, transcriptome = infiles
    
    log = outfile.replace('.fa.gz', '.log')
    
    statement = '''cat %(transcriptome)s %(genome)s 2> %(log)s > %(outfile)s'''
    
    P.run(statement, to_cluster=False)


@merge([concatenate_genome_transcriptome, decoys], 'resources/salmon_index/mphf.bin')
def salmon_index(infiles, outfile):
    '''
    Along with the list of decoys salmon also needs the concatenated transcriptome and genome reference file for index.
    NOTE: the genome targets (decoys) should come after the transcriptome targets in the reference.
    
    Developer's note: mphf.bin seems to be the last large file written to disk, that is not a log file.
    '''
    
    gentrome, decoys = infiles
    
    outdir = outfile.replace('/mphf.bin', '')
    log = outdir + '.log'
    
    statement = '''salmon index -t %(gentrome)s -d %(decoys)s -p 12 -i %(outdir)s 2> %(log)s'''
    
    P.run(statement, job_threads = 12)


    
FASTQ_files = glob.glob('')

@collate(FASTQ_files, r'')
def salmon_alevin():
    '''
    '''
    
    statement = '''salmon alevin
        -l ISR
        -i {params.index}
        -1 {input.fastq1} -2 {input.fastq2}
        -o results/alevin/{wildcards.sample} -p {params.threads} --tgMap {params.tgmap}
        --chromium --dumpFeatures
        {params.cells_option}
        2> {log.stderr}
    '''
    
    P.run(statement, job_threads = 12)

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
