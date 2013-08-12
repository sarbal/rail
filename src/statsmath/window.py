import histogram
import sys

"""
Returns the site by finding the maximum in the scores
To break ties it uses the direction.
If direction=="5", that means its a 5' end and it will return the score closest to the 5' end (aka. left)
The vice versa happens with direction=="3"

Note that this just returns offsets wrt to window frame
"""
def findSite(scores,direction):
    count = -1 if direction=="5" else 1
    i = len(scores)-1 if direction=="5" else 0
    m, ind = -1, -1
    while i>=0 and i<len(scores):
        if m < scores[i]:
            ind = i
            m = scores[i]
        i+=count
    return ind,scores[ind]


"""
Scores a set of windows based off of splice site
"""
def score(seq, site, hist,cost):
    wsize = len(site) # window size
    nwins = len(seq)-wsize+1
    wins = [0]*nwins

    for i in range(0,nwins):
        for j in range(0,len(site)):
            s = 1 if site[j]==seq[i+j] else cost
            wins[i]+=s*hist[i+j]
    return wins

"""
Note:  Site = XX (e.g. GT)

Only scores the 5' (aka left) side
"""
def slide_left(refID, sts, site, fastaF, radius):
    n,r = 2*radius, radius
    in_start = min(sts)
    hist = histogram.hist_score(sts,in_start,"5",2*n+1)
    mean,std = hist.index(max(hist))+2,histogram.stddev(hist)
    #Create a normal distributed scoring scheme based off of candidates
    norm_score = histogram.normal_score(2*n+1,mean,std)
    """Remember that fasta index is base 1 indexing"""
    seq = fastaF.fetch_sequence(refID,in_start-n,in_start+n).upper()
    cost = -3
    win_score = score(seq,site,norm_score,cost)
    rel_site,total_score = findSite(win_score,"5")
    ref_site = rel_site+in_start-n-1
    #returned transformed coordinates of junction sites
    return ref_site, norm_score, win_score, total_score

