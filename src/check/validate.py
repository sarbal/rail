"""
validate.py

Reads in the bed file containing the estimated splice sites and the pickle file containing the transcripts and provides the following statistics
1.  Number of exactly correct splice junctions
2.  Number of splice junctions within 1 radius (specified by user)
3.  Number of splice junctions completely off 
4.  Plot of the distribution of error
"""
import os
import site
import argparse
import sys
import math
import pickle
import bisect
from collections import Counter
from collections import defaultdict
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
site.addsitedir(os.path.join(base_path, "annotation"))
site.addsitedir(os.path.join(base_path, "struct"))
site.addsitedir(os.path.join(base_path, "fasta"))

import gtf
import search
import fasta

parser = argparse.ArgumentParser(description=\
                                     'Splice junction validator')
parser.add_argument(\
    '--xscripts-file', metavar='path', type=str, required=True,
    help='Path of the transcripts pickle file')
parser.add_argument(\
    '--bed-file', metavar='path', type=str, required=True,
    help='Path of the transcripts pickle file')
parser.add_argument(\
    '--radius', type=int, required=False,default=10,
    help='The radius of tolerance for identifying splice site neighborhoods')
parser.add_argument(\
    '--refseq', type=str, required=True,
    help='The reference sequence')

args = parser.parse_args()


"""
Given a dictionary of sites, obtains reference sequence and returns a Counter object
"""
def siteDistribution(sites,fh):
    seq_hist = Counter()
    for k,s in sites.iteritems():
        for i in range(0,len(sites[k]),2):
            st,en = s[i],s[i+1]
            refseq = fh.fetch_sequence(k,st+1,en+1).upper()
            seq_hist[refseq]+=1
    return seq_hist
"""
Finds all annotated splice sites based off of annotated transcripts
and returns a list of splice sites binned by reference sequence id
"""
def annotated_sites(xscripts):
    sites = defaultdict(list)
    for x in xscripts:
        sites[x.seqid]=sites[x.seqid]+x.getSites()
    for k,v in sites.iteritems():
        sites[k] = list(set(sites[k]))
        sites[k].sort()
    return sites

"""
Bins all splice sites in bed file and bins them by reference sequence id
"""
def readBedSites(bedfile):
    sites = defaultdict(list)
    with open(bedfile,'r') as fh:
        for ln in fh:
            line = ln.rstrip()
            toks = line.split("\t")
            seq,st = toks[0],int(toks[1])
            sites[seq].append(st)
    for k,v in sites.iteritems():
        sites[k] = list(set(sites[k]))
        sites[k].sort()        
    return sites

def union_sites(sites):
    total_sites = set()
    for k,v in sites.iteritems():
        total_sites = total_sites.union(set(v))
    return set(total_sites)

def compare(bed_sites,annot_sites,radius):
    correct = 0
    nearby  = 0
    incorrect = 0
    missed_sites = union_sites(annot_sites)
    total = len(missed_sites)/2
    for k,v in bed_sites.iteritems():
        for guess in v:
            exact = search.find(annot_sites[k],guess)
            if guess==exact:
                #print "Correct","Guess",guess,"Exact",exact
                correct+=1
                missed_sites.discard(exact)
            elif abs(guess-exact)<=radius:
                #print "Nearby","Guess",guess,"Exact",exact
                nearby+=1
                missed_sites.discard(exact)
            else:
                #print "Incorrect","Guess",guess,"Exact",exact
                incorrect+=1
    return total,correct/2,nearby/2,incorrect/2,len(missed_sites)/2 #since we looking at 2x sites

if __name__=="__main__":
    xscripts = pickle.load(open(args.xscripts_file,'rb'))
    bed_sites = readBedSites(args.bed_file)
    annot_sites = annotated_sites(xscripts)
    #print annot_sites
    total,correct,nearby,incorrect,missed = compare(bed_sites,annot_sites,args.radius)
    fastaH = fasta.fasta(args.refseq)
    bed_site_stats = siteDistribution(bed_sites,fastaH)
    annot_site_stats = siteDistribution(annot_sites,fastaH)
    
    print "Total annot sites   \t",total
    print "Correct             \t",correct
    print "Nearby              \t",nearby
    print "Incorrect           \t",incorrect
    print "Missed              \t",missed
    print "Bed site stats      \t",bed_site_stats
    print "Annotated site stats\t",annot_site_stats

    
